from __future__ import annotations

"""
Add/edit task screen for Smart Student Planner.

This screen is used to create new tasks or edit existing ones.
It validates user input and persists changes via the DataManager.
"""

import os
import uuid
from datetime import date
from typing import Tuple

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
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
    image_path = StringProperty("")

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
        self.image_path = ""
        if "image_path_label" in ids:
            ids.image_path_label.text = "No image selected"

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
        self.image_path = task.image_path
        if "image_path_label" in ids:
            ids.image_path_label.text = task.image_path or "No image selected"

    def _validate_form(self, title: str, module: str, due_date_str: str, priority: str) -> Tuple[bool, str]:
        """
        Validate all form fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        ok, msg = validate_non_empty(title, "Title")
        if not ok:
            return False, msg

        ok, msg = validate_non_empty(module, "Module")
        if not ok:
            return False, msg

        ok, msg = validate_date(due_date_str)
        if not ok:
            return False, msg

        ok, msg = validate_priority(priority)
        if not ok:
            return False, msg

        return True, ""

    def _create_task_from_data(self, title: str, module: str, due_date_obj: date, priority: str, notes: str, is_completed: bool) -> TaskModel:
        """
        Create a TaskModel instance from form data.
        """
        return TaskModel(
            title=title,
            module=module,
            due_date=due_date_obj,
            priority=priority,
            notes=notes,
            image_path=self.image_path,
            is_completed=is_completed,
        )

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

        ok, msg = self._validate_form(title, module, due_date_str, priority)
        if not ok:
            self.error_message = msg
            return

        due_date_obj = date.fromisoformat(due_date_str)

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
                image_path=self.image_path,
                is_completed=is_completed,
            )
            self.data_manager.update_task(existing.task_id, updated_task)
        else:
            new_task = self._create_task_from_data(
                title, module, due_date_obj, priority, notes, is_completed
            )
            self.data_manager.add_task(new_task)

        app = App.get_running_app()
        dashboard = app.root.get_screen("dashboard")  # type: ignore[attr-defined]
        dashboard.refresh_tasks()
        app.root.current = "dashboard"  # type: ignore[attr-defined]

    def save_task(self, *args, **kwargs) -> None:
        """Alias for submit_form used by older kv bindings."""
        self.submit_form()

    def _update_image_label(self) -> None:
        ids = self.ids
        if "image_path_label" in ids:
            ids.image_path_label.text = self.image_path or "No image selected"

    def open_image_picker(self) -> None:
        """Open a file chooser popup to select an image."""
        chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"], path=os.getcwd())
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        content.add_widget(chooser)

        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel_btn = Button(text="Cancel")
        select_btn = Button(text="Select")
        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        content.add_widget(buttons)

        popup = Popup(title="Upload Image", content=content, size_hint=(0.9, 0.9), auto_dismiss=False)
        cancel_btn.bind(on_release=popup.dismiss)
        select_btn.bind(on_release=lambda instance: self._pick_image(chooser.selection, popup))
        popup.open()

    def _pick_image(self, selection: list[str], popup: Popup) -> None:
        if not selection:
            self.error_message = "Please select an image file."
            return
        self.image_path = selection[0]
        self._update_image_label()
        self.error_message = ""
        popup.dismiss()

    def open_camera(self) -> None:
        """Open a camera popup for taking a new photo."""
        try:
            camera = Camera(play=True, resolution=(640, 480), index=0)
        except Exception:
            self.error_message = "Camera access is unavailable on this device."
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        content.add_widget(camera)

        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        cancel_btn = Button(text="Cancel")
        capture_btn = Button(text="Capture")
        buttons.add_widget(cancel_btn)
        buttons.add_widget(capture_btn)
        content.add_widget(buttons)

        popup = Popup(title="Camera", content=content, size_hint=(0.9, 0.9), auto_dismiss=False)
        cancel_btn.bind(on_release=lambda *_: popup.dismiss())
        capture_btn.bind(on_release=lambda *_: self._capture_image(camera, popup))
        popup.open()

    def _capture_image(self, camera: Camera, popup: Popup) -> None:
        if not camera.texture:
            self.error_message = "Camera is not available." 
            return

        images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "images")
        os.makedirs(images_dir, exist_ok=True)
        file_name = f"img_{uuid.uuid4().hex}.png"
        image_path = os.path.join(images_dir, file_name)
        try:
            camera.export_to_png(image_path)
        except Exception:
            self.error_message = "Failed to save camera image."
            return

        self.image_path = image_path
        self._update_image_label()
        self.error_message = ""
        popup.dismiss()

    def cancel(self) -> None:
        """
        Cancel the operation and return to the dashboard without saving.
        """
        app: App = App.get_running_app()
        app.root.current = "dashboard"  # type: ignore[attr-defined]
