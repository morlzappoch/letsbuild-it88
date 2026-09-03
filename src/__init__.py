"""
Jubilant Train - Secure Data & Code Sanitization Pipeline
Proprietary Software - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.

This package implements the MoProtect Methodology for secure, compliant preparation
of code and data for AI-assisted development and model training.
"""

__version__ = "1.0.0"
__author__ = "Morley Moses Apooch"
__license__ = "Proprietary"

from .sanitizer import CodeSanitizer
from .validator import ComplianceValidator
from .trainer import LocalTrainer
from .manager import ProjectManager, Project, Task

__all__ = [
    "CodeSanitizer",
    "ComplianceValidator",
    "LocalTrainer",
    "ProjectManager",
    "Project",
    "Task",
]
