"""
Tests for Jubilant Train Sanitizer and Validator

Proprietary - Closed Source
© 2026 Morley Moses Apooch. All Rights Reserved.
"""

import pytest
import tempfile
from pathlib import Path

from jubilant_train.sanitizer import CodeSanitizer
from jubilant_train.validator import ComplianceValidator


class TestCodeSanitizer:
    """Test CodeSanitizer class."""

    def test_sanitizer_creation(self):
        """Test sanitizer initialization."""
        sanitizer = CodeSanitizer()
        assert sanitizer is not None

    def test_scan_for_prohibited_licenses(self):
        """Test license scanning."""
        sanitizer = CodeSanitizer()
        content = """
# License: GNU General Public License v3
import some_module
"""
        findings = sanitizer.scan_for_prohibited_licenses(content)
        assert len(findings) > 0
        assert any("GPL" in str(f) for f in findings)

    def test_detect_language(self):
        """Test language detection."""
        sanitizer = CodeSanitizer()
        assert sanitizer._detect_language("test.py") == "python"
        assert sanitizer._detect_language("test.js") == "javascript"
        assert sanitizer._detect_language("test.md") == "markdown"
        assert sanitizer._detect_language("test.sh") == "bash"

    def test_inject_ai_disclosure(self):
        """Test AI disclosure injection."""
        sanitizer = CodeSanitizer()
        content = "def hello():\n    print('Hello')"
        modified, hash_val = sanitizer.inject_ai_disclosure(content, "test.py")
        assert "AI-ASSISTED CODE DISCLOSURE" in modified
        assert len(hash_val) == 16

    def test_sanitize_file(self):
        """Test file sanitization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.py"
            output_file = Path(tmpdir) / "output.py"

            input_file.write_text("def test():\n    pass")

            sanitizer = CodeSanitizer()
            report = sanitizer.sanitize_file(str(input_file), str(output_file))

            assert report["status"] == "success"
            assert output_file.exists()
            assert "AI-ASSISTED" in output_file.read_text()

    def test_generate_audit_log(self):
        """Test audit log generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.py"
            output_file = Path(tmpdir) / "output.py"
            audit_file = Path(tmpdir) / "audit.json"

            input_file.write_text("def test():\n    pass")

            sanitizer = CodeSanitizer()
            sanitizer.sanitize_file(str(input_file), str(output_file))
            audit = sanitizer.generate_audit_log(str(audit_file))

            assert audit_file.exists()
            assert "audit_hash" in audit
            assert audit["total_files_processed"] == 1


class TestComplianceValidator:
    """Test ComplianceValidator class."""

    def test_validator_creation(self):
        """Test validator initialization."""
        validator = ComplianceValidator()
        assert validator is not None

    def test_validate_ai_disclosure(self):
        """Test AI disclosure validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "# AI-ASSISTED CODE DISCLOSURE\n"
                "# MoProtect Methodology\n"
                "# human review required\n"
                "# Morley Moses Apooch\n"
                "def test():\n    pass"
            )

            validator = ComplianceValidator()
            result = validator.validate_ai_disclosure(str(test_file))
            assert result["status"] == "passed"

    def test_validate_copyright_notice(self):
        """Test copyright validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "# © 2026 Morley Moses Apooch\n"
                "# proprietary software\n"
                "def test():\n    pass"
            )

            validator = ComplianceValidator()
            result = validator.validate_copyright_notice(str(test_file))
            assert result["status"] in ["passed", "warning"]

    def test_seal_artifact(self):
        """Test artifact sealing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            seal_file = Path(tmpdir) / "test.seal.json"
            test_file.write_text("def test():\n    pass")

            validator = ComplianceValidator()
            seal = validator.seal_artifact(str(test_file), str(seal_file))

            assert seal["status"] == "success"
            assert "content_hash" in seal
            assert "seal_integrity_hash" in seal
            assert seal_file.exists()

    def test_validate_file(self):
        """Test comprehensive file validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "# AI-ASSISTED CODE DISCLOSURE\n"
                "# © 2026 Morley Moses Apooch\n"
                "# MoProtect Methodology\n"
                "# human review required\n"
                "# proprietary software\n"
                "def test():\n    pass"
            )

            validator = ComplianceValidator()
            report = validator.validate_file(str(test_file))

            assert "checks" in report
            assert "overall_status" in report

    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            report_file = Path(tmpdir) / "report.json"
            test_file.write_text("def test():\n    pass")

            validator = ComplianceValidator()
            validator.validate_file(str(test_file))
            report = validator.generate_compliance_report(str(report_file))

            assert report_file.exists()
            assert "report_seal" in report
            assert "summary" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
