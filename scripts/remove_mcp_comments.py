#!/usr/bin/env python3
"""Remove MCP implementation reference comments from all analytics functions."""

import os
import re
from pathlib import Path


def remove_mcp_comments(file_path):
    """Remove MCP implementation reference section from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Patterns to match MCP reference sections
    patterns = [
        # Triple quoted MCP reference blocks (double quotes)
        r'"""[\s\n]*MCP Implementation Reference:[\s\S]*?"""',
        # Triple quoted MCP reference blocks (single quotes)
        r"'''[\s\n]*MCP Implementation Reference:[\s\S]*?'''",
        # Single line MCP reference comments
        r'#\s*MCP Implementation Reference:.*$',
        # Multi-line single comments starting with MCP reference
        r'#\s*MCP Implementation Reference:.*(?:\n#.*)*'
    ]
    
    # Remove all MCP reference patterns
    cleaned_content = content
    for pattern in patterns:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.MULTILINE)
    
    # Remove any trailing empty lines
    lines = cleaned_content.split('\n')
    while lines and not lines[-1].strip():
        lines.pop()
    
    cleaned_content = '\n'.join(lines)
    
    # Only write back if content changed
    if cleaned_content != content:
        with open(file_path, 'w') as f:
            f.write(cleaned_content)
        return True
    return False


def process_directory(directory):
    """Process all Python files in a directory and its subdirectories."""
    processed_count = 0
    modified_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ directories
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(root, file)
                processed_count += 1
                
                if remove_mcp_comments(file_path):
                    modified_count += 1
                    print(f"✓ Cleaned: {file_path}")
    
    return processed_count, modified_count


def main():
    """Main function to clean all analytics functions."""
    project_root = Path("/Users/spaceship/project/analytic-agent-cli")
    
    print("🧹 Removing MCP Implementation Reference comments...")
    print("=" * 60)
    
    # Process analytics directories
    directories = [
        project_root / "staffer" / "functions" / "analytics" / "tools",
        project_root / "staffer" / "functions" / "analytics" / "resources",
        project_root / "staffer" / "functions" / "analytics" / "prompts",
    ]
    
    total_processed = 0
    total_modified = 0
    
    for directory in directories:
        if directory.exists():
            print(f"\n📁 Processing {directory.relative_to(project_root)}...")
            processed, modified = process_directory(directory)
            total_processed += processed
            total_modified += modified
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   Files processed: {total_processed}")
    print(f"   Files modified: {total_modified}")
    print(f"   Files unchanged: {total_processed - total_modified}")
    print("=" * 60)
    
    if total_modified > 0:
        print("✅ Successfully removed MCP comments from all modified files!")
    else:
        print("ℹ️  No MCP comments found to remove.")


if __name__ == "__main__":
    main()