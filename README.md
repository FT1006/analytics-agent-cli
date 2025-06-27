# Analytic Agent CLI - AI Analytics in Folders

AI that works in whatever folder you're in. Just `cd` to any project and talk to AI about your data.

## Quick Start

Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey), then:

```bash
# Install
git clone https://github.com/FT1006/analytic-agent-cli.git
cd analytic-agent-cli
pip install -e .

# Set your API key
export GEMINI_API_KEY=your_key_here

# Go to any folder and chat with AI
cd /your/project
staffer # Start interactive mode (default)

# Optional: Install enhanced terminal dependencies
pip install prompt-toolkit rich yaspin

# Or run single commands
staffer "what files are here?"
staffer "add error handling to main.py"
```

## How it works

- **AI knows your folder** - Understands what's in your current directory
- **Reads and writes files** - Can view and modify Excel files and data in your folder
- **Analyzes data** - Performs analytics and creates insights from your datasets
- **Remembers conversations** - Picks up where you left off
- **Adapts to folder changes** - Asks if you want to continue or start fresh when you switch projects
- **Enhanced terminal UI** - Rich prompts, command history, and syntax highlighting
- **Works everywhere** - Any folder, any project

## How UX works

- **Smart sessions** - Automatically saves and restores your conversations
- **Directory detection** - Notices when you switch folders and asks what to do
- **Session commands** - Use `/reset`, `/session`, `/help` in interactive mode
- **Natural exit** - Just type `exit` or `quit` to save and leave
- **Arrow key history** - Use ↑↓ to navigate through previous commands
- **Persistent history** - Command history saved across sessions

**Terminal Dependencies (optional):**

```bash
pip install prompt-toolkit rich yaspin
```

If not installed, Analytic Agent CLI automatically falls back to basic terminal mode.

## Examples

```bash
# Start interactive chat in any folder (default)
cd ~/my-python-project
staffer
# 🚀 Analytic Agent CLI - AI Analytics in Folders
# Enhanced terminal mode enabled
staffer ~/my-python-project [0 msgs]> what's in this folder?
# 🔧 Calling get_files_info...
# [AI shows your files with syntax highlighting]
staffer ~/my-python-project [2 msgs]> create a README for this project
# ⚡ AI is thinking...
# [AI creates README.md]
staffer ~/my-python-project [4 msgs]> exit
# ✅ Session saved
# ✅ Goodbye!

# Run single commands without entering interactive mode
cd ~/my-web-app
staffer "fix the bug in main.py"
staffer "add tests for the main functions"

# Switch folders, AI adapts automatically
cd ~/my-data-project
staffer
# Analytic Agent CLI notices you changed folders
Directory changed from ~/my-web-app to ~/my-data-project
[N] Start new session  [K] Keep old session
Choice (N/k): n
staffer ~/my-data-project [0 msgs]> what kind of project is this?
```

## Troubleshooting

**API Key not working?**

```bash
echo $GEMINI_API_KEY  # Should show your key
```

**Command not found?**

```bash
pip install -e .  # Reinstall
which staffer      # Check if in PATH
```

**Need help?**

```bash
staffer --help
```

That's it! AI that understands your folders and helps with your data.
