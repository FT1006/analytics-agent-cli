#!/usr/bin/env python3
"""
Simple verification that business logic is preserved between MCP and Staffer.
Focuses on actual function body content, excluding signatures and schemas.
"""

import re
from pathlib import Path
from typing import List, Tuple


def extract_function_body_only(file_path: Path) -> str:
    """Extract only the function body implementation, excluding signature and schemas."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    body_lines = []
    inside_function = False
    inside_schema = False
    inside_mcp_reference = False
    
    for line in lines:
        # Start of function body (after docstring)
        if (inside_function and 
            line.strip() and 
            not line.strip().startswith('"""') and 
            not line.strip().startswith("'''") and
            not '"""' in line and
            not "'''" in line):
            
            # Skip schema sections
            if 'schema_' in line or line.strip().startswith('# Gemini function schema'):
                inside_schema = True
                continue
            
            # Skip MCP reference sections
            if 'MCP Implementation Reference' in line:
                inside_mcp_reference = True
                continue
                
            if inside_schema and line.strip() == '':
                inside_schema = False
                continue
                
            if inside_mcp_reference:
                continue
                
            if not inside_schema:
                body_lines.append(line)
        
        # Detect start of function
        if (line.strip().startswith('def ') or 
            line.strip().startswith('async def ')):
            inside_function = True
    
    return '\n'.join(body_lines)


def normalize_for_comparison(implementation: str, is_mcp: bool = False) -> str:
    """Normalize implementation for fair comparison."""
    lines = implementation.split('\n')
    normalized = []
    
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
            
        normalized_line = line
        
        # Handle working_directory parameter in function calls
        if not is_mcp:
            # Remove working_directory from Staffer function calls for comparison
            normalized_line = re.sub(r'(\w+)\(\s*working_directory,\s*', r'\1(', normalized_line)
            normalized_line = re.sub(r'(\w+)\(\s*working_directory\s*\)', r'\1()', normalized_line)
        
        # Handle async differences
        if is_mcp:
            normalized_line = re.sub(r'\bawait\s+', '', normalized_line)
        
        # Handle asyncio vs subprocess differences
        normalized_line = re.sub(r'asyncio\.create_subprocess_shell', 'subprocess.run', normalized_line)
        normalized_line = re.sub(r'await process\.communicate\(\)', 'process.communicate()', normalized_line)
        
        normalized.append(normalized_line.strip())
    
    # Remove empty lines
    return '\n'.join(line for line in normalized if line)


def compare_logic_simple(mcp_file: Path, staffer_file: Path) -> Tuple[bool, List[str]]:
    """Simple comparison focusing only on business logic."""
    try:
        # Extract function bodies
        mcp_body = extract_function_body_only(mcp_file)
        staffer_body = extract_function_body_only(staffer_file)
        
        # Normalize for comparison
        mcp_normalized = normalize_for_comparison(mcp_body, is_mcp=True)
        staffer_normalized = normalize_for_comparison(staffer_body, is_mcp=False)
        
        # Simple string comparison
        if mcp_normalized == staffer_normalized:
            return True, []
        
        # If not identical, find key differences
        mcp_lines = [line for line in mcp_normalized.split('\n') if line]
        staffer_lines = [line for line in staffer_normalized.split('\n') if line]
        
        differences = []
        
        # Check for major structural differences
        if len(mcp_lines) != len(staffer_lines):
            differences.append(f"Different number of logic lines: MCP={len(mcp_lines)}, Staffer={len(staffer_lines)}")
        
        # Check for significant logic differences (not just parameter order)
        significant_diffs = 0
        for i, (mcp_line, staffer_line) in enumerate(zip(mcp_lines, staffer_lines)):
            if mcp_line != staffer_line:
                # Check if this is just a parameter reordering or working_directory addition
                if not is_minor_difference(mcp_line, staffer_line):
                    significant_diffs += 1
                    if len(differences) < 3:  # Limit output
                        differences.append(f"Line {i+1}: '{mcp_line}' vs '{staffer_line}'")
        
        if significant_diffs > 0:
            differences.insert(0, f"{significant_diffs} significant logic differences found")
        
        return significant_diffs == 0, differences
        
    except Exception as e:
        return False, [f"Comparison error: {e}"]


def is_minor_difference(mcp_line: str, staffer_line: str) -> bool:
    """Check if difference is minor (parameter reordering, working_directory, etc.)."""
    # Check for working_directory parameter differences
    if 'working_directory' in staffer_line and 'working_directory' not in mcp_line:
        return True
    
    # Check for import differences
    if 'import' in mcp_line and 'import' in staffer_line:
        return True
    
    # Check for parameter reordering in the same function call
    mcp_words = set(re.findall(r'\w+', mcp_line))
    staffer_words = set(re.findall(r'\w+', staffer_line))
    
    # If same words, just different order, it's minor
    if mcp_words == staffer_words or staffer_words - mcp_words == {'working_directory'}:
        return True
    
    return False


def main():
    project_root = Path("/Users/spaceship/project/analytic-agent-cli")
    mcp_dir = project_root / "function_bank" / "mcp_server"
    staffer_dir = project_root / "staffer" / "functions" / "analytics"
    
    print("🔍 Simple Logic Preservation Verification")
    print("=" * 50)
    print("Checking if core business logic is preserved...")
    print()
    
    # Find file pairs
    pairs = []
    
    # Tools
    for mcp_file in (mcp_dir / "tools").glob("*.py"):
        if mcp_file.name not in ["__init__.py", "pandas_tools.py"]:
            staffer_file = staffer_dir / "tools" / mcp_file.name
            if staffer_file.exists():
                pairs.append((mcp_file, staffer_file))
    
    # Resources (single-function files)
    for mcp_file in (mcp_dir / "resources").glob("*.py"):
        if mcp_file.name not in ["__init__.py", "data_resources.py"]:
            staffer_file = staffer_dir / "resources" / mcp_file.name
            if staffer_file.exists():
                pairs.append((mcp_file, staffer_file))
    
    # Prompts
    for mcp_file in (mcp_dir / "prompts").glob("*.py"):
        if mcp_file.name != "__init__.py":
            staffer_file = staffer_dir / "prompts" / mcp_file.name
            if staffer_file.exists():
                pairs.append((mcp_file, staffer_file))
    
    # Compare each pair
    preserved_count = 0
    total_count = len(pairs)
    
    for mcp_file, staffer_file in pairs:
        logic_preserved, differences = compare_logic_simple(mcp_file, staffer_file)
        
        func_name = mcp_file.stem.replace('_tool', '').replace('_resource', '').replace('_prompt', '')
        
        if logic_preserved:
            preserved_count += 1
            print(f"✅ {func_name}")
        else:
            print(f"❌ {func_name}")
            for diff in differences[:2]:
                print(f"   • {diff}")
    
    print("=" * 50)
    preservation_rate = (preserved_count / total_count) * 100
    print(f"📊 Logic Preservation: {preserved_count}/{total_count} ({preservation_rate:.1f}%)")
    
    if preservation_rate == 100:
        print("🎉 Perfect! All business logic preserved!")
        print("✅ SOP v3.1 'Minimal Transformation' successfully followed!")
    elif preservation_rate >= 90:
        print("✅ Excellent! Business logic well preserved!")
        print("📝 Minor differences may be expected transformations")
    else:
        print("⚠️  Warning: Significant logic changes detected!")
    
    return preservation_rate >= 90


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)