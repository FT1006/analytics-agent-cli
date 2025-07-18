import os
import argparse
from pathlib import Path
from google.genai import types
import sys
from .available_functions import get_available_functions, call_function
from .llm import get_client

def _is_ancestor(path: Path, cwd: Path) -> bool:
    """Check if path is an ancestor of cwd (parent, grandparent, etc)."""
    try:
        return path != cwd and cwd.is_relative_to(path)
    except (ValueError, TypeError):
        return False


def prune_stale_dir_msgs(msgs, cwd: Path, max_messages=120):
    """Filter stale directory context with ancestor path detection. Returns new list, no mutation."""
    cwd_str = str(cwd)
    
    # Get all ancestor paths to filter out
    ancestor_paths = []
    current = cwd.parent
    while current != current.parent:  # Stop at filesystem root
        ancestor_paths.append(str(current))
        current = current.parent
    
    kept = []
    for m in msgs:
        skip_message = False
        
        if m.role == "model" and m.parts:
            text = m.parts[0].text or ""
            
            # Drop old cwd headers that don't match current directory
            if "[Working directory:" in text and cwd_str not in text:
                skip_message = True
                
            # Drop messages that specifically reference working IN ancestor paths
            else:
                for ancestor_path in ancestor_paths:
                    # Only filter if it looks like a working directory reference
                    if (cwd_str not in text and 
                        (text.endswith(str(ancestor_path)) or 
                         f"in {ancestor_path}" in text or
                         f"Working in {ancestor_path}" in text or
                         f"Files in {ancestor_path}" in text)):
                        skip_message = True
                        break
                
        # Enhanced tool response filtering for ancestor directories
        elif m.role == "tool" and m.parts:
            fc = getattr(m.parts[0], "function_response", None)
            if fc and getattr(fc, "name", "") == "get_files_info":
                result = str(getattr(fc, "response", {}).get("result", ""))
                # Drop tool responses that start with ancestor paths but not current path
                for ancestor_path in ancestor_paths:
                    if result.startswith(ancestor_path) and not result.startswith(cwd_str):
                        skip_message = True
                        break
        
        if not skip_message:
            kept.append(m)
    
    # Hard limit on message count to prevent token overflow
    if len(kept) > max_messages:
        # Keep most recent messages to preserve context
        kept = kept[-max_messages:]
    
    return kept


def build_prompt(messages, working_directory=None):
    """Build system prompt with working directory and function info."""
    if working_directory is None:
        working_directory = Path.cwd()
    else:
        working_directory = Path(working_directory)
    
    # Double header weight for salience without per-turn spam
    cwd_header_1 = f"[cwd: {working_directory}]"
    cwd_header_2 = f"⚠️ You are now working in {working_directory}. Always answer with this full path."
    
    return f"""{cwd_header_1}
{cwd_header_2}

You are a helpful AI coding agent working in: {working_directory}

When asked about your location or "where you are", you should state: {working_directory}

You can perform the following operations:

- List files and directories using get_files_info()
- Read file contents using get_file_content(path)  
- Execute Python files using run_python_file(path, args)
- Write or overwrite files using write_file(path, content)

All paths you provide should be relative to the working directory: {working_directory}

You have access to these functions - use them confidently to explore directories, read files, and accomplish tasks."""


