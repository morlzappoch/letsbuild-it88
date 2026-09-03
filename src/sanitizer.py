"""
CodeSanitizer - License & Content Sanitization Module

Implements MoProtect Step 1 (Disclosure) and Step 2 (Sanitization):
- Scans code for prohibited licenses (GPL, AGPL)
- Injects mandatory AI disclosure headers
- Generates audit trails
- Produces sanitized output

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import json
import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CodeSanitizer:
    """
    Sanitizes code and data by:
    1. Removing/flagging GPL/AGPL dependencies
    2. Injecting AI usage disclosure headers
    3. Scanning for prohibited patterns
    4. Generating immutable audit logs
    """

    AI_DISCLOSURE_HEADER = {
        "python": """# ============================================================================
# AI-ASSISTED CODE DISCLOSURE
# This artifact was created with AI-assisted development tools.
# Human review and authorization required before deployment.
# MoProtect Methodology - Disclosure Protocol Compliance
# Owner: Morley Moses Apooch | Date: {date} | Hash: {hash}
# ============================================================================
""",
        "javascript": """// ============================================================================
// AI-ASSISTED CODE DISCLOSURE
// This artifact was created with AI-assisted development tools.
// Human review and authorization required before deployment.
// MoProtect Methodology - Disclosure Protocol Compliance
// Owner: Morley Moses Apooch | Date: {date} | Hash: {hash}
// ============================================================================
""",
        "markdown": """<!-- ============================================================================
AI-ASSISTED CODE DISCLOSURE
This artifact was created with AI-assisted development tools.
Human review and authorization required before deployment.
MoProtect Methodology - Disclosure Protocol Compliance
Owner: Morley Moses Apooch | Date: {date} | Hash: {hash}
============================================================================ -->
""",
        "bash": """#!/bin/bash
