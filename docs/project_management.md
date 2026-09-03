# Project Management System

**Jubilant Train Self-Management & Orchestration**

## Overview

The **ProjectManager** module provides autonomous project and task management capabilities for Jubilant Train. It enables:

- **Project Creation & Lifecycle:** Create, track, and manage multi-task projects
- **Task Orchestration:** Automatic dependency resolution and execution sequencing
- **Checkpoint Management:** Create recovery points and restore from failures
- **Self-Healing:** Automatic retry logic with configurable recovery strategies
- **MoProtect Integration:** Native support for 4-step protocol tracking
- **Status Monitoring:** Real-time project health and progress reporting

## Quick Start

### Create a Project

```bash
# Create a new project with MoProtect protocol support
python -m jubilant_train project create --id myproject --name "My AI Pipeline" --description "Safe deployment pipeline"
```

### Add Tasks

```bash
# Add a sanitization task
python -m jubilant_train project add-task \
  --id myproject \
  --task-id sanitize \
  --title "Sanitize Source Code" \
  --description "Remove GPL/AGPL code" \
  --moprotect-step sanitization

# Add a validation task that depends on sanitization
python -m jubilant_train project add-task \
  --id myproject \
  --task-id validate \
  --title "Validate Compliance" \
  --depends-on sanitize \
  --moprotect-step human_assertion
```

### Execute Project

```bash
# Execute all tasks in dependency order
python -m jubilant_train project execute --id myproject --report execution_report.json

# Continue execution even if a task fails
python -m jubilant_train project execute --id myproject --continue-on-failure
```

### Monitor Progress

```bash
# Check project status
python -m jubilant_train project status --id myproject

# List all projects
python -m jubilant_train project status
```

### Self-Healing

```bash
# Attempt to recover from failures by retrying tasks
python -m jubilant_train project heal --id myproject --report healing_report.json
```

## Core Concepts

### Task

A **Task** represents a single unit of work in a project.

**Properties:**
- `task_id`: Unique identifier
- `title`: Human-readable name
- `description`: Detailed description
- `status`: pending, in_progress, completed, failed, blocked
- `depends_on`: List of task IDs that must complete first
- `moprotect_step`: Optional MoProtect protocol step (disclosure, sanitization, human_assertion, sealing)
- `retry_count`: Number of retry attempts
- `max_retries`: Maximum number of retries (default: 3)

**Example:**
```python
from jubilant_train.manager import Task

task = Task(
    "sanitize_code",
    "Sanitize Source Code",
    "Remove GPL/AGPL dependencies",
    depends_on=["prepare_env"],
    moprotect_step="sanitization"
)
```

### Project

A **Project** is a collection of tasks with shared state and lifecycle management.

**Properties:**
- `project_id`: Unique identifier
- `name`: Project name
- `description`: Detailed description
- `status`: active, completed, failed
- `moprotect_protocol`: Enable MoProtect tracking (default: True)
- `tasks`: Dictionary of Task objects
- `checkpoints`: List of saved states for recovery

**Example:**
```python
from jubilant_train.manager import Project, Task

project = Project("myproject", "Safe Deployment", moprotect_protocol=True)

task1 = Task("setup", "Environment Setup")
task2 = Task("sanitize", "Code Sanitization", depends_on=["setup"])
task3 = Task("validate", "Compliance Validation", depends_on=["sanitize"])

project.add_task(task1)
project.add_task(task2)
project.add_task(task3)

# Get available tasks (ready to run)
available = project.get_next_available_tasks()  # Returns [task1]
```

### ProjectManager

The **ProjectManager** orchestrates project lifecycle and provides persistence.

**Key Methods:**
- `create_project()`: Create a new project
- `get_project()`: Retrieve a project
- `execute_project()`: Run all tasks in sequence
- `self_heal()`: Retry failed tasks
- `generate_status_report()`: Get comprehensive project status
- `save_project()`: Persist project state to disk
- `load_projects()`: Restore projects from disk

**Example:**
```python
from jubilant_train.manager import ProjectManager

manager = ProjectManager()
project = manager.create_project("myproject", "My Project")

# Manage tasks...
# Execute
report = manager.execute_project("myproject")

# Check status
status = manager.generate_status_report("myproject")
print(f"Progress: {status['project_status']['progress_percent']}%")
```

