#!/bin/bash
# Simple script to install the /generate command

echo "Installing /generate command..."

# Move the temp file to the correct location
if [ -f "generate_command_temp.md" ]; then
    mv generate_command_temp.md .claude/commands/generate.md
    echo "✅ Successfully installed /generate command at .claude/commands/generate.md"
else
    echo "❌ Error: generate_command_temp.md not found"
    echo "Make sure you're running this from the workflow directory"
    exit 1
fi

# Verify
if [ -f ".claude/commands/generate.md" ]; then
    echo "✅ Verification: Command file exists"
    echo ""
    echo "You can now use the /generate command in your workflow!"
    echo "Example: /generate v1.0.0 v0.9.0"
else
    echo "❌ Verification failed: Command file not created"
    exit 1
fi
