"""
Tests for Jubilant Train Project Manager

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import pytest
import tempfile
from pathlib import Path

from jubilant_train.manager import Task, Project, ProjectManager


class TestTask:
    """Test Task class."""

    def test_task_creation(self):
        """Test task creation."""
        task = Task("task1", "Test Task", "A test task")
        assert task.task_id == "task1"
        assert task.title == "Test Task"
        assert task.status == "pending"

    def test_task_start_complete(self):
        """Test task state transitions."""
        task = Task("task1", "Test Task")
        task.start()
        assert task.status == "in_progress"
        assert task.started_at is not None

        task.complete()
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_task_fail(self):
        """Test task failure."""
        task = Task("task1", "Test Task")
        task.start()
        task.fail("Test error")
        assert task.status == "failed"
        assert task.error == "Test error"

    def test_task_retry(self):
        """Test task retry."""
        task = Task("task1", "Test Task")
        task.fail("Error")
        assert task.can_retry() is True

        task.retry()
        assert task.status == "pending"
        assert task.retry_count == 1

    def test_task_max_retries(self):
        """Test max retries limit."""
        task = Task("task1", "Test Task")
        task.max_retries = 2

        for _ in range(2):
            task.fail("Error")
            task.retry()

        assert task.retry_count == 2
        assert task.can_retry() is False


class TestProject:
    """Test Project class."""

    def test_project_creation(self):
        """Test project creation."""
        project = Project("proj1", "Test Project", "A test project")
        assert project.project_id == "proj1"
        assert project.name == "Test Project"
        assert project.status == "active"

    def test_add_task(self):
        """Test adding tasks to project."""
        project = Project("proj1", "Test Project")
        task = Task("task1", "Task 1")
        project.add_task(task)
        assert project.get_task("task1") is not None

    def test_get_available_tasks(self):
        """Test getting available tasks."""
        project = Project("proj1", "Test Project")
        task1 = Task("task1", "Task 1")
        task2 = Task("task2", "Task 2", depends_on=["task1"])

        project.add_task(task1)
        project.add_task(task2)

        available = project.get_next_available_tasks()
        assert len(available) == 1
        assert available[0].task_id == "task1"

        # Complete task1
        task1.complete()
        available = project.get_next_available_tasks()
        assert len(available) == 1
        assert available[0].task_id == "task2"

    def test_checkpoint_creation(self):
        """Test checkpoint creation."""
        project = Project("proj1", "Test Project")
        task = Task("task1", "Task 1")
        project.add_task(task)

        checkpoint = project.create_checkpoint("test_checkpoint")
        assert checkpoint["label"] == "test_checkpoint"
        assert len(project.checkpoints) == 1

    def test_restore_from_checkpoint(self):
        """Test checkpoint restoration."""
        project = Project("proj1", "Test Project")
        task = Task("task1", "Task 1")
        project.add_task(task)

        # Complete the task
        task.complete()
        checkpoint = project.create_checkpoint()
        assert task.status == "completed"

        # Revert status
        task.status = "pending"
        assert task.status == "pending"

        # Restore from checkpoint
        project.restore_from_checkpoint(0)
        assert task.status == "completed"

    def test_project_status(self):
        """Test project status reporting."""
        project = Project("proj1", "Test Project")
        task1 = Task("task1", "Task 1")
        task2 = Task("task2", "Task 2")

        project.add_task(task1)
        project.add_task(task2)

        status = project.get_status()
        assert status["total_tasks"] == 2
        assert status["pending"] == 2
        assert status["completed"] == 0

        task1.complete()
        status = project.get_status()
        assert status["completed"] == 1
        assert status["progress_percent"] == 50


class TestProjectManager:
    """Test ProjectManager class."""

    def test_create_project(self):
        """Test project creation via manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(tmpdir)
            project = manager.create_project("proj1", "Test Project")
            assert manager.get_project("proj1") is not None

    def test_save_and_load_project(self):
        """Test project persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager1 = ProjectManager(tmpdir)
            project = manager1.create_project("proj1", "Test Project")
            task = Task("task1", "Task 1")
            project.add_task(task)
            task.complete()
            manager1.save_project(project)

            # Create new manager and load projects
            manager2 = ProjectManager(tmpdir)
            loaded_project = manager2.get_project("proj1")
            assert loaded_project is not None
            assert loaded_project.get_task("task1").status == "completed"

    def test_moprotect_status(self):
        """Test MoProtect protocol step tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(tmpdir)
            project = manager.create_project("proj1", "Test Project", moprotect_protocol=True)

            # Add tasks for each MoProtect step
            for step in ["disclosure", "sanitization", "human_assertion", "sealing"]:
                task = Task(f"task_{step}", f"Task {step}", moprotect_step=step)
                project.add_task(task)

            status_report = manager.generate_status_report("proj1")
            moprotect_status = status_report["moprotect_steps_status"]

            assert "disclosure" in moprotect_status
            assert "sanitization" in moprotect_status
            assert "human_assertion" in moprotect_status
            assert "sealing" in moprotect_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