# ============================================================================
# AI-ASSISTED CODE DISCLOSURE
# This artifact was created with AI-assisted development tools.
# Human review and authorization required before deployment.
# MoProtect Methodology - Disclosure Protocol Compliance
# Owner: Morley Moses Apooch | Date: {date} | Hash: {hash}
# ============================================================================
""",
    }

    PROHIBITED_LICENSES = [
        "GPL",
        "AGPL",
        "GPLv2",
        "GPLv3",
        "AGPLv3",
        "GFDL",
        "Affero",
    ]

    PROHIBITED_PATTERNS = [
        r"GPL-2\.0",
        r"GPL-3\.0",
        r"AGPL-3\.0",
        r"copyleft",
        r"(license|licence).*?(gpl|agpl|copyleft)",
        r"free.*software.*foundation",
    ]

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the sanitizer.

        Args:
            config_path: Path to config directory with allowed_licenses.json
        """
        self.config_path = config_path or "./config"
        self.allowed_licenses = self._load_config("allowed_licenses.json")
        self.banned_patterns = self._load_config("banned_patterns.json")
        self.audit_log = []

    def _load_config(self, filename: str) -> Dict:
        """Load configuration from JSON file."""
        config_file = Path(self.config_path) / filename
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        logger.warning(f"Config file {config_file} not found, using defaults")
        return {}

    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for audit trail."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".md": "markdown",
            ".sh": "bash",
            ".rb": "python",  # Fallback
        }
        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, "python")

    def scan_for_prohibited_licenses(self, content: str) -> List[Dict]:
        """
        Scan content for prohibited licenses.

        Returns:
            List of findings with license name, line number, and match text.
        """
        findings = []
        for i, line in enumerate(content.split("\n"), 1):
            for pattern in self.PROHIBITED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "type": "prohibited_license",
                        "line": i,
                        "match": line.strip(),
                        "pattern": pattern,
                    })

        for i, line in enumerate(content.split("\n"), 1):
            for license_name in self.PROHIBITED_LICENSES:
                if license_name.lower() in line.lower():
                    findings.append({
                        "type": "prohibited_license",
                        "line": i,
                        "match": line.strip(),
                        "license": license_name,
                    })

        return findings

    def inject_ai_disclosure(
        self, content: str, file_path: str
    ) -> Tuple[str, str]:
        """
        Inject AI disclosure header into content.

        Args:
            content: File content
            file_path: Path to file (for language detection)

        Returns:
            Tuple of (modified_content, header_hash)
        """
        language = self._detect_language(file_path)
        header_template = self.AI_DISCLOSURE_HEADER.get(language, "")

        if not header_template:
            logger.warning(
                f"No disclosure template for {language}, skipping injection"
            )
            return content, ""

        content_hash = self._calculate_hash(content)[:16]
        header = header_template.format(date=datetime.now().isoformat(), hash=content_hash)

        # Avoid double-injection
        if "AI-ASSISTED CODE DISCLOSURE" in content:
            logger.info(f"{file_path} already has disclosure header, skipping")
            return content, content_hash

        modified_content = header + "\n" + content
        return modified_content, content_hash

    def sanitize_file(
        self, input_path: str, output_path: str, inject_disclosure: bool = True
    ) -> Dict:
        """
        Sanitize a single file.

        Args:
            input_path: Path to input file
            output_path: Path to output file
            inject_disclosure: Whether to inject AI disclosure header

        Returns:
            Dictionary with sanitization report
        """
        report = {
            "input_file": input_path,
            "output_file": output_path,
            "timestamp": datetime.now().isoformat(),
            "findings": [],
            "injection_status": "skipped",
            "hash": "",
        }

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            report["error"] = str(e)
            return report

        # Scan for prohibited licenses
        findings = self.scan_for_prohibited_licenses(content)
        report["findings"] = findings

        if findings:
            logger.warning(f"Found {len(findings)} prohibited patterns in {input_path}")

        # Inject AI disclosure if requested and no critical findings
        if inject_disclosure:
            modified_content, content_hash = self.inject_ai_disclosure(
                content, input_path
            )
            report["injection_status"] = "success"
            report["hash"] = content_hash
        else:
            modified_content = content
            report["injection_status"] = "disabled"

        # Write sanitized output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            report["status"] = "success"
        except Exception as e:
            report["error"] = str(e)
            report["status"] = "failed"

        self.audit_log.append(report)
        return report

    def sanitize_directory(
        self, input_dir: str, output_dir: str, inject_disclosure: bool = True
    ) -> List[Dict]:
        """
        Recursively sanitize all files in a directory.

        Args:
            input_dir: Input directory
            output_dir: Output directory
            inject_disclosure: Whether to inject AI disclosure

        Returns:
            List of sanitization reports
        """
        reports = []
        input_path = Path(input_dir)

        for file_path in input_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(input_path)
                output_file = Path(output_dir) / rel_path

                report = self.sanitize_file(str(file_path), str(output_file), inject_disclosure)
                reports.append(report)

        return reports

    def generate_audit_log(self, output_path: str) -> Dict:
        """
        Generate immutable audit log of all sanitization operations.

        Args:
            output_path: Path to write audit log JSON

        Returns:
            Audit log dictionary
        """
        audit = {
            "generated_at": datetime.now().isoformat(),
            "generator": "Jubilant Train - CodeSanitizer v1.0",
            "moprotect_protocol": "Disclosure + Sanitization",
            "operations": self.audit_log,
            "total_files_processed": len(self.audit_log),
            "findings_count": sum(
                len(op.get("findings", [])) for op in self.audit_log
            ),
        }

        audit_hash = self._calculate_hash(json.dumps(audit, sort_keys=True))
        audit["audit_hash"] = audit_hash

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(audit, f, indent=2)

        logger.info(f"Audit log generated: {output_path}")
        return audit

    def reset_audit_log(self):
        """Clear the in-memory audit log."""
        self.audit_log = []
