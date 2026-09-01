"""
Custom Command Service module for Intelligent Python Voice Assistant.
Safely loads, validates, and executes configuration-based user custom commands.
Enforces strict security policies (no eval/exec or unsafe shell execution).
"""

import json
import os
import webbrowser
from typing import Tuple, List, Dict, Any, Optional
from core.logger import get_logger
from config import Config

logger = get_logger("CustomService")

class CustomCommandService:
    """Manages custom user commands loaded from JSON configuration."""

    ALLOWED_ACTION_TYPES = {"open_url", "response"}

    def __init__(self, custom_config_path: Optional[str] = None):
        self.config_path = custom_config_path or str(Config.CUSTOM_COMMANDS_FILE)
        self.commands: List[Dict[str, Any]] = []
        self.load_and_validate_commands()

    def load_and_validate_commands(self) -> bool:
        """Loads and validates custom command definitions from JSON configuration."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Custom commands configuration file not found at: {self.config_path}")
            self.commands = []
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "commands" not in data or not isinstance(data["commands"], list):
                logger.error(f"Invalid schema in custom commands configuration file: {self.config_path}")
                self.commands = []
                return False

            valid_commands = []
            for cmd in data["commands"]:
                if self._validate_single_command(cmd):
                    valid_commands.append(cmd)
                else:
                    logger.warning(f"Skipping invalid/unsafe custom command definition: {cmd}")

            self.commands = valid_commands
            logger.info(f"CustomCommandService loaded {len(self.commands)} valid custom commands.")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in custom commands file '{self.config_path}': {e}")
            self.commands = []
            return False
        except Exception as e:
            logger.error(f"Failed to load custom commands: {e}")
            self.commands = []
            return False

    def _validate_single_command(self, cmd: Any) -> bool:
        """Validates a single custom command definition for safety and schema correctness."""
        if not isinstance(cmd, dict):
            return False

        name = cmd.get("name")
        phrases = cmd.get("phrases")
        action_type = cmd.get("action_type")
        action_value = cmd.get("action_value")

        if not name or not isinstance(name, str):
            return False

        if not phrases or not isinstance(phrases, list) or not all(isinstance(p, str) for p in phrases):
            return False

        if not action_type or action_type not in self.ALLOWED_ACTION_TYPES:
            logger.warning(f"Rejected custom command '{name}': Action type '{action_type}' is not allowed for security reasons.")
            return False

        if not action_value or not isinstance(action_value, str):
            return False

        # Additional URL safety check if action_type is open_url
        if action_type == "open_url":
            if not (action_value.startswith("http://") or action_value.startswith("https://")):
                logger.warning(f"Rejected custom command '{name}': URL must start with http:// or https://")
                return False

        return True

    def match_and_execute(self, user_input: str) -> Tuple[bool, str]:
        """
        Checks if the input matches any configured custom command phrase.
        If matched, safely executes the action and returns (True, response_text).
        Otherwise returns (False, "").
        """
        if not user_input or not user_input.strip() or not self.commands:
            return False, ""

        clean_input = user_input.strip().lower()

        for cmd in self.commands:
            for phrase in cmd.get("phrases", []):
                if clean_input == phrase.strip().lower():
                    logger.info(f"Custom command matched: '{cmd['name']}' via phrase: '{phrase}'")
                    response_text = self._execute_safe_action(cmd["action_type"], cmd["action_value"], cmd["name"])
                    return True, response_text

        return False, ""

    def _execute_safe_action(self, action_type: str, action_value: str, command_name: str) -> str:
        """Executes predefined safe actions without eval/exec/subprocess."""
        if action_type == "open_url":
            try:
                webbrowser.open(action_value)
                return f"Opening custom URL for '{command_name}': {action_value}"
            except Exception as e:
                logger.error(f"Failed to open URL '{action_value}': {e}")
                return f"Sorry, I couldn't open the URL for '{command_name}'."

        elif action_type == "response":
            return action_value

        return ""