## Workflow

### 1. Project Creation

```python
manager = ProjectManager()
project = manager.create_project(
    "data_pipeline",
    "Secure Data Processing Pipeline",
    description="Process customer data with MoProtect compliance"
)
```

### 2. Task Addition

```python
# Task 1: Prepare data
prepare_task = Task(
    "prepare",
    "Prepare Data",
    moprotect_step="disclosure"
)
project.add_task(prepare_task)

# Task 2: Sanitize (depends on prepare)
sanitize_task = Task(
    "sanitize",
    "Sanitize Data",
    depends_on=["prepare"],
    moprotect_step="sanitization"
)
project.add_task(sanitize_task)

# Task 3: Validate (depends on sanitize)
validate_task = Task(
    "validate",
    "Validate Compliance",
    depends_on=["sanitize"],
    moprotect_step="human_assertion"
)
project.add_task(validate_task)

# Task 4: Seal (depends on validate)
seal_task = Task(
    "seal",
    "Cryptographic Sealing",
    depends_on=["validate"],
    moprotect_step="sealing"
)
project.add_task(seal_task)
```

### 3. Checkpoint Creation

```python
# Create checkpoint before risky operation
project.create_checkpoint("before_production")

# If something goes wrong, restore state
project.restore_from_checkpoint(0)
```

### 4. Project Execution

```python
# Execute all tasks
report = manager.execute_project("data_pipeline")

print(f"Tasks Executed: {report['tasks_executed']}")
print(f"Tasks Succeeded: {report['tasks_succeeded']}")
print(f"Tasks Failed: {report['tasks_failed']}")
print(f"Checkpoints Created: {report['checkpoints_created']}")
```

### 5. Status Monitoring

```python
status_report = manager.generate_status_report("data_pipeline")

print(f"Total Tasks: {status_report['project_status']['total_tasks']}")
print(f"Completed: {status_report['project_status']['completed']}")
print(f"Progress: {status_report['project_status']['progress_percent']}%")

# Check MoProtect step progress
for step, data in status_report['moprotect_steps_status'].items():
    print(f"{step}: {data['completed']}/{data['total']} complete")

# View available and blocked tasks
print(f"Ready to run: {len(status_report['available_tasks'])} tasks")
print(f"Blocked: {len(status_report['blocked_tasks'])} tasks")
```

## Self-Healing

### Automatic Retry

Failed tasks can automatically retry up to `max_retries` times:

```python
# Attempt to heal failed project
heal_report = manager.self_heal("data_pipeline")

print(f"Retried: {heal_report['tasks_retried']}")
print(f"Recovered: {heal_report['tasks_recovered']}")
print(f"Irrecoverable: {heal_report['tasks_irrecoverable']}")
```

### Checkpoint Recovery

Use checkpoints to save and restore project state:

```python
# Create checkpoint before risky operation
cp = project.create_checkpoint("before_sync")

# If operation fails, restore previous state
if operation_failed:
    project.restore_from_checkpoint(0)
    # Re-execute from checkpoint
    manager.execute_project("myproject", continue_on_failure=False)
```

## MoProtect Integration

The ProjectManager natively supports MoProtect protocol tracking:

```python
# Create project with MoProtect enabled
project = manager.create_project(
    "secure_deployment",
    "Secure Deployment Pipeline",
    moprotect_protocol=True
)

# Add tasks aligned with MoProtect steps
steps = ["disclosure", "sanitization", "human_assertion", "sealing"]
for i, step in enumerate(steps):
    task = Task(
        f"step_{i}",
        f"MoProtect Step: {step.title()}",
        moprotect_step=step
    )
    if i > 0:
        task.depends_on = [f"step_{i-1}"]
    project.add_task(task)

# Get MoProtect progress
status = manager.generate_status_report("secure_deployment")
for step, progress in status['moprotect_steps_status'].items():
    print(f"{step}: {progress['completed']}/{progress['total']}")
```

## Persistence

### Automatic Saving

Project state is automatically saved after each operation:

