from __future__ import annotations

"""
Add/edit task screen for Smart Student Planner.

This screen is used to create new tasks or edit existing ones.
It validates user input and persists changes via the DataManager.
"""

from datetime import datetime

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen

from models.task_model import TaskModel
from storage.data_manager import DataManager
from utils.validators import validate_date, validate_non_empty, validate_priority


class AddTaskScreen(Screen):
    """
    Screen for adding or editing a task.

    The screen has two modes:
        - Add mode: create a new task.
        - Edit mode: update an existing task.
    """

    error_message = StringProperty("")
    is_edit_mode = BooleanProperty(False)
    editing_task_id = StringProperty("")

    def on_pre_enter(self, *args) -> None:
        """
        Prepare the screen just before it becomes visible.
        """
        super().on_pre_enter(*args)
        self.error_message = ""

    @property
    def data_manager(self) -> DataManager:
        """Shortcut to access the shared DataManager."""
        app: App = App.get_running_app()
        return app.data_manager  # type: ignore[attr-defined]

    def set_mode_add(self) -> None:
        """
        Configure the screen for adding a new task.
        """
        self.is_edit_mode = False
        self.editing_task_id = ""
        self.error_message = ""
        self._clear_form()

    def set_mode_edit(self, task_id: str) -> None:
        """
        Configure the screen for editing an existing task.
        """
        self.is_edit_mode = True
        self.editing_task_id = task_id
        self.error_message = ""
        self._populate_form_from_task()

    def _clear_form(self) -> None:
        """Clear all form fields."""
        ids = self.ids
        ids.title_input.text = ""
        ids.module_input.text = ""
        ids.due_date_input.text = ""
        ids.notes_input.text = ""
        ids.priority_spinner.text = "Medium"
        ids.completed_checkbox.active = False

    def _populate_form_from_task(self) -> None:
        """
        Load task data into the form for editing.
        """
        task = self.data_manager.get_task(self.editing_task_id)
        if task is None:
            self.set_mode_add()
            return

        ids = self.ids
        ids.title_input.text = task.title
        ids.module_input.text = task.module
        ids.due_date_input.text = task.due_date.strftime(task.DATE_FORMAT)
        ids.notes_input.text = task.notes
        ids.priority_spinner.text = task.priority
        ids.completed_checkbox.active = task.is_completed

    def submit_form(self) -> None:
        """
        Validate form data and create or update a task accordingly.
        """
        ids = self.ids
        title = ids.title_input.text
        module = ids.module_input.text
        due_date_str = ids.due_date_input.text
        priority = ids.priority_spinner.text
        notes = ids.notes_input.text
        is_completed = ids.completed_checkbox.active

        ok, msg = validate_non_empty(title, "Title")
        if not ok:
            self.error_message = msg
            return

        ok, msg = validate_non_empty(module, "Module")
        if not ok:
            self.error_message = msg
            return

        ok, msg = validate_date(due_date_str)
        if not ok:
            self.error_message = msg
            return

        ok, msg = validate_priority(priority)
        if not ok:
            self.error_message = msg
            return

        due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()

        if self.is_edit_mode:
            existing = self.data_manager.get_task(self.editing_task_id)
            if existing is None:
                self.error_message = "Task no longer exists."
                return

            updated_task = TaskModel(
                task_id=existing.task_id,
                title=title,
                module=module,
                due_date=due_date_obj,
                priority=priority,
                notes=notes,
                is_completed=is_completed,
            )
            self.data_manager.update_task(existing.task_id, updated_task)
        else:
            new_task = TaskModel(
                title=title,
                module=module,
                due_date=due_date_obj,
                priority=priority,
                notes=notes,
                is_completed=is_completed,
            )
            self.data_manager.add_task(new_task)

        app: App = App.get_running_app()
        dashboard = app.root.get_screen("dashboard")  # type: ignore[attr-defined]
        dashboard.refresh_tasks()
        app.root.current = "dashboard"  # type: ignore[attr-defined]

    def cancel(self) -> None:
        """
        Cancel the operation and return to the dashboard without saving.
        """
        app: App = App.get_running_app()
        app.root.current = "dashboard"  # type: ignore[attr-defined]

