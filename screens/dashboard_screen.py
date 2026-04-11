from __future__ import annotations

"""
Dashboard (home) screen for Smart Student Planner.

This screen displays the list of tasks, allows filtering by search
query, and provides buttons for adding tasks, opening details, and
logging out.
"""

from typing import List

from kivy.app import App
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from models.task_model import TaskModel
from storage.data_manager import DataManager


class TaskListItem(Button):
    """
    Reusable task row widget used on the dashboard.

    This is implemented as a Python class (instead of KV-only) so it has
    proper Kivy properties/callbacks that the KV layout can safely bind to.
    """

    task_id = StringProperty("")
    title = StringProperty("")
    module = StringProperty("")
    due_date = StringProperty("")
    priority = StringProperty("")
    is_completed = BooleanProperty(False)

    # Callback invoked when the user taps the row.
    open_detail_callback = ObjectProperty(None, allownone=True)


class DashboardScreen(Screen):
    """
    Dashboard screen showing all tasks.

    The screen interacts with the DataManager to retrieve and filter
    tasks, and provides handler methods used by the .kv UI.
    """

    search_query = StringProperty("")

    def on_pre_enter(self, *args) -> None:
        """
        Called by Kivy just before the screen becomes visible.
        """
        super().on_pre_enter(*args)
        self.refresh_tasks()

    @property
    def data_manager(self) -> DataManager:
        """
        Convenience property to access the shared DataManager instance.
        """
        app: App = App.get_running_app()
        return app.data_manager  # type: ignore[attr-defined]

    def refresh_tasks(self) -> None:
        """
        Refresh the list of tasks from the DataManager, applying any
        active search query and updating the visible list.
        """
        tasks: List[TaskModel] = self.data_manager.search_tasks(self.search_query)
        container = self.ids.get("tasks_container")
        if container is None:
            return

        container.clear_widgets()

        # Build one TaskListItem widget per task using the Kivy template.
        for task in tasks:
            item = TaskListItem()
            item.task_id = task.task_id
            item.title = task.title
            item.module = task.module
            item.due_date = task.due_date.strftime(task.DATE_FORMAT)
            item.priority = task.priority
            item.is_completed = task.is_completed
            item.open_detail_callback = self.open_task_detail
            container.add_widget(item)

    def on_search_query(self, instance, value: str) -> None:
        """
        Kivy callback when the search_query property changes.
        """
        del instance  # unused
        self.search_query = value
        self.refresh_tasks()

    def open_add_task(self) -> None:
        """
        Navigate to the AddTask screen in 'add' mode.
        """
        app: App = App.get_running_app()
        add_screen = app.root.get_screen("add_task")  # type: ignore[attr-defined]
        add_screen.set_mode_add()
        app.root.current = "add_task"  # type: ignore[attr-defined]

    def open_task_detail(self, task_id: str) -> None:
        """
        Navigate to the TaskDetail screen for a specific task.
        """
        app: App = App.get_running_app()
        detail_screen = app.root.get_screen("task_detail")  # type: ignore[attr-defined]
        detail_screen.load_task(task_id)
        app.root.current = "task_detail"  # type: ignore[attr-defined]

    def logout(self) -> None:
        """
        Navigate back to the login screen and reset its fields.
        """
        app: App = App.get_running_app()
        login_screen = app.root.get_screen("login")  # type: ignore[attr-defined]
        login_screen.reset_fields()
        app.root.current = "login"  # type: ignore[attr-defined]

