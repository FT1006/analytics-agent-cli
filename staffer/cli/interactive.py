"""Interactive mode for Staffer - continuous prompt loop."""

import os
from pathlib import Path
from google.genai import types
from ..main import process_prompt
from ..session import load_session, save_session, create_working_directory_message, load_session_with_metadata, save_session_with_metadata
from ..available_functions import get_available_functions, call_function
from ..llm import get_client
from ..ui.terminal import get_terminal_ui


def check_directory_change(metadata):
    """Check if cwd has changed since session creation."""
    current_cwd = os.getcwd()
    session_cwd = metadata.get('cwd')
    
    # If no cwd in metadata, no change to detect
    if not session_cwd:
        return False
        
    return current_cwd != session_cwd


def prompt_directory_change(old_dir, new_dir):
    """Prompt user about directory change."""
    print(f"Directory changed from {old_dir} to {new_dir}")
    choice = input("[N] Start new session  [K] Keep old session\nChoice (N/k): ")
    return choice.lower() not in ['k']


def should_reinitialize_working_directory(messages, current_dir):
    """Check if we need to reinitialize working directory based on message history."""
    # For now, always reinitialize to ensure fresh context
    # TODO: Could add smarter detection based on last working directory call
    return True


def initialize_session_with_working_directory(messages, verbose=False):
    """Force AI to call get_working_directory to establish current location."""
    working_directory = Path(os.getcwd())
    available_functions = get_available_functions(str(working_directory))
    
    # Add explicit directive to get working directory
    init_prompt = "You MUST call get_working_directory() to confirm your current working directory before proceeding."
    current_message = types.Content(
        role="user",
        parts=[types.Part(text=init_prompt)]
    )
    
    conversation = messages + [current_message]
    
    # Enhanced system instruction to force function call
    system_prompt = """On every new interactive session initialization, your FIRST ACTION must be calling get_working_directory(). 
Do not proceed with any other requests until you've explicitly called and confirmed the working directory.

You MUST call get_working_directory() immediately when asked to confirm your working directory."""
    
    client = get_client()
    
    # Force the function call
    for i in range(3):  # Try up to 3 times
        res = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=conversation,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
            )
        )
        
        if res.candidates:
            for candidate in res.candidates:
                # Handle potential None parts (malformed LLM response)
                parts = candidate.content.parts or []
                for part in parts:
                    if part.function_call and part.function_call.name == "get_working_directory":
                        # Function called! Execute it and add result
                        function_result = call_function(part.function_call, str(working_directory), verbose=verbose)
                        conversation.append(function_result)
                        
                        # Add confirmation message
                        confirmation = types.Content(
                            role="model",
                            parts=[types.Part(text=f"🛠️ **Confirmed working directory**: {working_directory}")]
                        )
                        conversation.append(confirmation)
                        
                        # Return only the original messages without the initialization
                        # The working directory has been confirmed, no need to add to history
                        return messages
                
                # Add response to conversation history only if it has valid parts
                if candidate.content.parts and len(candidate.content.parts) > 0:
                    conversation.append(candidate.content)
                elif verbose:
                    print(f"   ⚠️  Skipping empty content from conversation history")
        
        # If no function call, break
        # Handle potential None parts in generator expression
        has_function_calls = any(
            part.function_call 
            for candidate in res.candidates 
            for part in (candidate.content.parts or [])
            if part.function_call
        )
        if not has_function_calls:
            break
    
    # If function wasn't called, return original messages
    return messages


def process_command(user_input, messages):
    """Process special commands. Returns (handled, updated_messages)."""
    if not user_input.startswith('/'):
        return False, messages
    
    command = user_input.lower()
    
    if command == '/reset':
        print("Session cleared. Starting fresh in", os.getcwd())
        save_session_with_metadata([])  # Save empty session
        return True, []  # Clear all messages
    
    elif command == '/session':
        show_session_info(messages)
        return True, messages  # Don't modify messages
    
    elif command == '/help':
        show_help()
        return True, messages  # Don't modify messages
    
    else:
        print(f"Unknown command: {user_input}")
        print("Type /help for available commands")
        return True, messages  # Don't modify messages


def count_conversation_items(messages):
    """Count different types of conversation items."""
    user_questions = 0
    agent_responses = 0
    function_attempts = 0
    function_successes = 0
    
    for msg in messages:
        if hasattr(msg, 'role'):
            if msg.role == 'user':
                user_questions += 1
            elif msg.role == 'model':
                # Check if this model message contains function calls or is a text response
                if hasattr(msg, 'parts') and msg.parts:
                    has_function_calls = any(hasattr(part, 'function_call') and part.function_call for part in msg.parts)
                    has_text = any(hasattr(part, 'text') and part.text for part in msg.parts)
                    
                    if has_function_calls:
                        # Count function call attempts
                        function_attempts += sum(1 for part in msg.parts if hasattr(part, 'function_call') and part.function_call)
                    
                    if has_text and not has_function_calls:
                        # Only count as agent response if it's PURE text (no function calls)
                        agent_responses += 1
            elif msg.role == 'tool':
                # Count successful function executions
                function_successes += 1
    
    return user_questions, function_attempts, function_successes, agent_responses


