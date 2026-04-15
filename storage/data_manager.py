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
        self.tasks: Dict[str, TaskModel] = {}

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
            self.tasks = {}
            return

        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            self.tasks = {}
            return

        loaded_tasks: Dict[str, TaskModel] = {}
        for item in data.get("tasks", []):
            try:
                task = TaskModel.from_dict(item)
                loaded_tasks[task.task_id] = task
            except Exception:
                # Skip invalid entries rather than crashing the app.
                continue

        self.tasks = loaded_tasks

    def save_tasks(self) -> None:
        """
        Save the current tasks to the JSON file.

        The data is stored as a dict with a 'tasks' list so that the
        format can be extended in the future if needed.
        """
        serialized = {
            "last_saved": datetime.now().isoformat(timespec="seconds"),
            "tasks": [task.to_dict() for task in self.tasks.values()],
        }

        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(serialized, file, indent=4)
        except OSError:
            # For coursework we fail silently to avoid crashing.
            pass

    def get_all_tasks(self) -> List[TaskModel]:
        """
        Get all tasks sorted by due date.

        Returns:
            A list of TaskModel instances.
        """
        return sorted(self.tasks.values(), key=lambda task: task.due_date)

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """
        Retrieve a single task by its ID.

        Args:
            task_id: Unique identifier.

        Returns:
            TaskModel if found, otherwise None.
        """
        return self.tasks.get(task_id)

    def add_task(self, task: TaskModel) -> None:
        """
        Add a new task and persist changes.

        Args:
            task: The TaskModel instance to add.
        """
        self.tasks[task.task_id] = task
        self.save_tasks()

    def update_task(self, task_id: str, updated_task: TaskModel) -> None:
        """
        Replace an existing task with an updated version.

        Args:
            task_id: ID of the task to update.
            updated_task: New TaskModel instance.
        """
        if task_id in self.tasks:
            self.tasks[task_id] = updated_task
            self.save_tasks()

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task by ID and persist changes.

        Args:
            task_id: ID of the task to delete.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()

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
        task = self.tasks.get(task_id)
        if task is None:
            return

        task.is_completed = is_completed
        self.save_tasks()

