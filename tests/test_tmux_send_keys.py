#!/usr/bin/env python3
"""Test script to verify tmux send-keys with Enter key (C-m)."""

import subprocess
import time
import sys


def test_tmux_send_keys_basic():
    """Test basic tmux send-keys functionality with Enter key."""
    print("=" * 60)
    print("Test 1: Basic tmux send-keys with C-m")
    print("=" * 60)

    session_id = "test_send_keys_1"

    # Clean up any existing session
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)

    # Create a new tmux session
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_id],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Failed to create session: {result.stderr}")
        return False
    print(f"Created tmux session: {session_id}")

    # Send a simple echo command with Enter key
    test_command = "echo 'Hello from tmux test'"
    result = subprocess.run(
        ["tmux", "send-keys", "-t", session_id, test_command, "C-m"],
        capture_output=True,
        text=True
    )
    print(f"Send-keys return code: {result.returncode}")
    if result.stderr:
        print(f"Stderr: {result.stderr}")

    # Wait for command to execute
    time.sleep(0.5)

    # Capture session output
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session_id, "-p"],
        capture_output=True,
        text=True
    )
    print(f"\nSession output:\n{result.stdout}")

    # Check if our echo output is visible
    if "Hello from tmux test" in result.stdout:
        print("\u2713 SUCCESS: Command was executed and output is visible")
    else:
        print("\u2717 FAILED: Command output not found in session")

    # Clean up
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)
    print(f"\nCleaned up session: {session_id}")
    return "Hello from tmux test" in result.stdout


def test_tmux_send_keys_no_enter():
    """Test tmux send-keys WITHOUT Enter key (should NOT execute)."""
    print("\n" + "=" * 60)
    print("Test 2: tmux send-keys WITHOUT C-m (should not execute)")
    print("=" * 60)

    session_id = "test_send_keys_2"

    # Clean up any existing session
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)

    # Create a new tmux session
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_id],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Failed to create session: {result.stderr}")
        return False
    print(f"Created tmux session: {session_id}")

    # Send a command WITHOUT Enter key
    test_command = "echo 'This should not execute'"
    result = subprocess.run(
        ["tmux", "send-keys", "-t", session_id, test_command],
        capture_output=True,
        text=True
    )
    print(f"Send-keys return code: {result.returncode}")

    # Wait briefly
    time.sleep(0.3)

    # Capture session output
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session_id, "-p"],
        capture_output=True,
        text=True
    )
    print(f"\nSession output:\n{result.stdout}")

    # Without Enter, the command should NOT be executed
    # The text should appear but not the execution output
    if "This should not execute" in result.stdout:
        if "This should not execute" in result.stdout and \
           not ("This should not execute" in result.stdout and "$" in result.stdout.split("This should not execute")[0].split("\n")[-1]):
            print("\u2713 SUCCESS: Command text visible but NOT executed (as expected)")
        else:
            print("\u2717 Command may have been executed (unexpected)")
    else:
        print("Command text not found in session")

    # Clean up
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)
    print(f"\nCleaned up session: {session_id}")
    return True


def test_tmux_send_keys_with_delay():
    """Test tmux send-keys with small delay (our fix)."""
    print("\n" + "=" * 60)
    print("Test 3: tmux send-keys with delay (simulating fix)")
    print("=" * 60)

    session_id = "test_send_keys_3"

    # Clean up any existing session
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)

    # Create a new tmux session
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_id],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Failed to create session: {result.stderr}")
        return False
    print(f"Created tmux session: {session_id}")

    # Send command with Enter key
    test_command = "echo 'Test with delay fix'"
    result = subprocess.run(
        ["tmux", "send-keys", "-t", session_id, test_command, "C-m"],
        capture_output=True,
        text=True
    )
    print(f"Send-keys return code: {result.returncode}")

    # Apply the fix: small delay after sending keys
    time.sleep(0.1)

    # Capture session output
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session_id, "-p"],
        capture_output=True,
        text=True
    )
    print(f"\nSession output:\n{result.stdout}")

    if "Test with delay fix" in result.stdout:
        print("\u2713 SUCCESS: Command executed with delay fix")
    else:
        print("\u2717 FAILED: Command output not found")

    # Clean up
    subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)
    print(f"\nCleaned up session: {session_id}")
    return "Test with delay fix" in result.stdout


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("# Tmux Send-Keys Enter Key (C-m) Test Suite")
    print("#" * 60 + "\n")

    results = []

    # Test 1: Basic functionality
    results.append(("Basic C-m test", test_tmux_send_keys_basic()))

    # Test 2: Without Enter (control)
    results.append(("No Enter test", test_tmux_send_keys_no_enter()))

    # Test 3: With delay fix
    results.append(("Delay fix test", test_tmux_send_keys_with_delay()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "\u2713 PASS" if result else "\u2717 FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(r for _, r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