def estimate_tokens_breakdown(messages):
    """Estimate input and output tokens separately."""
    input_chars = 0
    output_chars = 0
    
    for msg in messages:
        if hasattr(msg, 'role') and hasattr(msg, 'parts') and msg.parts:
            msg_chars = sum(len(str(part)) for part in msg.parts)
            
            if msg.role == 'user':
                input_chars += msg_chars
            elif msg.role == 'model':
                output_chars += msg_chars
            elif msg.role == 'tool':
                # Tool responses count as output
                output_chars += msg_chars
    
    # Rough approximation: 4 characters per token
    input_tokens = input_chars // 4
    output_tokens = output_chars // 4
    total_tokens = input_tokens + output_tokens
    
    return input_tokens, output_tokens, total_tokens


def show_session_info(messages):
    """Display current session information."""
    current_dir = os.getcwd()
    user_questions, function_attempts, function_successes, agent_responses = count_conversation_items(messages)
    input_tokens, output_tokens, total_tokens = estimate_tokens_breakdown(messages)
    
    print(f"Current Directory: {current_dir}")
    print(f"User questions: {user_questions}")
    print(f"Agent responses: {agent_responses}")
    print(f"Function call attempts: {function_attempts}")
    print(f"Function call successes: {function_successes}")
    print(f"Estimated tokens - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")


def show_help():
    """Display available commands."""
    print("Available commands:")
    print("  /reset    - Clear conversation history")
    print("  /session  - Show session info")
    print("  /help     - Show this help")
    print("  /exit     - Save session and quit")
    print("  /quit     - Save session and quit")


def main(verbose=False):
    """Main interactive mode entry point."""
    # Get terminal UI (enhanced or basic)
    terminal = get_terminal_ui()
    terminal.display_welcome()
    terminal.display_success("Type '/exit' or '/quit' to end the session")
    
    # Load previous session with metadata 
    messages, metadata = load_session_with_metadata()
    
    # Check for directory change
    if messages and check_directory_change(metadata):
        old_dir = metadata.get('cwd', 'unknown')
        new_dir = os.getcwd()
        
        if prompt_directory_change(old_dir, new_dir):
            # User wants new session
            messages = []
            print("Starting new session...")
        else:
            # User wants to keep old session
            print(f"Keeping session from {old_dir}")
    
    if messages:
        terminal.display_success(f"Restored conversation with {len(messages)} previous messages")
    
    # Force working directory initialization
    current_dir = Path(os.getcwd())
    # COMMENTED OUT: Let users choose when to provide directory context
    # if should_reinitialize_working_directory(messages, current_dir):
    #     with terminal.show_spinner("Initializing working directory context..."):
    #         messages = initialize_session_with_working_directory(messages, verbose=verbose)
    #         save_session_with_metadata(messages)
    
    print()  # Spacing
    
    while True:
        try:
            # Build session info for rich prompt
            user_questions, function_attempts, function_successes, agent_responses = count_conversation_items(messages)
            session_info = {
                'cwd': str(current_dir),
                'message_count': agent_responses
            }
            user_input = terminal.get_input(session_info).strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['/exit', '/quit']:
                # Save session with metadata before exiting - Slice 4 feature
                save_session_with_metadata(messages)
                terminal.display_success("Session saved")
                terminal.display_success("Goodbye!")
                break
            
            # Check for special commands first
            handled, messages = process_command(user_input, messages)
            if handled:
                continue
                
            # Start spinner for AI processing
            spinner = terminal.show_spinner("AI is thinking...")
            spinner.__enter__()
            try:
                messages = process_prompt(user_input, verbose=verbose, messages=messages, terminal=terminal, spinner=spinner)
            finally:
                # Ensure spinner is stopped (process_prompt may have already stopped it)
                try:
                    spinner.__exit__(None, None, None)
                except:
                    pass
            
        except (EOFError, KeyboardInterrupt):
            # Save session before exiting on Ctrl+C - Slice 4 feature
            save_session_with_metadata(messages)
            terminal.display_success("Session saved")
            print("\nGoodbye!")
            break
        except Exception as e:
            terminal.display_error(f"Error: {e}")
            continue