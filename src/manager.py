"""
ProjectManager - Self-Management System for Jubilant Train

Implements project and task management with:
- Workflow state tracking
- Progress monitoring
- Self-healing and recovery
- Checkpoint management
- Status reporting

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Literal
from datetime import datetime
import hashlib
import pickle

logger = logging.getLogger(__name__)


class Task:
    """Represents a single task in a project."""

    STATUS_ENUM = Literal["pending", "in_progress", "completed", "failed", "blocked"]

    def __init__(
        self,
        task_id: str,
        title: str,
        description: str = "",
        depends_on: Optional[List[str]] = None,
        moprotect_step: Optional[str] = None,
    ):
        """Initialize a task."""
        self.task_id = task_id
        self.title = title
        self.description = description
        self.depends_on = depends_on or []
        self.moprotect_step = moprotect_step
        self.status: Task.STATUS_ENUM = "pending"
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.error: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3

    def start(self) -> None:
        """Mark task as in progress."""
        self.status = "in_progress"
        self.started_at = datetime.now().isoformat()
        logger.info(f"Task started: {self.task_id} - {self.title}")

    def complete(self) -> None:
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        logger.info(f"Task completed: {self.task_id} - {self.title}")

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.now().isoformat()
        logger.error(f"Task failed: {self.task_id} - {error}")

    def block(self, reason: str) -> None:
        """Mark task as blocked."""
        self.status = "blocked"
        self.error = reason
        logger.warning(f"Task blocked: {self.task_id} - {reason}")

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries and self.status == "failed"

    def retry(self) -> None:
        """Attempt to retry a failed task."""
        if self.can_retry():
            self.retry_count += 1
            self.status = "pending"
            self.started_at = None
            self.completed_at = None
            self.error = None
            logger.info(f"Task retry {self.retry_count}: {self.task_id}")
        else:
            logger.error(f"Cannot retry task: {self.task_id} (max retries reached)")

    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "moprotect_step": self.moprotect_step,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "retry_count": self.retry_count,
            "depends_on": self.depends_on,
        }


class Project:
    """Represents a project with multiple tasks."""

    def __init__(
        self,
        project_id: str,
        name: str,
        description: str = "",
        moprotect_protocol: bool = True,
    ):
        """Initialize a project."""
        self.project_id = project_id
        self.name = name
        self.description = description
        self.moprotect_protocol = moprotect_protocol
        self.created_at = datetime.now().isoformat()
        self.tasks: Dict[str, Task] = {}
        self.checkpoints: List[Dict] = []
        self.status = "active"
        self.metadata: Dict = {}

    def add_task(self, task: Task) -> None:
        """Add a task to the project."""
        self.tasks[task.task_id] = task
        logger.info(f"Task added to project: {task.task_id}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self.tasks.get(task_id)

    def get_next_available_tasks(self) -> List[Task]:
        """
        Get tasks that are ready to run (dependencies met, status pending).

        Returns:
            List of available tasks
        """
        available = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue

            # Check if dependencies are met
            deps_met = all(
                self.tasks[dep_id].status == "completed"
                for dep_id in task.depends_on
                if dep_id in self.tasks
            )

            if deps_met:
                available.append(task)

        return available

    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks blocked by failed dependencies."""
        blocked = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue

            for dep_id in task.depends_on:
                if dep_id in self.tasks and self.tasks[dep_id].status == "failed":
                    blocked.append(task)
                    break

        return blocked

    def create_checkpoint(self, label: str = "") -> Dict:
        """
        Create a project checkpoint for recovery.

        Args:
            label: Optional checkpoint label

        Returns:
            Checkpoint dictionary
        """
        checkpoint = {
            "checkpoint_id": len(self.checkpoints),
            "label": label or f"checkpoint_{len(self.checkpoints)}",
            "timestamp": datetime.now().isoformat(),
            "tasks_completed": sum(
                1 for t in self.tasks.values() if t.status == "completed"
            ),
            "tasks_failed": sum(
                1 for t in self.tasks.values() if t.status == "failed"
            ),
            "tasks_pending": sum(
                1 for t in self.tasks.values() if t.status == "pending"
            ),
            "project_state": {
                task_id: task.to_dict()
                for task_id, task in self.tasks.items()
            },
        }
        self.checkpoints.append(checkpoint)
        logger.info(f"Checkpoint created: {checkpoint['label']}")
        return checkpoint

    def restore_from_checkpoint(self, checkpoint_id: int) -> bool:
        """
        Restore project state from a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            Success status
        """
        if checkpoint_id >= len(self.checkpoints):
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False

        checkpoint = self.checkpoints[checkpoint_id]
        try:
            # Restore task states
            for task_id, task_data in checkpoint["project_state"].items():
                if task_id not in self.tasks:
                    continue

                task = self.tasks[task_id]
                task.status = task_data["status"]
                task.started_at = task_data["started_at"]
                task.completed_at = task_data["completed_at"]
                task.error = task_data["error"]
                task.retry_count = task_data["retry_count"]

            logger.info(f"Project restored from checkpoint: {checkpoint['label']}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False

    def get_status(self) -> Dict:
        """Get comprehensive project status."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        in_progress = sum(1 for t in self.tasks.values() if t.status == "in_progress")
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        blocked = sum(1 for t in self.tasks.values() if t.status == "blocked")

        return {
            "project_id": self.project_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending,
            "blocked": blocked,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "checkpoints": len(self.checkpoints),
        }

    def to_dict(self) -> Dict:
        """Convert project to dictionary."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "status": self.status,
            "moprotect_protocol": self.moprotect_protocol,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "checkpoints_count": len(self.checkpoints),
            "metadata": self.metadata,
        }


