"""
CLI Main Application

Main entry point for the CLI.
"""

import argparse
import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from free_llm_api import FreeLLMAPI, FreeLLMAPIConfig
from .commands import COMMANDS, BaseCommand, CommandResult

logger = logging.getLogger(__name__)


class CLIApp:
    """
    Command-line interface application for Free LLM API.
    
    Provides an interactive and non-interactive CLI for accessing
    free LLM providers.
    """
    
    def __init__(self):
        self.api = FreeLLMAPI()
        self.commands: Dict[str, BaseCommand] = {}
        self._init_commands()
        self.interactive_mode = False
    
    def _init_commands(self):
        """Initialize all commands."""
        for name, cmd_class in COMMANDS.items():
            self.commands[name] = cmd_class(self.api)
    
    async def initialize(self):
        """Initialize the API."""
        await self.api.initialize()
    
    async def run(self, args: Optional[List[str]] = None):
        """
        Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments (None for sys.argv)
        """
        if args is None:
            args = sys.argv[1:]
        
        # Check for help
        if not args or "--help" in args or "-h" in args:
            self.print_help()
            return
        
        # Check for interactive mode
        if "--interactive" in args or "-i" in args:
            await self.run_interactive()
            return
        
        # Parse command
        if not args:
            self.print_help()
            return
        
        command_name = args[0]
        command_args = args[1:]
        
        # Check for help on specific command
        if "--help" in command_args or "-h" in command_args:
            if command_name in self.commands:
                print(self.commands[command_name].get_help())
            else:
                print(f"Unknown command: {command_name}")
            return
        
        # Execute command
        if command_name in self.commands:
            await self._execute_command(command_name, command_args)
        else:
            print(f"Unknown command: {command_name}")
            print(f"Available commands: {', '.join(self.commands.keys())}")
    
    async def _execute_command(self, command_name: str, args: List[str]):
        """Execute a specific command."""
        try:
            # Initialize API if not already done
            if not self.api._initialized:
                await self.api.initialize()
            
            # Execute command
            result = await self.commands[command_name].execute(args)
            
            if not result.success:
                if result.error:
                    print(f"Error: {result.error}", file=sys.stderr)
                elif result.message:
                    print(f"Error: {result.message}", file=sys.stderr)
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            logger.exception("Error executing command")
            sys.exit(1)
    
    async def run_interactive(self):
        """Run in interactive mode."""
        self.interactive_mode = True
        
        print("\n" + "=" * 60)
        print("Free LLM API - Interactive Mode")
        print("=" * 60)
        print("\nType 'help' for available commands, 'exit' to quit")
        print()
        
        # Initialize API
        await self.initialize()
        
        while True:
            try:
                # Get input
                try:
                    user_input = input("llmapi> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Parse input
                parts = user_input.split()
                if not parts:
                    continue
                
                command_name = parts[0]
                command_args = parts[1:]
                
                # Handle special commands
                if command_name in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break
                
                if command_name in ("help", "?"):
                    if command_args:
                        if command_args[0] in self.commands:
                            print(self.commands[command_args[0]].get_help())
                        else:
                            print(f"Unknown command: {command_args[0]}")
                    else:
                        self.print_help()
                    continue
                
                # Execute command
                if command_name in self.commands:
                    result = await self.commands[command_name].execute(command_args)
                    if not result.success:
                        if result.error:
                            print(f"Error: {result.error}")
                        elif result.message:
                            print(f"Error: {result.message}")
                else:
                    print(f"Unknown command: {command_name}")
                    print(f"Available commands: {', '.join(self.commands.keys())}")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to leave interactive mode")
            except Exception as e:
                print(f"Error: {e}")
                logger.exception("Error in interactive mode")
    
    def print_help(self):
        """Print help message."""
        print("\n" + "=" * 60)
        print("Free LLM API - Command Line Interface")
        print("=" * 60)
        print("\nUsage:")
        print("  llmapi [command] [options]")
        print("  llmapi --interactive  # Start interactive mode")
        print("\nCommands:")
        
        for name, cmd in self.commands.items():
            usage = cmd.get_usage()
            print(f"  {name:15} {usage}")
        
        print("\nOptions:")
        print("  --interactive, -i   Start interactive mode")
        print("  --help, -h         Show this help message")
        print("\nExamples:")
        print('  llmapi chat "What is AI?"')
        print("  llmapi list")
        print("  llmapi info groq")
        print("  llmapi --interactive")
        print("=" * 60)


async def main():
    """Main entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run CLI
    cli = CLIApp()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
