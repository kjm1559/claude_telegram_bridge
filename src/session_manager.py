#!/usr/bin/env python3
"""Session manager for Claude Telegram Bridge."""

import subprocess
import uuid
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple, List
from datetime import datetime

from .config import BASE_DIR, CLAUDE_BINARY, CLAUDE_PROJECTS_DIR

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages tmux and Claude sessions."""

    def __init__(self, db, project_dir: Optional[Path] = None, message_monitor = None):
        """Initialize session manager.

        Args:
            db: Database instance.
            project_dir: Optional project directory for session files.
            message_monitor: Optional message monitor instance for real-time monitoring.
        """
        self.db = db
        self.project_dir = project_dir or self._create_project_dir()
        self.message_monitor = message_monitor

    def _create_project_dir(self) -> Path:
        """Create project directory for session files.

        Returns:
            Path to project directory.
        """
        # Project directory template: /home/user/path/-home-user-path
        cwd = "/tmp"
        cwd_name = "tmp"  # simplified for now
        return Path(f"{cwd}/-{cwd_name}")

    def get_session_file_path(self, session_id: str, cwd: str) -> Path:
        """Compute the path to a session's JSONL file.

        Args:
            session_id: UUID of the session.
            cwd: Working directory of the session.

        Returns:
            Path to the JSONL file.
        """
        # Extract project name from cwd
        # e.g., /home/mj/claude_telegram_bridge -> -home-mj-claude-telegram-bridge
        project_path = Path(cwd)

        # Build folder name: -<path-with-hyphens>
        path_parts = [p.replace(" ", "-") for p in project_path.parts]
        folder_name = "-" + "-".join(path_parts)

        return CLAUDE_PROJECTS_DIR / folder_name / f"{session_id}.jsonl"

    def generate_uuid(self) -> str:
        """Generate a new UUID for session.

        Returns:
            UUID string.
        """
        return str(uuid.uuid4())

    def create_session(self, session_id: str, cwd: str) -> Tuple[bool, str]:
        """Create a new tmux and Claude session.

        Args:
            session_id: UUID for the session.
            cwd: Current working directory.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Create tmux session
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_id],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, f"Failed to create tmux session: {result.stderr}"

            # Launch Claude in the session
            # Using a simple shell command for Claude
            # In production, this would be a proper Claude CLI call
            claude_cmd = f"{CLAUDE_BINARY} --session-id {session_id}"
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_id, claude_cmd, "C-m"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                # Clean up tmux session on failure
                subprocess.run(["tmux", "kill-session", "-t", session_id], capture_output=True)
                return False, f"Failed to start Claude: {result.stderr}"

            # Store session in database
            self.db.create_session(session_id, cwd)

            return True, f"Session {session_id} created successfully"

        except Exception as e:
            return False, f"Error creating session: {str(e)}"

    def end_session(self, session_id: str) -> Tuple[bool, str]:
        """End a tmux session.

        Args:
            session_id: UUID of the session to end.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Kill tmux session
            result = subprocess.run(
                ["tmux", "kill-session", "-t", session_id],
                capture_output=True,
                text=True
            )

            if result.returncode != 0 and "no server" not in result.stderr:
                return False, f"Failed to kill tmux session: {result.stderr}"

            # Mark as inactive in database
            self.db.deactivate_session(session_id)

            # Unregister from message monitor if available
            if self.message_monitor is not None:
                self.message_monitor.unregister_session(session_id)

            return True, f"Session {session_id} terminated"

        except Exception as e:
            return False, f"Error ending session: {str(e)}"

    def is_session_active(self, session_id: str) -> bool:
        """Check if a tmux session is active.

        Args:
            session_id: UUID of the session.

        Returns:
            True if session is active, False otherwise.
        """
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_id],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_all_active_sessions(self) -> List[str]:
        """Get list of all active tmux sessions.

        Returns:
            List of session IDs.
        """
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            sessions = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # Format: session_id: (attached|detached)
                    parts = line.split(":")
                    if parts:
                        sessions.append(parts[0])

            return sessions
        except Exception:
            return []

    def send_interrupt(self, session_id: str) -> Tuple[bool, str]:
        """Send interrupt signal (Escape key) to session.

        Args:
            session_id: UUID of the session.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Check if session exists
            if not self.is_session_active(session_id):
                return False, f"Session {session_id} is not active"

            # Send Escape key to interrupt
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_id, "Escape"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, f"Failed to send interrupt: {result.stderr}"

            return True, f"Interrupt signal sent to session {session_id}"

        except Exception as e:
            return False, f"Error sending interrupt: {str(e)}"

    def send_keys(self, session_id: str, command: str) -> Tuple[bool, str]:
        """Send command to tmux session.

        Args:
            session_id: UUID of the session.
            command: Command to send.

        Returns:
            Tuple of (success, message).
        """
        logger.info(f"[SESSION] send_keys called: session_id={session_id}, command='{command[:100]}'")
        try:
            # Check if session exists
            if not self.is_session_active(session_id):
                logger.error(f"[SESSION] Session {session_id} is not active")
                return False, f"Session {session_id} is not active"

            # Send command with Enter
            logger.info(f"[SESSION] Sending to tmux: session={session_id}, command='{command}'")
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_id, command, "C-m"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"[SESSION] Failed to send command: {result.stderr}")
                return False, f"Failed to send command: {result.stderr}"

            logger.info(f"[SESSION] Command sent successfully to {session_id}")
            return True, f"Command sent to session {session_id}"

        except Exception as e:
            return False, f"Error sending command: {str(e)}"

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information from database and tmux.

        Args:
            session_id: UUID of the session.

        Returns:
            Session info dictionary or None.
        """
        session = self.db.get_session(session_id)
        if not session:
            return None

        # Check tmux status
        active = self.is_session_active(session_id)

        return {
            "session_id": session["session_id"],
            "cwd": session["cwd"],
            "created_at": session["created_at"],
            "last_used": session["last_used"],
            "is_active": active or session["is_active"],
            "tmux_active": active
        }

    def select_session(self, chat_id: int, session_id: str) -> Tuple[bool, str]:
        """Select a session for a user.

        Args:
            chat_id: Telegram chat ID.
            session_id: UUID of session to select.

        Returns:
            Tuple of (success, message).
        """
        # Verify session exists and is valid
        session = self.db.get_session(session_id)
        if not session:
            return False, f"Session {session_id} not found"

        if not self.is_session_active(session_id):
            return False, f"Session {session_id} is not active"

        # Set selected session
        self.db.set_user_session(chat_id, session_id)
        self.db.update_session_last_used(session_id)

        # Register with message monitor if available
        if self.message_monitor is not None:
            self.message_monitor.register_session(session_id, chat_id, session["cwd"])

        return True, f"Selected session: {session_id}"

    def get_selected_session(self, chat_id: int) -> Optional[str]:
        """Get selected session for a user.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Session ID or None.
        """
        return self.db.get_user_session(chat_id)