class ProjectManager:
    """
    Self-management system for Jubilant Train projects.

    Features:
    - Project creation and lifecycle management
    - Task orchestration with dependency resolution
    - Checkpoint-based recovery
    - Status monitoring and reporting
    - Self-healing capabilities
    """

    def __init__(self, workspace_path: str = "."):
        """Initialize project manager."""
        self.workspace_path = Path(workspace_path)
        self.state_dir = self.workspace_path / ".jubilant" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Project] = {}
        self.load_projects()

    def create_project(
        self,
        project_id: str,
        name: str,
        description: str = "",
        moprotect_protocol: bool = True,
    ) -> Project:
        """Create a new project."""
        project = Project(project_id, name, description, moprotect_protocol)
        self.projects[project_id] = project
        self.save_project(project)
        logger.info(f"Project created: {project_id} - {name}")
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        return self.projects.get(project_id)

    def save_project(self, project: Project) -> bool:
        """
        Save project state to disk.

        Args:
            project: Project to save

        Returns:
            Success status
        """
        try:
            project_file = self.state_dir / f"{project.project_id}.json"
            with open(project_file, "w") as f:
                json.dump(project.to_dict(), f, indent=2)
            logger.info(f"Project saved: {project.project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    def load_projects(self) -> None:
        """Load all projects from disk."""
        try:
            for project_file in self.state_dir.glob("*.json"):
                with open(project_file, "r") as f:
                    data = json.load(f)

                project = Project(
                    data["project_id"],
                    data["name"],
                    data["description"],
                    data.get("moprotect_protocol", True),
                )
                project.status = data["status"]
                project.created_at = data["created_at"]
                project.metadata = data.get("metadata", {})

                # Load tasks
                for task_id, task_data in data.get("tasks", {}).items():
                    task = Task(
                        task_data["task_id"],
                        task_data["title"],
                        task_data["description"],
                        task_data.get("depends_on", []),
                        task_data.get("moprotect_step"),
                    )
                    task.status = task_data["status"]
                    task.created_at = task_data["created_at"]
                    project.add_task(task)

                self.projects[project.project_id] = project
                logger.info(f"Project loaded: {project.project_id}")

        except Exception as e:
            logger.error(f"Failed to load projects: {e}")

    def execute_project(self, project_id: str, continue_on_failure: bool = False) -> Dict:
        """
        Execute project tasks in dependency order.

        Args:
            project_id: Project to execute
            continue_on_failure: Whether to continue if a task fails

        Returns:
            Execution report
        """
        project = self.get_project(project_id)
        if not project:
            return {"status": "failed", "error": f"Project {project_id} not found"}

        execution_report = {
            "project_id": project_id,
            "started_at": datetime.now().isoformat(),
            "tasks_executed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "checkpoints_created": 0,
        }

        try:
            iteration = 0
            max_iterations = len(project.tasks) + 10  # Safety limit

            while iteration < max_iterations:
                iteration += 1

                # Get next available tasks
                available = project.get_next_available_tasks()
                if not available:
                    break

                for task in available:
                    task.start()

                    # Simulate task execution (would be actual MoProtect steps)
                    try:
                        # In real implementation, call actual sanitizer/validator functions
                        logger.info(
                            f"Executing task: {task.task_id} ({task.moprotect_step})"
                        )
                        task.complete()
                        execution_report["tasks_executed"] += 1
                        execution_report["tasks_succeeded"] += 1

                    except Exception as e:
                        task.fail(str(e))
                        execution_report["tasks_executed"] += 1
                        execution_report["tasks_failed"] += 1

                        if not continue_on_failure:
                            logger.error(
                                f"Execution halted due to task failure: {task.task_id}"
                            )
                            break

                # Create checkpoint every 5 tasks
                if execution_report["tasks_executed"] % 5 == 0:
                    project.create_checkpoint(
                        f"after_{execution_report['tasks_executed']}_tasks"
                    )
                    execution_report["checkpoints_created"] += 1

                self.save_project(project)

                if not continue_on_failure and execution_report["tasks_failed"] > 0:
                    break

            execution_report["completed_at"] = datetime.now().isoformat()
            execution_report["project_status"] = project.get_status()

        except Exception as e:
            logger.error(f"Project execution failed: {e}")
            execution_report["error"] = str(e)

        return execution_report

    def self_heal(self, project_id: str) -> Dict:
        """
        Attempt to self-heal a failed project by retrying failed tasks.

        Args:
            project_id: Project to heal

        Returns:
            Healing report
        """
        project = self.get_project(project_id)
        if not project:
            return {"status": "failed", "error": f"Project {project_id} not found"}

        heal_report = {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "tasks_retried": 0,
            "tasks_recovered": 0,
            "tasks_irrecoverable": 0,
        }

        # Get failed tasks
        failed_tasks = [t for t in project.tasks.values() if t.status == "failed"]

        for task in failed_tasks:
            if task.can_retry():
                task.retry()
                heal_report["tasks_retried"] += 1
            else:
                heal_report["tasks_irrecoverable"] += 1

        self.save_project(project)
        logger.info(f"Project self-healing attempted: {project_id}")
        return heal_report

    def generate_status_report(self, project_id: str) -> Dict:
        """Generate comprehensive project status report."""
        project = self.get_project(project_id)
        if not project:
            return {"status": "failed", "error": f"Project {project_id} not found"}

        status = project.get_status()
        blocked_tasks = project.get_blocked_tasks()
        available_tasks = project.get_next_available_tasks()

        return {
            "project_status": status,
            "available_tasks": [{"id": t.task_id, "title": t.title} for t in available_tasks],
            "blocked_tasks": [
                {"id": t.task_id, "title": t.title, "reason": t.error}
                for t in blocked_tasks
            ],
            "moprotect_steps_status": self._get_moprotect_status(project),
            "checkpoints_available": len(project.checkpoints),
            "generated_at": datetime.now().isoformat(),
        }

    def _get_moprotect_status(self, project: Project) -> Dict:
        """Get MoProtect protocol step status."""
        steps = ["disclosure", "sanitization", "human_assertion", "sealing"]
        status = {}

        for step in steps:
            tasks = [t for t in project.tasks.values() if t.moprotect_step == step]
            if tasks:
                completed = sum(1 for t in tasks if t.status == "completed")
                status[step] = {
                    "total": len(tasks),
                    "completed": completed,
                    "progress_percent": (completed / len(tasks) * 100),
                }

        return status

    def list_projects(self) -> List[Dict]:
        """List all projects with their status."""
        return [p.get_status() for p in self.projects.values()]