def process_prompt(prompt, verbose=False, messages=None, terminal=None, spinner=None):
    """Process a single prompt using the AI agent."""
    if messages is None:
        messages = []
    working_directory = Path(os.getcwd())
    
    # Track if spinner has been stopped
    spinner_stopped = False
    
    def stop_spinner_once():
        nonlocal spinner_stopped
        if spinner is not None and not spinner_stopped:
            try:
                spinner.__exit__(None, None, None)
            except:
                pass
            spinner_stopped = True
    available_functions = get_available_functions(str(working_directory))

    if verbose:
        print(f"Working directory: {working_directory}")
        print(f"User prompt: {prompt}")

    # Filter stale directory context from conversation history
    clean_messages = prune_stale_dir_msgs(messages, working_directory)
    system_prompt = build_prompt(clean_messages, working_directory)

    # Add current user prompt
    current_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    # Build conversation for LLM (history + current prompt)
    conversation_for_llm = clean_messages + [current_message]

    client = get_client()
    
    for i in range(20):
        function_called = False
        res = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=conversation_for_llm,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
            )   
        )    

        promptTokens = res.usage_metadata.prompt_token_count
        responseTokens = res.usage_metadata.candidates_token_count

        if res.candidates:
            for candidate in res.candidates:
                # Collect all function responses for this turn
                function_response_parts = []
                # Handle potential None parts (malformed LLM response)
                parts = candidate.content.parts or []
                for part in parts:
                    if part.function_call:
                        function_called = True
                        # Stop spinner before first output
                        stop_spinner_once()
                        # Display function call indicator if terminal provided
                        if terminal:
                            terminal.display_function_call(part.function_call.name)
                        if verbose:
                            function_call_result = call_function(part.function_call, working_directory, verbose=True)
                        else:
                            function_call_result = call_function(part.function_call, working_directory)
                        if not function_call_result.parts[0].function_response.response:
                            sys.exit(1)
                        else:
                            function_response_parts.append(
                                types.Part(function_response=types.FunctionResponse(
                                    name=part.function_call.name,
                                    response=function_call_result.parts[0].function_response.response
                                ))
                            )
                
                # Add assistant response to conversation history (validate parts first)
                if candidate.content.parts and len(candidate.content.parts) > 0:
                    conversation_for_llm.append(candidate.content)
                elif verbose:
                    print(f"   ⚠️  Skipping empty content from conversation history")
                
                # Add all function responses as a single tool message
                if function_response_parts:
                    tool_message = types.Content(
                        role="tool",
                        parts=function_response_parts
                    )
                    conversation_for_llm.append(tool_message)
            if not function_called:
                # Stop spinner before AI response
                stop_spinner_once()
                if terminal:
                    terminal.display_ai_response(res.text)
                else:
                    print(f"-> {res.text}")
                break
        i+=1

    if verbose:
        print(f"Prompt tokens: {promptTokens}")
        print(f"Response tokens: {responseTokens}")
    
    # Return conversation_for_llm which now contains all the new responses
    return conversation_for_llm


def main():
    parser = argparse.ArgumentParser(
        description="Analytics Agent CLI - AI analytics agent for data analysis and insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  aacli                             # Start interactive mode (default)
  aacli "analyze this dataset"      # Single command mode
  aacli "create insights from data" --verbose
  aacli --interactive               # Explicit interactive mode

Interactive Mode Features:
  • Rich terminal interface with syntax highlighting
  • Smart prompts showing directory and message count: analytics-agent ~/project [5 msgs]>
  • Up/down arrow keys for command history navigation
  • Session commands: /reset, /session, /help
  • Directory change detection (prompts when switching folders)
  • Auto-save conversations, persistent command history
  • Visual feedback: ✅ success, ⚠️ warnings, processing spinners
  • Function call indicators showing what AI is doing
  • Type 'exit' or 'quit' to save and quit

Terminal Experience:
  • Enhanced mode: Rich UI when prompt-toolkit/rich/yaspin available
  • Basic mode: Clean fallback that works everywhere
  • Automatic detection and graceful fallback"""
    )
    parser.add_argument("prompt", nargs='?', help="The task or question for the AI agent")
    parser.add_argument("--verbose", action="store_true", help="Show detailed function call information")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--version", action="version", version="Analytics Agent CLI 0.1.0")
    
    args = parser.parse_args()
    
    # Handle interactive mode - either explicit flag or no prompt provided
    if args.interactive or not args.prompt:
        from .cli.interactive import main as interactive_main
        interactive_main(verbose=args.verbose)
        return
    
    # Single command mode with prompt
    process_prompt(args.prompt, args.verbose)

if __name__ == "__main__":
    main()