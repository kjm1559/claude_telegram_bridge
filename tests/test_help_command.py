#!/usr/bin/env python3
"""Test script for /help command functionality."""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.command_handlers import HelpCommand


def test_help_command():
    """Test /help command processing."""
    print("\n=== Testing /help command ===")

    # Create help command handler (doesn't need session_manager)
    help_cmd = HelpCommand()

    # Test /help
    print("\n1. Testing '/help'...")
    success, response = help_cmd.handle(12345, None)
    print(f"Success: {success}")
    print(f"Response: {response[:200]}...")
    assert success, "Help command should succeed"
    assert len(response) > 0, "Help command should return response text"
    print("✅ /help works!")

    # Test /help /new_session
    print("\n2. Testing '/help /new_session'...")
    success, response = help_cmd.handle(12345, "/new_session")
    print(f"Success: {success}")
    print(f"Response: {response[:200]}...")
    assert success, "/help /new_session should succeed"
    print("✅ /help /new_session works!")

    # Test unknown command
    print("\n3. Testing '/help /unknown'...")
    success, response = help_cmd.handle(12345, "/unknown")
    print(f"Success: {success}")
    print(f"Response: {response[:200]}...")
    print("✅ Unknown command handling works!")

    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    test_help_command()
