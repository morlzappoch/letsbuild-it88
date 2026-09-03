"""
Jubilant Train - Main CLI Entry Point

Provides command-line interface for:
- Sanitizing code/data (MoProtect Step 1-2)
- Validating compliance (MoProtect Step 3-4)
- Training local models (optional)

Usage:
  python -m jubilant_train sanitize --input ./src --output ./sanitized
  python -m jubilant_train validate --check ./sanitized
  python -m jubilant_train train --data ./training_data.txt

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .sanitizer import CodeSanitizer
from .validator import ComplianceValidator
from .trainer import LocalTrainer
from .manager import ProjectManager, Project, Task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def sanitize_command(args) -> int:
    """
    Execute sanitization command (MoProtect Steps 1-2).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Starting sanitization pipeline...")

    sanitizer = CodeSanitizer(config_path=args.config)

    try:
        input_path = Path(args.input)
        output_path = Path(args.output)

        if input_path.is_file():
            logger.info(f"Sanitizing file: {input_path}")
            report = sanitizer.sanitize_file(
                str(input_path),
                str(output_path),
                inject_disclosure=not args.no_disclosure,
            )
            reports = [report]
        else:
            logger.info(f"Sanitizing directory: {input_path}")
            reports = sanitizer.sanitize_directory(
                str(input_path),
                str(output_path),
                inject_disclosure=not args.no_disclosure,
            )

        # Generate audit log
        if args.audit:
            sanitizer.generate_audit_log(args.audit)
            logger.info(f"Audit log generated: {args.audit}")

        # Summary
        total_files = len(reports)
        total_findings = sum(len(r.get("findings", [])) for r in reports)
        logger.info(f"Sanitization complete: {total_files} files, {total_findings} findings")

        return 0

    except Exception as e:
        logger.error(f"Sanitization failed: {e}")
        return 1


def validate_command(args) -> int:
    """
    Execute validation command (MoProtect Steps 3-4).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Starting compliance validation pipeline...")

    validator = ComplianceValidator(config_path=args.config)

    try:
        check_path = Path(args.check)

        if check_path.is_file():
            logger.info(f"Validating file: {check_path}")
            report = validator.validate_file(str(check_path))
            reports = [report]
        else:
            logger.info(f"Validating directory: {check_path}")
            reports = validator.validate_directory(str(check_path))

        # Seal if requested
        if args.seal:
            for report in reports:
                file_path = report.get("file")
                seal_path = Path(args.seal) / f"{Path(file_path).stem}.seal.json"
                validator.seal_artifact(file_path, str(seal_path))
            logger.info(f"Seals generated in: {args.seal}")

        # Generate compliance report
        if args.report:
            validator.generate_compliance_report(args.report)
            logger.info(f"Compliance report generated: {args.report}")

        # Summary
        summary = validator.compliance_report
        logger.info(
            f"Validation complete: {summary['total_checks']} checks, "
            f"{summary['passed']} passed, {summary['failed']} failed, "
            f"{summary['warnings']} warnings"
        )

        return 0 if summary["failed"] == 0 else 1

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


def train_command(args) -> int:
    """
    Execute training command (optional fine-tuning).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Starting local model training pipeline...")

    trainer = LocalTrainer(
        model_name=args.model,
        output_dir=args.output_dir,
        enable_validation=not args.no_validation,
    )

    try:
        # Prepare data
        logger.info(f"Preparing training data: {args.data}")
        prep_report = trainer.prepare_training_data(
            args.data,
            sanitize=not args.no_sanitize,
            train_size=args.train_size,
        )
        logger.info(f"Data preparation: {prep_report['status']}")

        # Train model
        logger.info("Starting model training...")
        train_report = trainer.train_model(
            args.data,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            validate_compliance=not args.no_validation,
        )
        logger.info(f"Training: {train_report['status']}")

        # Generate report
        if args.report:
            trainer.generate_training_report(args.report)
            logger.info(f"Training report generated: {args.report}")

        return 0 if train_report["status"] == "completed" else 1

    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1