```python
manager.save_project(project)  # Explicit save
manager.execute_project("id")  # Auto-saves after execution
```

### Loading Projects

Projects are loaded from disk when ProjectManager is initialized:

```python
# Projects from previous sessions are automatically loaded
manager = ProjectManager()
existing_projects = manager.list_projects()
```

### Checkpoint Files

Checkpoints are stored in `.jubilant/state/` directory:

```
.jubilant/
└── state/
    ├── myproject.json           # Project state
    └── other_project.json       # Another project
```

## CLI Reference

### Project Management

```bash
# Create project
python -m jubilant_train project create \
  --id PROJECT_ID \
  --name "Project Name" \
  --description "Optional description" \
  [--no-moprotect]

# Add task
python -m jubilant_train project add-task \
  --id PROJECT_ID \
  --task-id TASK_ID \
  --title "Task Title" \
  [--description "Description"] \
  [--depends-on TASK_ID ...] \
  [--moprotect-step {disclosure,sanitization,human_assertion,sealing}]

# Execute project
python -m jubilant_train project execute \
  --id PROJECT_ID \
  [--continue-on-failure] \
  [--report REPORT_FILE]

# Check status
python -m jubilant_train project status \
  [--id PROJECT_ID] \
  [-o OUTPUT_FILE]

# Self-heal
python -m jubilant_train project heal \
  --id PROJECT_ID \
  [--report REPORT_FILE]
```

## Advanced Features

### Task Dependencies

Tasks are executed only when all dependencies complete:

```python
# Create task that depends on other tasks
task = Task(
    "validate",
    "Validate",
    depends_on=["sanitize", "review"]  # All must complete first
)
```

### Blocking

Tasks become blocked if a dependency fails:

```python
status_report = manager.generate_status_report("id")
blocked_tasks = status_report['blocked_tasks']
# These tasks are waiting for failed dependencies to be fixed
```

### Retry Configuration

Customize retry behavior per task:

```python
task = Task("id", "title")
task.max_retries = 5  # Allow up to 5 retries
```

## Examples

### Example 1: Safe Deployment Pipeline

```python
from jubilant_train.manager import ProjectManager, Task

manager = ProjectManager()
project = manager.create_project(
    "safe_deploy",
    "Safe AI Model Deployment",
    description="Deploy with full MoProtect compliance"
)

# Step 1: Disclosure - Add AI usage headers
task1 = Task("disclosure", "Inject AI Disclosure", moprotect_step="disclosure")
project.add_task(task1)

# Step 2: Sanitization - Remove GPL code
task2 = Task(
    "sanitization",
    "Sanitize GPL/AGPL",
    depends_on=["disclosure"],
    moprotect_step="sanitization"
)
project.add_task(task2)

# Step 3: Human Review
task3 = Task(
    "human_review",
    "Human Review & Approval",
    depends_on=["sanitization"],
    moprotect_step="human_assertion"
)
project.add_task(task3)

# Step 4: Seal for legal evidence
task4 = Task(
    "sealing",
    "Cryptographic Sealing",
    depends_on=["human_review"],
    moprotect_step="sealing"
)
project.add_task(task4)

# Execute
report = manager.execute_project("safe_deploy")
print(f"Deployment Complete: {report['tasks_succeeded']} succeeded, {report['tasks_failed']} failed")
```

### Example 2: Multi-Stage Data Processing

```python
project = manager.create_project(
    "data_proc",
    "Multi-Stage Data Processing"
)

# Parallel preparation tasks
for i in range(3):
    task = Task(f"prepare_{i}", f"Prepare Dataset {i}")
    project.add_task(task)

# Merge all datasets (depends on all preparation)
merge_task = Task(
    "merge",
    "Merge Datasets",
    depends_on=[f"prepare_{i}" for i in range(3)]
)
project.add_task(merge_task)

# Continue processing
process_task = Task("process", "Process Data", depends_on=["merge"])
project.add_task(process_task)

manager.execute_project("data_proc")
```

## Questions & Support

For questions about the ProjectManager or self-management system, contact:

**Morley Moses Apooch**  
Yorkton, Saskatchewan, Canada

© 2026 Morley Moses Apooch. All Rights Reserved.
