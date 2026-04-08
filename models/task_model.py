from __future__ import annotations

"""
Task model definition for Smart Student Planner.

This module defines the TaskModel class, which represents a single
academic task in the application. It includes helper methods for
serializing and deserializing task data to/from dictionaries so that
it can be stored in JSON.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, Optional
import uuid


@dataclass
class TaskModel:
    """
    Represents a single academic task.

    Attributes:
        task_id: Unique identifier for the task.
        title: Title of the task (for example "Essay Draft").
        module: Academic module or course name.
        due_date: Due date as a date object.
        priority: Priority level ("Low", "Medium", or "High").
        notes: Optional notes or description.
        is_completed: Boolean flag indicating completion status.
    """

    title: str
    module: str
    due_date: date
    priority: str
    notes: str = ""
    is_completed: bool = False
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    DATE_FORMAT = "%Y-%m-%d"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the TaskModel instance into a dictionary suitable for JSON
        serialization.

        Returns:
            A dictionary containing all task fields.
        """
        return {
            "task_id": self.task_id,
            "title": self.title,
            "module": self.module,
            "due_date": self.due_date.strftime(self.DATE_FORMAT),
            "priority": self.priority,
            "notes": self.notes,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskModel":
        """
        Create a TaskModel instance from a dictionary.

        Args:
            data: Dictionary with keys matching the to_dict() output.

        Returns:
            A TaskModel instance.
        """
        due_date_str = data.get("due_date", "")
        due_date_obj = date.fromisoformat(due_date_str)

        return cls(
            task_id=data.get("task_id", uuid.uuid4().hex),
            title=data.get("title", ""),
            module=data.get("module", ""),
            due_date=due_date_obj,
            priority=data.get("priority", "Medium"),
            notes=data.get("notes", ""),
            is_completed=bool(data.get("is_completed", False)),
        )

    @staticmethod
    def generate_id() -> str:
        """
        Generate a new unique task identifier.

        Returns:
            A unique hexadecimal string.
        """
        return uuid.uuid4().hex

    @staticmethod
    def safe_get(tasks: Dict[str, "TaskModel"], task_id: str) -> Optional["TaskModel"]:
        """
        Safely retrieve a task from a mapping by id.

        Args:
            tasks: Dictionary mapping task_id to TaskModel.
            task_id: ID of the task to retrieve.

        Returns:
            TaskModel if found, otherwise None.
        """
        return tasks.get(task_id)

