from __future__ import annotations

"""
Login screen for Smart Student Planner.

This screen provides a simple username/password form. For this
coursework, we use a basic hard-coded check rather than a database.
"""

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

    # Hard-coded credentials for demonstration.
    VALID_USERNAME = "student"
    VALID_PASSWORD = "password"

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

        if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            self.error_message = ""
            app: App = App.get_running_app()
            if app is not None:
                app.root.current = "dashboard"
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