def project_create_command(args) -> int:
    """
    Execute project creation command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Creating project...")

    manager = ProjectManager()

    try:
        project = manager.create_project(
            args.project_id,
            args.name,
            args.description or "",
            moprotect_protocol=not args.no_moprotect,
        )
        logger.info(f"Project created: {project.project_id}")
        return 0

    except Exception as e:
        logger.error(f"Project creation failed: {e}")
        return 1


def project_add_task_command(args) -> int:
    """
    Execute add task command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info(f"Adding task to project: {args.project_id}")

    manager = ProjectManager()
    project = manager.get_project(args.project_id)

    if not project:
        logger.error(f"Project not found: {args.project_id}")
        return 1

    try:
        task = Task(
            args.task_id,
            args.title,
            args.description or "",
            args.depends_on or [],
            args.moprotect_step,
        )
        project.add_task(task)
        manager.save_project(project)
        logger.info(f"Task added: {task.task_id}")
        return 0

    except Exception as e:
        logger.error(f"Task creation failed: {e}")
        return 1


def project_execute_command(args) -> int:
    """
    Execute project execution command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info(f"Executing project: {args.project_id}")

    manager = ProjectManager()
    project = manager.get_project(args.project_id)

    if not project:
        logger.error(f"Project not found: {args.project_id}")
        return 1

    try:
        report = manager.execute_project(args.project_id, args.continue_on_failure)

        if args.report:
            with open(args.report, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Execution report saved: {args.report}")

        logger.info(
            f"Project execution complete: {report['tasks_succeeded']} succeeded, "
            f"{report['tasks_failed']} failed"
        )

        return 0 if report["tasks_failed"] == 0 else 1

    except Exception as e:
        logger.error(f"Project execution failed: {e}")
        return 1


def project_status_command(args) -> int:
    """
    Execute project status command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    manager = ProjectManager()

    try:
        if args.project_id:
            report = manager.generate_status_report(args.project_id)
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Status report saved: {args.output}")
            else:
                print(json.dumps(report, indent=2))
        else:
            projects = manager.list_projects()
            print(json.dumps(projects, indent=2))

        return 0

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return 1


