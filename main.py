from __future__ import annotations

"""
Main entry point for the Smart Student Planner application.

This module initializes the Kivy App, sets up the ScreenManager, and
exposes a shared DataManager instance that all screens can access.

Run this file to start the application:
    python main.py
"""

import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from storage.data_manager import DataManager
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.add_task_screen import AddTaskScreen
from screens.task_detail_screen import TaskDetailScreen


class PlannerScreenManager(ScreenManager):
    """
    Custom ScreenManager for Smart Student Planner.

    The actual screen instances are created via the .kv file.
    """

    pass


class SmartStudentPlannerApp(App):
    """
    Main Kivy application class.

    Attributes:
        data_manager: Shared DataManager instance used for all task
            operations and persistence.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data_manager: DataManager = DataManager()

    def build(self):
        """
        Build and return the root widget.

        We load the .kv file, which defines the visual layout and
        registers the screens.
        """
        kv_path = os.path.join(os.path.dirname(__file__), "kv", "planner.kv")
        Builder.load_file(kv_path)

        # The root widget is defined as PlannerScreenManager in the .kv file.
        return PlannerScreenManager()

    def open_delete_confirmation(self, task_detail_screen: TaskDetailScreen) -> None:
        """
        Open a simple confirmation popup before deleting a task.

        Args:
            task_detail_screen: The TaskDetailScreen instance that
                initiated the delete.
        """
        from kivy.factory import Factory

        popup = Factory.DeleteConfirmPopup()
        # Attach the calling TaskDetailScreen so the popup can call delete_task().
        popup.parent_task_detail = task_detail_screen
        popup.open()


if __name__ == "__main__":
    SmartStudentPlannerApp().run()

