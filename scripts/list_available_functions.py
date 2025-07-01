#!/usr/bin/env python3
"""List all available functions organized by category."""

from staffer.available_functions import available_functions, all_functions

def print_function_summary():
    """Print a summary of all available functions by category."""
    
    # Categorize functions
    file_ops = []
    excel = []
    analytics_tools = []
    analytics_resources = []
    analytics_prompts = []
    
    for func_name in sorted(all_functions.keys()):
        # File operations
        if any(word in func_name for word in ['file', 'working_directory', 'python']):
            file_ops.append(func_name)
        # Excel operations
        elif any(word in func_name for word in ['excel', 'workbook', 'worksheet', 'cell', 'merge', 'unmerge', 
                                                 'range', 'formula', 'table', 'chart', 'pivot']):
            excel.append(func_name)
        # Analytics tools
        elif any(word in func_name for word in ['analyze', 'calculate', 'compare', 'detect', 'execute', 
                                                 'export', 'find', 'generate', 'load_dataset', 'list_loaded',
                                                 'memory_optimization', 'merge_datasets', 'segment', 'suggest',
                                                 'time_series', 'validate']):
            analytics_tools.append(func_name)
        # Analytics prompts
        elif any(word in func_name for word in ['investigation', 'consultation', 'assessment', 'workshop',
                                                 'first_look', 'datasources', 'assets', 'discovery', 'session']):
            analytics_prompts.append(func_name)
        # Analytics resources
        else:
            analytics_resources.append(func_name)
    
    print("=" * 60)
    print("STAFFER AVAILABLE FUNCTIONS SUMMARY")
    print("=" * 60)
    print(f"Total Functions: {len(all_functions)}")
    print()
    
    # File Operations
    print(f"📁 File Operations ({len(file_ops)} functions):")
    for func in file_ops:
        print(f"   • {func}")
    print()
    
    # Excel Operations
    print(f"📊 Excel Operations ({len(excel)} functions):")
    for func in excel:
        print(f"   • {func}")
    print()
    
    # Analytics Tools
    print(f"🔧 Analytics Tools ({len(analytics_tools)} functions):")
    for func in analytics_tools:
        print(f"   • {func}")
    print()
    
    # Analytics Resources
    print(f"📋 Analytics Resources ({len(analytics_resources)} functions):")
    for func in analytics_resources:
        print(f"   • {func}")
    print()
    
    # Analytics Prompts
    print(f"💬 Analytics Prompts ({len(analytics_prompts)} functions):")
    for func in analytics_prompts:
        print(f"   • {func}")
    
    print("=" * 60)
    print(f"✅ Successfully registered all {len(all_functions)} functions!")
    print("=" * 60)


if __name__ == "__main__":
    print_function_summary()