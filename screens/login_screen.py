from __future__ import annotations

"""
Login screen for Smart Student Planner.

This screen provides a simple username/password form. For this
coursework, we use a basic hard-coded check rather than a database.
"""

import re
from typing import Optional

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class LoginScreen(Screen):
    """
    Login screen for the application.

    Username and password are checked against simple hard-coded values.
    In a real application, you would replace this with a proper
    authentication system.
    """

    error_message = StringProperty("")

    # Note: authentication is now backed by the shared DataManager.

    def clear_error(self) -> None:
        """Clear any existing error message."""
        self.error_message = ""

    def attempt_login(self, username: str, password: str) -> None:
        """
        Validate inputs and, if successful, navigate to the dashboard.

        Args:
            username: Entered username.
            password: Entered password.
        """
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            self.error_message = "Username and password are required."
            return
        
        if len(password) < 8:
            self.error_message = "Password must be at least 8 characters."
            return
        if not re.search(r'[A-Z]', password):
            self.error_message = "Password must contain at least one uppercase letter."
            return
        if not re.search(r'[a-z]', password):
            self.error_message = "Password must contain at least one lowercase letter."
            return
        if not re.search(r'[0-9]', password):
            self.error_message = "Password must contain at least one digit."
            return
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.error_message = "Password must contain at least one special character."
            return

        # authenticate via DataManager
        app: App = App.get_running_app()
        if app is None:
            self.error_message = "Internal error: app not available."
            return

        dm = app.data_manager
        if dm.authenticate_user(username, password):
            # set the active user
            dm.set_current_user(username)
            self.error_message = ""
            app.root.current = "dashboard"  # type: ignore[attr-defined]
        else:
            self.error_message = "Invalid username or password."

    def reset_fields(self) -> None:
        """
        Clear input fields and error message. This is called when the user
        logs out and comes back to the login screen.
        """
        self.error_message = ""
        if "username_input" in self.ids:
            self.ids.username_input.text = ""
        if "password_input" in self.ids:
            self.ids.password_input.text = ""
        # also clear create user popup fields if present
        if "create_username_input" in self.ids:
            self.ids.create_username_input.text = ""
        if "create_password_input" in self.ids:
            self.ids.create_password_input.text = ""
        if "create_password_confirm_input" in self.ids:
            self.ids.create_password_confirm_input.text = ""

    def _validate_password_strength(self, password: str) -> Optional[str]:
        """Return None if ok, otherwise an error message."""
        if len(password) < 8:
            return "Password must be at least 8 characters."
        if not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r'[0-9]', password):
            return "Password must contain at least one digit."
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return "Password must contain at least one special character."
        return None

    def create_user(self, username: str, password: str, confirm: str) -> None:
        """Create a new user via DataManager and show error messages on failure."""
        username = (username or "").strip()
        password = (password or "").strip()
        confirm = (confirm or "").strip()

        if not username or not password or not confirm:
            self.error_message = "All fields are required to create an account."
            return
        if password != confirm:
            self.error_message = "Passwords do not match."
            return

        # password strength
        pw_err = self._validate_password_strength(password)
        if pw_err:
            self.error_message = pw_err
            return

        app = App.get_running_app()
        if app is None:
            self.error_message = "Internal error: app not available."
            return

        dm = app.data_manager
        if dm.user_exists(username):
            self.error_message = "User already exists. Choose a different username."
            return

        ok = dm.add_user(username, password)
        if not ok:
            self.error_message = "Failed to create user."
            return

        # success - clear the popup fields and auto-login
        dm.set_current_user(username)
        self.error_message = ""
        app.root.current = "dashboard"  # type: ignore[attr-defined]

