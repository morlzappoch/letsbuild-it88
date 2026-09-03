"""
ComplianceValidator - AI Disclosure & Legal Compliance Module

Implements MoProtect Step 3 (Human Assertion) and Step 4 (Sealing):
- Validates mandatory AI disclosure headers
- Checks for copyright & WIPO compliance
- Verifies human review checkpoints
- Produces sealing hashes for legal evidence

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComplianceValidator:
    """
    Validates code and artifacts for:
    1. Mandatory AI disclosure headers
    2. Copyright & WIPO compliance
    3. Human review sign-off
    4. Cryptographic sealing for legal evidence
    """

    REQUIRED_DISCLOSURE_KEYWORDS = [
        "AI-ASSISTED",
        "human review",
        "MoProtect",
        "Morley Moses Apooch",
    ]

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the compliance validator."""
        self.config_path = config_path or "./config"
        self.validation_log = []
        self.compliance_report = {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }

    def _calculate_seal_hash(self, content: str) -> str:
        """Calculate SHA-256 seal hash for legal evidence."""
        return hashlib.sha256(content.encode()).hexdigest()

    def validate_ai_disclosure(self, file_path: str) -> Dict:
        """
        Validate that AI disclosure header is present and complete.

        Args:
            file_path: Path to file to validate

        Returns:
            Validation result with status and findings
        """
        result = {
            "file": file_path,
            "check_type": "ai_disclosure",
            "timestamp": datetime.now().isoformat(),
            "status": "passed",
            "issues": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            return result

        # Check for disclosure header
        if "AI-ASSISTED CODE DISCLOSURE" not in content:
            result["status"] = "failed"
            result["issues"].append("Missing AI-ASSISTED CODE DISCLOSURE header")

        # Check for required keywords
        missing_keywords = []
        for keyword in self.REQUIRED_DISCLOSURE_KEYWORDS:
            if keyword not in content:
                missing_keywords.append(keyword)

        if missing_keywords:
            result["status"] = "failed"
            result["issues"].append(
                f"Missing required keywords: {', '.join(missing_keywords)}"
            )

        # Check for hash in header (sealing requirement)
        if "Hash:" not in content and "hash:" not in content.lower():
            result["status"] = "warning"
            result["issues"].append("Missing content hash in disclosure header")

        result["issues_count"] = len(result["issues"])
        self.validation_log.append(result)
        self.compliance_report["total_checks"] += 1
        if result["status"] == "passed":
            self.compliance_report["passed"] += 1
        elif result["status"] == "failed":
            self.compliance_report["failed"] += 1
        else:
            self.compliance_report["warnings"] += 1

        return result

    def validate_copyright_notice(self, file_path: str) -> Dict:
        """
        Validate copyright notice compliance.

        Args:
            file_path: Path to file to validate

        Returns:
            Validation result
        """
        result = {
            "file": file_path,
            "check_type": "copyright",
            "timestamp": datetime.now().isoformat(),
            "status": "passed",
            "issues": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            return result

        # Check for copyright statement
        copyright_pattern = r"©.*20\d{2}.*Morley Moses Apooch"
        if not re.search(copyright_pattern, content):
            result["status"] = "warning"
            result["issues"].append("Missing or incomplete copyright notice")

        # Check for proprietary/closed-source indicator
        if not re.search(r"proprietary|closed.?source", content, re.IGNORECASE):
            result["status"] = "warning"
            result["issues"].append("Missing proprietary/closed-source indicator")

        result["issues_count"] = len(result["issues"])
        self.validation_log.append(result)
        self.compliance_report["total_checks"] += 1
        if result["status"] == "passed":
            self.compliance_report["passed"] += 1
        else:
            self.compliance_report["warnings"] += 1

        return result

    def validate_human_review_signoff(self, file_path: str) -> Dict:
        """
        Validate human review sign-off presence.

        Args:
            file_path: Path to file to validate

        Returns:
            Validation result
        """
        result = {
            "file": file_path,
            "check_type": "human_review",
            "timestamp": datetime.now().isoformat(),
            "status": "warning",  # Optional but recommended
            "issues": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            return result

        # Check for human review indicators
        review_patterns = [
            r"REVIEWED.*[BY|AUTHORIZED]",
            r"HUMAN REVIEW COMPLETE",
            r"APPROVED",
            r"SIGNED OFF",
        ]

        has_review = any(re.search(pattern, content, re.IGNORECASE) for pattern in review_patterns)

        if not has_review:
            result["status"] = "warning"
            result["issues"].append(
                "Human review sign-off not found (optional but recommended)"
            )
        else:
            result["status"] = "passed"

        result["issues_count"] = len(result["issues"])
        self.validation_log.append(result)
        self.compliance_report["total_checks"] += 1
        if result["status"] == "passed":
            self.compliance_report["passed"] += 1
        else:
            self.compliance_report["warnings"] += 1

        return result

    def seal_artifact(
        self, file_path: str, seal_output_path: Optional[str] = None
    ) -> Dict:
        """
        Cryptographically seal an artifact for legal evidence (MoProtect Step 4).

        Args:
            file_path: Path to artifact to seal
            seal_output_path: Optional path to write seal JSON

        Returns:
            Seal dictionary with hash and timestamp
        """
        seal = {
            "artifact": file_path,
            "sealed_at": datetime.now().isoformat(),
            "seal_provider": "Jubilant Train - ComplianceValidator",
            "moprotect_protocol": "Sealing (Step 4)",
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            seal["content_hash"] = self._calculate_seal_hash(content)
            seal["status"] = "success"
        except Exception as e:
            seal["status"] = "failed"
            seal["error"] = str(e)
            return seal

        # Generate seal integrity hash
        seal_integrity = self._calculate_seal_hash(json.dumps(seal, sort_keys=True))
        seal["seal_integrity_hash"] = seal_integrity

        # Write seal to file if requested
        if seal_output_path:
            import os
            os.makedirs(os.path.dirname(seal_output_path), exist_ok=True)
            with open(seal_output_path, "w") as f:
                json.dump(seal, f, indent=2)
            logger.info(f"Seal written to {seal_output_path}")

        return seal

    def validate_file(self, file_path: str) -> Dict:
        """
        Run all compliance checks on a single file.

        Args:
            file_path: Path to file to validate

        Returns:
            Comprehensive validation report
        """
        logger.info(f"Validating {file_path}")

        report = {
            "file": file_path,
            "validation_timestamp": datetime.now().isoformat(),
            "checks": {
                "ai_disclosure": self.validate_ai_disclosure(file_path),
                "copyright": self.validate_copyright_notice(file_path),
                "human_review": self.validate_human_review_signoff(file_path),
            },
            "overall_status": "passed",
        }

        # Determine overall status
        for check_result in report["checks"].values():
            if check_result.get("status") == "failed":
                report["overall_status"] = "failed"
                break
            elif check_result.get("status") == "warning":
                report["overall_status"] = "warning"

        return report

    def validate_directory(self, directory: str) -> List[Dict]:
        """
        Validate all files in a directory.

        Args:
            directory: Path to directory to validate

        Returns:
            List of validation reports
        """
        reports = []
        dir_path = Path(directory)

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [
                ".py",
                ".js",
                ".ts",
                ".md",
                ".sh",
            ]:
                report = self.validate_file(str(file_path))
                reports.append(report)

        return reports

    def generate_compliance_report(self, output_path: str) -> Dict:
        """
        Generate final compliance report with seal.

        Args:
            output_path: Path to write report

        Returns:
            Compliance report dictionary
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "generator": "Jubilant Train - ComplianceValidator v1.0",
            "moprotect_protocol": "Full 4-Step Validation",
            "summary": self.compliance_report.copy(),
            "validations": self.validation_log,
        }

        # Seal the report
        report_json = json.dumps(report, sort_keys=True)
        report["report_seal"] = self._calculate_seal_hash(report_json)

        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Compliance report generated: {output_path}")
        return report

    def reset_logs(self):
        """Clear validation logs and compliance counters."""
        self.validation_log = []
        self.compliance_report = {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }
