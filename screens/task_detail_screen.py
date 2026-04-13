from __future__ import annotations

"""
Task detail screen for Smart Student Planner.

This screen displays the full details of a single task and provides
options to mark it complete/incomplete, edit it, or delete it.
"""

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen

from models.task_model import TaskModel
from storage.data_manager import DataManager


class TaskDetailScreen(Screen):
    """
    Screen that shows details of a single task.
    """

    task_id = StringProperty("")
    title_text = StringProperty("")
    module_text = StringProperty("")
    due_date_text = StringProperty("")
    priority_text = StringProperty("")
    notes_text = StringProperty("")
    is_completed = BooleanProperty(False)
    info_message = StringProperty("")

    @property
    def data_manager(self) -> DataManager:
        """Shortcut to access the shared DataManager."""
        app: App = App.get_running_app()
        return app.data_manager  # type: ignore[attr-defined]

    def load_task(self, task_id: str) -> None:
        """
        Load a task from the DataManager into the screen properties.
        """
        self.task_id = task_id
        task = self.data_manager.get_task(task_id)
        if task is None:
            self.info_message = "Task not found."
            app: App = App.get_running_app()
            app.root.current = "dashboard"  # type: ignore[attr-defined]
            return

        self._update_from_task(task)
        self.info_message = ""

    def _update_from_task(self, task: TaskModel) -> None:
        """
        Update the screen properties from a TaskModel instance.
        """
        self.title_text = task.title
        self.module_text = task.module
        self.due_date_text = task.due_date.strftime(task.DATE_FORMAT)
        self.priority_text = task.priority
        self.notes_text = task.notes or "(No notes)"
        self.is_completed = task.is_completed

    def toggle_completion(self) -> None:
        """
        Toggle the completed status of the task.
        """
        if not self.task_id:
            return

        new_status = not self.is_completed
        self.data_manager.set_task_completion(self.task_id, new_status)

        task = self.data_manager.get_task(self.task_id)
        if task is not None:
            self._update_from_task(task)

    def delete_task(self) -> None:
        """
        Delete the current task and return to the dashboard.
        """
        if not self.task_id:
            return

        self.data_manager.delete_task(self.task_id)
        app: App = App.get_running_app()
        dashboard = app.root.get_screen("dashboard")  # type: ignore[attr-defined]
        dashboard.refresh_tasks()
        app.root.current = "dashboard"  # type: ignore[attr-defined]

    def open_edit(self) -> None:
        """
        Open the AddTaskScreen in edit mode for this task.
        """
        if not self.task_id:
            return

        app: App = App.get_running_app()
        add_screen = app.root.get_screen("add_task")  # type: ignore[attr-defined]
        add_screen.set_mode_edit(self.task_id)
        app.root.current = "add_task"  # type: ignore[attr-defined]

    def back_to_dashboard(self) -> None:
        """
        Navigate back to the dashboard without changing anything.
        """
        app: App = App.get_running_app()
        app.root.current = "dashboard"  # type: ignore[attr-defined]

