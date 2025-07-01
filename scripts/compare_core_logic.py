#!/usr/bin/env python3
"""
Intelligent comparison of core business logic between MCP and Staffer.
Focuses only on actual function implementation, ignoring signature and schema changes.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoreLogicComparison:
    file_name: str
    function_name: str
    core_logic_identical: bool
    logic_differences: List[str]
    expected_differences: List[str]


class CoreLogicComparator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.mcp_dir = self.project_root / "function_bank" / "mcp_server"
        self.staffer_dir = self.project_root / "staffer" / "functions" / "analytics"
    
    def extract_function_implementation(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """Extract just the core implementation logic, excluding signature and schemas."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    not node.name.startswith('_')):
                    
                    lines = content.split('\n')
                    
                    # Find function body start (after docstring)
                    func_start = node.lineno - 1
                    body_start = func_start + 1
                    
                    # Skip function definition line
                    while body_start < len(lines) and (
                        lines[body_start].strip() == '' or
                        lines[body_start].strip().startswith('"""') or
                        lines[body_start].strip().startswith("'''") or
                        '"""' in lines[body_start] or
                        "'''" in lines[body_start]
                    ):
                        body_start += 1
                    
                    # Find function body end
                    body_end = body_start
                    current_indent = None
                    
                    for i in range(body_start, len(lines)):
                        line = lines[i]
                        
                        # Stop at schema definitions
                        if line.strip().startswith('# Gemini function schema') or line.strip().startswith('schema_'):
                            break
                            
                        # Stop at MCP reference
                        if '"""' in line and 'MCP Implementation Reference' in line:
                            break
                            
                        # Stop at next function or end of indentation
                        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                            if not line.startswith('#'):
                                break
                        
                        body_end = i + 1
                    
                    # Extract core implementation
                    impl_lines = lines[body_start:body_end]
                    implementation = '\n'.join(impl_lines)
                    
                    return node.name, implementation
            
            return None, None
        except Exception as e:
            print(f"Error extracting implementation from {file_path}: {e}")
            return None, None
    
    def normalize_implementation(self, impl: str, is_mcp: bool = False) -> str:
        """Normalize implementation for comparison, handling expected differences."""
        lines = impl.split('\n')
        normalized = []
        
        for line in lines:
            # Skip empty lines and pure comments
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            normalized_line = line
            
            # Handle working_directory parameter additions
            if not is_mcp:
                # Remove working_directory from function calls for comparison
                normalized_line = re.sub(r'(\w+)\(\s*working_directory,\s*', r'\1(', normalized_line)
                normalized_line = re.sub(r'(\w+)\(\s*working_directory\s*\)', r'\1()', normalized_line)
            
            # Handle async/await differences
            if is_mcp:
                # Remove await keywords for comparison
                normalized_line = re.sub(r'\bawait\s+', '', normalized_line)
            
            # Handle import differences
            if 'asyncio' in line and 'subprocess' in line:
                continue  # Skip different import patterns
            
            # Handle async subprocess vs sync subprocess
            if 'asyncio.create_subprocess_shell' in line:
                normalized_line = normalized_line.replace('asyncio.create_subprocess_shell', 'subprocess.run')
            if 'process.communicate()' in line:
                normalized_line = normalized_line.replace('await process.communicate()', 'process.communicate()')
            
            normalized.append(normalized_line.rstrip())
        
        return '\n'.join(normalized)
    
    def compare_implementations(self, mcp_impl: str, staffer_impl: str, func_name: str) -> CoreLogicComparison:
        """Compare core business logic implementations."""
        # Normalize both implementations
        mcp_normalized = self.normalize_implementation(mcp_impl, is_mcp=True)
        staffer_normalized = self.normalize_implementation(staffer_impl, is_mcp=False)
        
        # Split into lines for comparison
        mcp_lines = [line.strip() for line in mcp_normalized.split('\n') if line.strip()]
        staffer_lines = [line.strip() for line in staffer_normalized.split('\n') if line.strip()]
        
        # Find actual logic differences
        logic_differences = []
        expected_differences = []
        
        # Simple line-by-line comparison
        max_lines = max(len(mcp_lines), len(staffer_lines))
        
        for i in range(max_lines):
            mcp_line = mcp_lines[i] if i < len(mcp_lines) else ""
            staffer_line = staffer_lines[i] if i < len(staffer_lines) else ""
            
            if mcp_line != staffer_line:
                # Check if this is an expected difference
                if self.is_expected_difference(mcp_line, staffer_line):
                    expected_differences.append(f"Expected: MCP='{mcp_line}' vs Staffer='{staffer_line}'")
                else:
                    logic_differences.append(f"Logic diff line {i+1}: MCP='{mcp_line}' vs Staffer='{staffer_line}'")
        
        return CoreLogicComparison(
            file_name="",  # Will be set by caller
            function_name=func_name,
            core_logic_identical=len(logic_differences) == 0,
            logic_differences=logic_differences,
            expected_differences=expected_differences
        )
    
    def is_expected_difference(self, mcp_line: str, staffer_line: str) -> bool:
        """Check if difference is expected per SOP v3.1."""
        expected_patterns = [
            # Working directory parameter differences
            (r'working_directory', True),
            # Import differences  
            (r'from google\.genai import types', True),
            # Async/subprocess differences
            (r'import asyncio', r'import subprocess'),
            (r'asyncio\.', r'subprocess\.'),
            # Path handling differences (expected in find_datasources)
            (r'Path\(directory_path\)', r'Path\(\) / directory_path'),
            (r'current_dir = Path\(directory_path\)\.resolve\(\)', r'if not os\.path\.isabs\(directory_path\)'),
        ]
        
        for pattern in expected_patterns:
            if isinstance(pattern, tuple) and len(pattern) == 2:
                if isinstance(pattern[1], str):
                    # Pattern replacement check
                    if re.search(pattern[0], mcp_line) and re.search(pattern[1], staffer_line):
                        return True
                elif pattern[1] is True:
                    # Simple pattern presence
                    if re.search(pattern[0], staffer_line):
                        return True
        
        return False
    
    def compare_file_pair(self, mcp_file: Path, staffer_file: Path) -> CoreLogicComparison:
        """Compare core logic between MCP and Staffer file pair."""
        mcp_func_name, mcp_impl = self.extract_function_implementation(mcp_file)
        staffer_func_name, staffer_impl = self.extract_function_implementation(staffer_file)
        
        if not mcp_impl or not staffer_impl:
            return CoreLogicComparison(
                file_name=mcp_file.name,
                function_name=mcp_func_name or staffer_func_name or "unknown",
                core_logic_identical=False,
                logic_differences=["Could not extract implementations"],
                expected_differences=[]
            )
        
        result = self.compare_implementations(mcp_impl, staffer_impl, staffer_func_name)
        result.file_name = mcp_file.name
        return result
    
    def find_file_pairs(self) -> List[Tuple[Path, Path]]:
        """Find all MCP → Staffer file pairs to compare."""
        pairs = []
        
        # Tools
        mcp_tools = self.mcp_dir / "tools"
        staffer_tools = self.staffer_dir / "tools"
        
        for mcp_file in mcp_tools.glob("*.py"):
            if mcp_file.name not in ["__init__.py", "pandas_tools.py"]:
                staffer_file = staffer_tools / mcp_file.name
                if staffer_file.exists():
                    pairs.append((mcp_file, staffer_file))
        
        # Resources (single-function files only)
        mcp_resources = self.mcp_dir / "resources"
        staffer_resources = self.staffer_dir / "resources"
        
        for mcp_file in mcp_resources.glob("*.py"):
            if mcp_file.name not in ["__init__.py", "data_resources.py"]:
                staffer_file = staffer_resources / mcp_file.name
                if staffer_file.exists():
                    pairs.append((mcp_file, staffer_file))
        
        # Prompts
        mcp_prompts = self.mcp_dir / "prompts"
        staffer_prompts = self.staffer_dir / "prompts"
        
        for mcp_file in mcp_prompts.glob("*.py"):
            if mcp_file.name != "__init__.py":
                staffer_file = staffer_prompts / mcp_file.name
                if staffer_file.exists():
                    pairs.append((mcp_file, staffer_file))
        
        return pairs
    
    def run_comparison(self) -> Dict[str, any]:
        """Run intelligent core logic comparison."""
        print("🧠 Intelligent Core Logic Comparison: MCP vs Staffer")
        print("=" * 60)
        print("Focus: Business logic preservation (ignoring signature/schema changes)")
        print()
        
        file_pairs = self.find_file_pairs()
        results = []
        identical_count = 0
        
        for mcp_file, staffer_file in file_pairs:
            result = self.compare_file_pair(mcp_file, staffer_file)
            results.append(result)
            
            if result.core_logic_identical:
                identical_count += 1
                print(f"✅ {result.function_name} ({result.file_name})")
                if result.expected_differences:
                    print(f"   📝 {len(result.expected_differences)} expected signature changes")
            else:
                print(f"❌ {result.function_name} ({result.file_name}) - Core logic differences:")
                for diff in result.logic_differences[:2]:
                    print(f"   • {diff}")
                if len(result.logic_differences) > 2:
                    print(f"   • ... and {len(result.logic_differences) - 2} more")
        
        print("=" * 60)
        logic_preservation_rate = identical_count / len(results) * 100
        
        print(f"📊 Core Logic Analysis:")
        print(f"   ✅ Logic preserved: {identical_count}/{len(results)}")
        print(f"   ❌ Logic changed: {len(results) - identical_count}/{len(results)}")
        print(f"   🎯 Logic Preservation: {logic_preservation_rate:.1f}%")
        
        if logic_preservation_rate == 100:
            print("\n🎉 Perfect! All core business logic preserved!")
            print("✨ SOP v3.1 'Minimal Transformation' successfully followed!")
        elif logic_preservation_rate >= 95:
            print("\n✅ Excellent! Core business logic almost perfectly preserved!")
            print("📝 Minor differences may be expected transformations")
        else:
            print("\n⚠️  Warning: Significant core logic changes detected!")
            print("🔍 Review differences to ensure they're intentional")
        
        return {
            "total": len(results),
            "logic_preserved": identical_count,
            "logic_changed": len(results) - identical_count,
            "preservation_rate": logic_preservation_rate,
            "results": results
        }


def main():
    project_root = "/Users/spaceship/project/analytic-agent-cli"
    comparator = CoreLogicComparator(project_root)
    results = comparator.run_comparison()
    
    # Success if > 95% logic preservation
    if results["preservation_rate"] < 95:
        exit(1)


if __name__ == "__main__":
    main()