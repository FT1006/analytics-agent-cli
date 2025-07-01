#!/usr/bin/env python3
"""
Compare business logic between MCP and Staffer implementations.
Verifies that only signature changes were made, core logic is preserved.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LogicComparison:
    file_name: str
    function_name: str
    logic_identical: bool
    differences: List[str]
    signature_only_changes: bool


class BusinessLogicComparator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.mcp_dir = self.project_root / "function_bank" / "mcp_server"
        self.staffer_dir = self.project_root / "staffer" / "functions" / "analytics"
    
    def normalize_function_body(self, func_body: str, is_mcp: bool = False) -> str:
        """Normalize function body for comparison by removing signature differences."""
        lines = func_body.strip().split('\n')
        normalized_lines = []
        
        for line in lines:
            # Skip function definition line
            if (line.strip().startswith('def ') or 
                line.strip().startswith('async def ')):
                continue
            
            # Skip docstring lines (first non-empty line after function def)
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                continue
                
            # Normalize function calls that might have working_directory added
            if is_mcp:
                # For MCP, we expect calls without working_directory
                normalized_line = line
            else:
                # For Staffer, normalize calls that should have working_directory added
                # Remove working_directory parameter from function calls for comparison
                normalized_line = re.sub(r'(\w+)\(working_directory,\s*', r'\1(', line)
                normalized_line = re.sub(r'(\w+)\(\s*working_directory\s*\)', r'\1()', normalized_line)
            
            # Normalize await calls (MCP has await, Staffer doesn't)
            if is_mcp:
                normalized_line = re.sub(r'await\s+', '', normalized_line)
            
            # Normalize import statements
            if 'from google.genai import types' in line:
                continue  # Skip Staffer-specific import
                
            normalized_lines.append(normalized_line)
        
        return '\n'.join(normalized_lines)
    
    def extract_function_body(self, file_path: Path) -> Optional[str]:
        """Extract the main function body from a Python file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find function definition and extract body
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    not node.name.startswith('_')):
                    
                    # Get the source lines for this function
                    lines = content.split('\n')
                    start_line = node.lineno - 1
                    
                    # Find the end of the function
                    end_line = start_line + 1
                    while end_line < len(lines):
                        line = lines[end_line]
                        # Stop at next function or class definition, or end of file
                        if (line.strip() and 
                            not line.startswith(' ') and 
                            not line.startswith('\t') and
                            not line.startswith('#') and
                            line.strip() != ''):
                            break
                        end_line += 1
                    
                    # Extract function body
                    func_lines = lines[start_line:end_line]
                    return '\n'.join(func_lines)
            
            return None
        except Exception as e:
            print(f"Error extracting function body from {file_path}: {e}")
            return None
    
    def compare_file_pair(self, mcp_file: Path, staffer_file: Path) -> LogicComparison:
        """Compare business logic between MCP and Staffer versions of a file."""
        mcp_body = self.extract_function_body(mcp_file)
        staffer_body = self.extract_function_body(staffer_file)
        
        if not mcp_body or not staffer_body:
            return LogicComparison(
                file_name=mcp_file.name,
                function_name="unknown",
                logic_identical=False,
                differences=["Could not extract function bodies"],
                signature_only_changes=False
            )
        
        # Extract function names
        mcp_func_name = self.extract_function_name(mcp_body)
        staffer_func_name = self.extract_function_name(staffer_body)
        
        # Normalize both function bodies
        mcp_normalized = self.normalize_function_body(mcp_body, is_mcp=True)
        staffer_normalized = self.normalize_function_body(staffer_body, is_mcp=False)
        
        # Compare normalized bodies
        differences = []
        logic_identical = True
        
        mcp_lines = mcp_normalized.split('\n')
        staffer_lines = staffer_normalized.split('\n')
        
        # Simple line-by-line comparison
        max_lines = max(len(mcp_lines), len(staffer_lines))
        
        for i in range(max_lines):
            mcp_line = mcp_lines[i].strip() if i < len(mcp_lines) else ""
            staffer_line = staffer_lines[i].strip() if i < len(staffer_lines) else ""
            
            # Skip empty lines and comments
            if not mcp_line and not staffer_line:
                continue
            if mcp_line.startswith('#') and staffer_line.startswith('#'):
                continue
                
            if mcp_line != staffer_line:
                logic_identical = False
                differences.append(f"Line {i+1}: MCP='{mcp_line}' vs Staffer='{staffer_line}'")
        
        # Check if differences are only signature-related
        signature_only_changes = self.are_differences_signature_only(differences)
        
        return LogicComparison(
            file_name=mcp_file.name,
            function_name=staffer_func_name or mcp_func_name or "unknown",
            logic_identical=logic_identical,
            differences=differences,
            signature_only_changes=signature_only_changes
        )
    
    def extract_function_name(self, func_body: str) -> Optional[str]:
        """Extract function name from function body."""
        lines = func_body.split('\n')
        for line in lines:
            if line.strip().startswith(('def ', 'async def ')):
                match = re.search(r'def\s+(\w+)', line)
                if match:
                    return match.group(1)
        return None
    
    def are_differences_signature_only(self, differences: List[str]) -> bool:
        """Check if differences are only related to function signatures."""
        signature_patterns = [
            r'async def.*vs.*def',  # async removal
            r'working_directory',   # working_directory parameter
            r'await\s+',           # await removal
            r'from google\.genai import types'  # import addition
        ]
        
        for diff in differences:
            is_signature_diff = any(re.search(pattern, diff) for pattern in signature_patterns)
            if not is_signature_diff:
                return False
        
        return True
    
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
        
        # Resources (except data_resources.py which has multiple functions)
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
        """Run complete business logic comparison."""
        print("🔍 Comparing Business Logic: MCP vs Staffer")
        print("=" * 60)
        
        file_pairs = self.find_file_pairs()
        results = []
        identical_count = 0
        signature_only_count = 0
        
        for mcp_file, staffer_file in file_pairs:
            result = self.compare_file_pair(mcp_file, staffer_file)
            results.append(result)
            
            if result.logic_identical:
                identical_count += 1
                print(f"✅ {result.function_name} ({result.file_name}) - Logic identical")
            elif result.signature_only_changes:
                signature_only_count += 1
                print(f"🔄 {result.function_name} ({result.file_name}) - Only signature changes")
            else:
                print(f"❌ {result.function_name} ({result.file_name}) - Logic differences found")
                for diff in result.differences[:3]:  # Show first 3 differences
                    print(f"   • {diff}")
                if len(result.differences) > 3:
                    print(f"   • ... and {len(result.differences) - 3} more")
        
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   ✅ Identical logic: {identical_count}")
        print(f"   🔄 Signature-only changes: {signature_only_count}")
        print(f"   ❌ Logic differences: {len(results) - identical_count - signature_only_count}")
        print(f"   📝 Total compared: {len(results)}")
        
        success_rate = (identical_count + signature_only_count) / len(results) * 100
        print(f"   🎯 SOP v3.1 Compliance: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 Perfect! All transformations preserve business logic!")
        elif success_rate >= 90:
            print("\n✨ Excellent! Transformations follow SOP v3.1 correctly!")
        else:
            print("\n⚠️  Some transformations may have unintended logic changes!")
        
        return {
            "total": len(results),
            "identical": identical_count,
            "signature_only": signature_only_count,
            "logic_differences": len(results) - identical_count - signature_only_count,
            "success_rate": success_rate,
            "results": results
        }


def main():
    project_root = "/Users/spaceship/project/analytic-agent-cli"
    comparator = BusinessLogicComparator(project_root)
    results = comparator.run_comparison()
    
    # Exit with error code if significant logic differences found
    if results["logic_differences"] > 0:
        exit(1)


if __name__ == "__main__":
    main()