#!/usr/bin/env python3
"""
Mechanical verification script for MCP-to-Staffer transformations.
Checks if all transformations follow SOP v3.1 rules correctly.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FunctionSignature:
    name: str
    params: List[str]
    has_async: bool
    has_working_directory: bool
    working_directory_first: bool


@dataclass
class TransformationCheck:
    file_path: str
    function_name: str
    passed: bool
    issues: List[str]


class MCPTransformationVerifier:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.mcp_dir = self.project_root / "function_bank" / "mcp_server"
        self.staffer_dir = self.project_root / "staffer" / "functions" / "analytics"
        
    def extract_function_signature(self, file_path: Path) -> Optional[FunctionSignature]:
        """Extract function signature from Python file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find the main function (not __init__ or helper functions)
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    not node.name.startswith('_')):
                    params = [arg.arg for arg in node.args.args]
                    return FunctionSignature(
                        name=node.name,
                        params=params,
                        has_async=isinstance(node, ast.AsyncFunctionDef),
                        has_working_directory='working_directory' in params,
                        working_directory_first=params[0] == 'working_directory' if params else False
                    )
            return None
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def check_imports(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check if file has required imports."""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for google.genai import
            if 'from google.genai import types' not in content:
                issues.append("Missing 'from google.genai import types' import")
            
            return len(issues) == 0, issues
        except Exception as e:
            return False, [f"Error reading file: {e}"]

    def check_schema_exists(self, file_path: Path, function_name: str) -> Tuple[bool, List[str]]:
        """Check if Gemini schema exists and is properly formatted."""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            schema_name = f"schema_{function_name}"
            
            # Check if schema exists
            if schema_name not in content:
                issues.append(f"Missing schema '{schema_name}'")
                return False, issues
            
            # Check if schema uses types.FunctionDeclaration
            if f"{schema_name} = types.FunctionDeclaration" not in content:
                issues.append(f"Schema '{schema_name}' doesn't use types.FunctionDeclaration")
            
            # Check if working_directory is excluded from schema
            schema_match = re.search(rf'{schema_name} = types\.FunctionDeclaration\((.*?)\)', content, re.DOTALL)
            if schema_match and 'working_directory' in schema_match.group(1):
                issues.append(f"Schema '{schema_name}' incorrectly includes working_directory parameter")
            
            return len(issues) == 0, issues
        except Exception as e:
            return False, [f"Error checking schema: {e}"]

    def check_mcp_reference(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check if MCP reference section exists."""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if 'MCP Implementation Reference:' not in content:
                issues.append("Missing MCP Implementation Reference section")
            
            return len(issues) == 0, issues
        except Exception as e:
            return False, [f"Error checking MCP reference: {e}"]

    def verify_signature_transformation(self, mcp_sig: FunctionSignature, staffer_sig: FunctionSignature) -> Tuple[bool, List[str]]:
        """Verify signature transformation follows SOP v3.1 rules."""
        issues = []
        
        # Check async removal
        if staffer_sig.has_async:
            issues.append("Staffer function should not be async")
        
        # Check working_directory addition
        if not staffer_sig.has_working_directory:
            issues.append("Staffer function missing working_directory parameter")
        elif not staffer_sig.working_directory_first:
            issues.append("working_directory should be first parameter")
        
        # Check parameter preservation (excluding working_directory)
        mcp_params = mcp_sig.params
        staffer_params = staffer_sig.params[1:] if staffer_sig.working_directory_first else staffer_sig.params
        
        if mcp_params != staffer_params:
            issues.append(f"Parameters changed: MCP {mcp_params} → Staffer {staffer_params}")
        
        return len(issues) == 0, issues

    def verify_file_pair(self, mcp_file: Path, staffer_file: Path) -> TransformationCheck:
        """Verify a single MCP → Staffer file transformation."""
        issues = []
        
        # Extract signatures
        mcp_sig = self.extract_function_signature(mcp_file)
        staffer_sig = self.extract_function_signature(staffer_file)
        
        if not mcp_sig:
            issues.append(f"Cannot extract MCP signature from {mcp_file}")
        if not staffer_sig:
            issues.append(f"Cannot extract Staffer signature from {staffer_file}")
        
        if mcp_sig and staffer_sig:
            # Verify signature transformation
            sig_ok, sig_issues = self.verify_signature_transformation(mcp_sig, staffer_sig)
            issues.extend(sig_issues)
            
            # Check imports
            imports_ok, import_issues = self.check_imports(staffer_file)
            issues.extend(import_issues)
            
            # Check schema
            schema_ok, schema_issues = self.check_schema_exists(staffer_file, staffer_sig.name)
            issues.extend(schema_issues)
            
            # Check MCP reference
            ref_ok, ref_issues = self.check_mcp_reference(staffer_file)
            issues.extend(ref_issues)
        
        return TransformationCheck(
            file_path=str(staffer_file),
            function_name=staffer_sig.name if staffer_sig else "unknown",
            passed=len(issues) == 0,
            issues=issues
        )

    def find_file_pairs(self) -> List[Tuple[Path, Path]]:
        """Find all MCP → Staffer file pairs to verify."""
        pairs = []
        
        # Tools
        mcp_tools = self.mcp_dir / "tools"
        staffer_tools = self.staffer_dir / "tools"
        
        for mcp_file in mcp_tools.glob("*.py"):
            if mcp_file.name != "__init__.py":
                staffer_file = staffer_tools / mcp_file.name
                if staffer_file.exists():
                    pairs.append((mcp_file, staffer_file))
        
        # Resources
        mcp_resources = self.mcp_dir / "resources"
        staffer_resources = self.staffer_dir / "resources"
        
        for mcp_file in mcp_resources.glob("*.py"):
            if mcp_file.name != "__init__.py":
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

    def run_verification(self) -> Dict[str, any]:
        """Run complete verification of all transformations."""
        print("🔍 Running MCP-to-Staffer Transformation Verification...")
        print("=" * 60)
        
        file_pairs = self.find_file_pairs()
        results = []
        passed_count = 0
        
        for mcp_file, staffer_file in file_pairs:
            result = self.verify_file_pair(mcp_file, staffer_file)
            results.append(result)
            
            if result.passed:
                passed_count += 1
                print(f"✅ {result.function_name} ({staffer_file.name})")
            else:
                print(f"❌ {result.function_name} ({staffer_file.name})")
                for issue in result.issues:
                    print(f"   • {issue}")
        
        print("=" * 60)
        print(f"📊 Results: {passed_count}/{len(results)} transformations passed")
        
        if passed_count == len(results):
            print("🎉 All transformations follow SOP v3.1 correctly!")
        else:
            print(f"⚠️  {len(results) - passed_count} transformations need fixes")
        
        return {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "results": results
        }


def main():
    project_root = "/Users/spaceship/project/analytic-agent-cli"
    verifier = MCPTransformationVerifier(project_root)
    results = verifier.run_verification()
    
    # Exit with error code if any checks failed
    if results["failed"] > 0:
        exit(1)


if __name__ == "__main__":
    main()