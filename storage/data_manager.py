from __future__ import annotations

"""
Data manager for Smart Student Planner.

This module is responsible for loading and saving task data to a local
JSON file, and provides CRUD operations for tasks. It acts as a simple
in-memory store with persistence.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from models.task_model import TaskModel


class DataManager:
    """
    Manages loading, saving, and manipulating tasks.

    Tasks are stored in-memory as a dict of task_id -> TaskModel,
    and persisted to disk as JSON.
    """

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        """
        Initialize the DataManager.

        Args:
            storage_dir: Optional directory where the JSON file is stored.
                If None, uses a 'storage' folder relative to this file.
        """
        if storage_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_dir = os.path.join(base_dir, "storage")

        self.storage_dir = storage_dir
        self.storage_file = os.path.join(self.storage_dir, "tasks.json")
        # mapping username -> (task_id -> TaskModel)
        self._users_tasks: Dict[str, Dict[str, TaskModel]] = {}
        # current logged-in username
        self.current_user: Optional[str] = None
        # simple users store: username -> password_hash
        self.users: Dict[str, str] = {}

        # Ensure the storage directory exists.
        os.makedirs(self.storage_dir, exist_ok=True)

        # Load existing tasks from disk if any.
        self.load_tasks()

    def load_tasks(self) -> None:
        """
        Load tasks from the JSON file into memory.

        If the file does not exist or cannot be read, the task list
        will simply remain empty.
        """
        if not os.path.exists(self.storage_file):
            self._users_tasks = {}
            return

        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            self.tasks = {}
            self.users = {}
            return

        # new format: users_tasks is a mapping username->list-of-task-dicts
        self._users_tasks = {}
        if "users_tasks" in data:
            for username, items in data.get("users_tasks", {}).items():
                user_tasks: Dict[str, TaskModel] = {}
                for item in items:
                    try:
                        task = TaskModel.from_dict(item)
                        user_tasks[task.task_id] = task
                    except Exception:
                        continue
                self._users_tasks[username] = user_tasks
        else:
            # legacy format: single tasks list -> put under a default user
            loaded_tasks: Dict[str, TaskModel] = {}
            for item in data.get("tasks", []):
                try:
                    task = TaskModel.from_dict(item)
                    loaded_tasks[task.task_id] = task
                except Exception:
                    continue
            if loaded_tasks:
                self._users_tasks["default"] = loaded_tasks

        # load users (simple dict username->hash)
        self.users = data.get("users", {}) or {}

    def save_tasks(self) -> None:
        """
        Save the current tasks to the JSON file.

        The data is stored as a dict with a 'tasks' list so that the
        format can be extended in the future if needed.
        """
        # serialize per-user task lists
        users_tasks_serialized = {
            username: [task.to_dict() for task in tasks.values()]
            for username, tasks in self._users_tasks.items()
        }

        serialized = {
            "last_saved": datetime.now().isoformat(timespec="seconds"),
            "users_tasks": users_tasks_serialized,
            "users": self.users,
        }

        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(serialized, file, indent=4)
        except OSError:
            # For coursework we fail silently to avoid crashing.
            pass

    def _get_user_tasks(self) -> Dict[str, TaskModel]:
        """Return the current user's task dictionary, or an empty dict."""
        return self._users_tasks.get(self.current_user, {}) if self.current_user else {}

    def get_all_tasks(self) -> List[TaskModel]:
        """
        Get all tasks sorted by due date.

        Returns:
            A list of TaskModel instances.
        """
        if not self.current_user:
            return []
        tasks = self._get_user_tasks()
        return sorted(tasks.values(), key=lambda task: task.due_date)

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """
        Retrieve a single task by its ID.

        Args:
            task_id: Unique identifier.

        Returns:
            TaskModel if found, otherwise None.
        """
        if not self.current_user:
            return None
        return self._get_user_tasks().get(task_id)

    def add_task(self, task: TaskModel) -> None:
        """
        Add a new task and persist changes.

        Args:
            task: The TaskModel instance to add.
        """
        if not self.current_user:
            return
        user_tasks = self._users_tasks.setdefault(self.current_user, {})
        user_tasks[task.task_id] = task
        self.save_tasks()

    def update_task(self, task_id: str, updated_task: TaskModel) -> None:
        """
        Replace an existing task with an updated version.

        Args:
            task_id: ID of the task to update.
            updated_task: New TaskModel instance.
        """
        if not self.current_user:
            return
        user_tasks = self._users_tasks.get(self.current_user, {})
        if task_id in user_tasks:
            user_tasks[task_id] = updated_task
            self.save_tasks()

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task by ID and persist changes.

        Args:
            task_id: ID of the task to delete.
        """
        if not self.current_user:
            return
        user_tasks = self._users_tasks.get(self.current_user, {})
        if task_id in user_tasks:
            del user_tasks[task_id]
            self.save_tasks()

    # -----------------
    # Per-user helpers
    # -----------------
    def _migrate_default_tasks_to_user(self, username: str) -> None:
        """Migrate legacy default tasks into the newly active user's account."""
        if "default" not in self._users_tasks:
            return
        if self._users_tasks.get(username):
            return

        self._users_tasks[username] = {
            task_id: task
            for task_id, task in self._users_tasks["default"].items()
        }
        del self._users_tasks["default"]
        self.save_tasks()

    def set_current_user(self, username: Optional[str]) -> None:
        """Set the currently active username for subsequent operations."""
        self.current_user = username
        if username:
            self._migrate_default_tasks_to_user(username)

    # -----------------
    # User management
    # -----------------
    def _hash_password(self, password: str) -> str:
        """Return a SHA-256 hex digest for the given password."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def user_exists(self, username: str) -> bool:
        """Return True if a user with `username` exists."""
        return username in self.users

    def add_user(self, username: str, password: str) -> bool:
        """Add a new user. Returns False if user exists, True on success."""
        if not username:
            return False
        if self.user_exists(username):
            return False
        self.users[username] = self._hash_password(password)
        self.save_tasks()
        return True

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate username/password against stored hash."""
        if not username or username not in self.users:
            return False
        return self.users[username] == self._hash_password(password)

    def search_tasks(self, query: str) -> List[TaskModel]:
        """
        Search for tasks whose title or module name contains the query.

        Args:
            query: Search text (case-insensitive).

        Returns:
            List of tasks matching the query.
        """
        if not query:
            return self.get_all_tasks()

        query_lower = query.lower()
        return [
            task
            for task in self.get_all_tasks()
            if query_lower in task.title.lower()
            or query_lower in task.module.lower()
        ]

    def set_task_completion(self, task_id: str, is_completed: bool) -> None:
        """
        Mark a task as complete or incomplete.

        Args:
            task_id: ID of the task.
            is_completed: New completion status.
        """
        if not self.current_user:
            return

        task = self._get_user_tasks().get(task_id)
        if task is None:
            return

        task.is_completed = is_completed
        self.save_tasks()