def project_heal_command(args) -> int:
    """
    Execute project self-healing command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info(f"Attempting to heal project: {args.project_id}")

    manager = ProjectManager()
    project = manager.get_project(args.project_id)

    if not project:
        logger.error(f"Project not found: {args.project_id}")
        return 1

    try:
        report = manager.self_heal(args.project_id)

        if args.report:
            with open(args.report, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Healing report saved: {args.report}")

        logger.info(
            f"Self-healing complete: {report['tasks_retried']} retried, "
            f"{report['tasks_irrecoverable']} irrecoverable"
        )

        return 0

    except Exception as e:
        logger.error(f"Self-healing failed: {e}")
        return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Jubilant Train - Secure Data & Code Sanitization Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sanitize source code
  python -m jubilant_train sanitize --input ./src --output ./sanitized

  # Validate compliance
  python -m jubilant_train validate --check ./sanitized --report compliance.json

  # Train local model
  python -m jubilant_train train --data training.txt --model gpt2

  # Create and manage projects
  python -m jubilant_train project create --id myproj --name "My Project"
  python -m jubilant_train project add-task --id myproj --task-id task1 --title "Sanitize"
  python -m jubilant_train project execute --id myproj
  python -m jubilant_train project status --id myproj
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Jubilant Train v1.0",
    )
    parser.add_argument(
        "--config",
        default="./config",
        help="Path to config directory (default: ./config)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sanitize subcommand
    sanitize = subparsers.add_parser("sanitize", help="Sanitize code/data")
    sanitize.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input file or directory",
    )
    sanitize.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory",
    )
    sanitize.add_argument(
        "--audit",
        help="Generate audit log (path to JSON file)",
    )
    sanitize.add_argument(
        "--no-disclosure",
        action="store_true",
        help="Skip AI disclosure header injection",
    )
    sanitize.set_defaults(func=sanitize_command)

    # Validate subcommand
    validate = subparsers.add_parser("validate", help="Validate compliance")
    validate.add_argument(
        "-c",
        "--check",
        required=True,
        help="File or directory to validate",
    )
    validate.add_argument(
        "--seal",
        help="Generate seals in directory",
    )
    validate.add_argument(
        "--report",
        help="Generate compliance report (path to JSON file)",
    )
    validate.set_defaults(func=validate_command)

    # Train subcommand
    train = subparsers.add_parser("train", help="Train local model")
    train.add_argument(
        "-d",
        "--data",
        required=True,
        help="Training data file",
    )
    train.add_argument(
        "-m",
        "--model",
        default="gpt2",
        help="HuggingFace model name (default: gpt2)",
    )
    train.add_argument(
        "-o",
        "--output-dir",
        default="./models",
        help="Output directory for trained model",
    )
    train.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)",
    )
    train.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size (default: 4)",
    )
    train.add_argument(
        "--learning-rate",
        type=float,
        default=5e-5,
        help="Learning rate (default: 5e-5)",
    )
    train.add_argument(
        "--train-size",
        type=float,
        default=0.9,
        help="Fraction of data for training (default: 0.9)",
    )
    train.add_argument(
        "--no-sanitize",
        action="store_true",
        help="Skip sanitization of training data",
    )
    train.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip compliance validation",
    )
    train.add_argument(
        "--report",
        help="Generate training report (path to JSON file)",
    )
    train.set_defaults(func=train_command)

    # Project subcommand
    project = subparsers.add_parser("project", help="Project management")
    project_subs = project.add_subparsers(dest="project_cmd")

    # Project create
    project_create = project_subs.add_parser("create", help="Create a new project")
    project_create.add_argument(
        "--id",
        dest="project_id",
        required=True,
        help="Project ID",
    )
    project_create.add_argument(
        "--name",
        required=True,
        help="Project name",
    )
    project_create.add_argument(
        "--description",
        help="Project description",
    )
    project_create.add_argument(
        "--no-moprotect",
        action="store_true",
        help="Disable MoProtect protocol",
    )
    project_create.set_defaults(func=project_create_command)

    # Project add task
    project_add_task = project_subs.add_parser("add-task", help="Add task to project")
    project_add_task.add_argument(
        "--id",
        dest="project_id",
        required=True,
        help="Project ID",
    )
    project_add_task.add_argument(
        "--task-id",
        dest="task_id",
        required=True,
        help="Task ID",
    )
    project_add_task.add_argument(
        "--title",
        required=True,
        help="Task title",
    )
    project_add_task.add_argument(
        "--description",
        help="Task description",
    )
    project_add_task.add_argument(
        "--depends-on",
        dest="depends_on",
        nargs="+",
        help="Task dependencies",
    )
    project_add_task.add_argument(
        "--moprotect-step",
        dest="moprotect_step",
        choices=["disclosure", "sanitization", "human_assertion", "sealing"],
        help="MoProtect protocol step",
    )
    project_add_task.set_defaults(func=project_add_task_command)

    # Project execute
    project_execute = project_subs.add_parser("execute", help="Execute project")
    project_execute.add_argument(
        "--id",
        dest="project_id",
        required=True,
        help="Project ID",
    )
    project_execute.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue execution even if a task fails",
    )
    project_execute.add_argument(
        "--report",
        help="Save execution report to file",
    )
    project_execute.set_defaults(func=project_execute_command)

    # Project status
    project_status = project_subs.add_parser("status", help="Check project status")
    project_status.add_argument(
        "--id",
        dest="project_id",
        help="Project ID (omit to list all projects)",
    )
    project_status.add_argument(
        "-o",
        "--output",
        help="Save status report to file",
    )
    project_status.set_defaults(func=project_status_command)

    # Project heal
    project_heal = project_subs.add_parser("heal", help="Self-heal failed project")
    project_heal.add_argument(
        "--id",
        dest="project_id",
        required=True,
        help="Project ID",
    )
    project_heal.add_argument(
        "--report",
        help="Save healing report to file",
    )
    project_heal.set_defaults(func=project_heal_command)

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Show help if no command or project subcommand
    if not hasattr(args, "func") or (hasattr(args, "command") and args.command == "project" and not hasattr(args, "project_cmd")):
        if hasattr(args, "command") and args.command == "project":
            parser.parse_args(["project", "-h"])
        parser.print_help()
        return 0

    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
