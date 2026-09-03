#!/usr/bin/env python3
"""
Test suite for Debugger - System Security Analyzer
Run this to verify all components work correctly
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, '.')

try:
    from debugger import SecurityAnalyzer

    def test_basic_initialization():
        """Test that the analyzer initializes correctly"""
        print("✓ Testing basic initialization...")
        analyzer = SecurityAnalyzer()
        assert hasattr(analyzer, 'app_name'), 'Missing app_name'
        assert hasattr(analyzer, 'version'), 'Missing version'
        print("  ✓ Initialization successful")

    def test_config_loading():
        """Test configuration loading"""
        print("✓ Testing config loading...")
        analyzer = SecurityAnalyzer()
        assert isinstance(analyzer.config, dict), 'Config should be a dict'
        assert 'suspicious_process_names' in analyzer.config
        assert 'cpu_outlier_threshold' in analyzer.config
        print("  ✓ Config loaded successfully")

    def test_file_hashing():
        """Test file integrity checking"""
        print("✓ Testing file hashing...")
        analyzer = SecurityAnalyzer()

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('test content')
            temp_path = f.name

        try:
            hash_value = analyzer._calculate_file_hash(Path(temp_path))
            assert isinstance(hash_value, str), 'Hash should be a hex string'
            assert len(hash_value) in (64, 40), 'Unexpected hash length (expected SHA-256 (64) or SHA-1 (40))'
            print(f"  ✓ File hashing works: {hash_value[:16]}...")
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    def test_process_detection():
        """Test process enumeration"""
        print("✓ Testing process detection...")
        analyzer = SecurityAnalyzer()
        processes = analyzer._list_processes()
        assert isinstance(processes, (list, tuple)), 'Processes should be a list or tuple'
        assert len(processes) > 0, 'Should detect at least one process'
        print(f"  ✓ Detected {len(processes)} processes")

    def test_scan_execution():
        """Test full system scan"""
        print("✓ Testing full scan execution...")
        analyzer = SecurityAnalyzer()

        # Scan current directory
        results = analyzer.scan_system('.', update_baseline=False)

        assert isinstance(results, dict), 'Scan results should be a dict'
        assert 'timestamp' in results
        assert 'anomalies_detected' in results
        assert 'threat_level' in results
        assert results.get('status') in (None, 'COMPLETE'), "Expected status 'COMPLETE' or omitted"

        print(f"  ✓ Scan completed: {len(results.get('anomalies_detected', []))} anomalies found")
        print(f"  ✓ Threat level: {results.get('threat_level')}")

    def test_report_generation():
        """Test report generation in all formats"""
        print("✓ Testing report generation...")
        analyzer = SecurityAnalyzer()
        results = analyzer.scan_system('.', update_baseline=False)

        # Generate text report
        text_report = analyzer.generate_report(results)
        assert isinstance(text_report, str)
        assert len(text_report) > 0
        print("  ✓ Text report generated")

        # Save JSON report
        json_path = 'test_report.json'
        csv_path = 'test_report.csv'
        html_path = 'test_report.html'

        try:
            analyzer.save_report(results, json_path)
            assert os.path.exists(json_path)
            print("  ✓ JSON report saved")

            # Save CSV report
            analyzer.save_report_csv(results, csv_path)
            assert os.path.exists(csv_path)
            print("  ✓ CSV report saved")

            # Save HTML report
            analyzer.save_report_html(results, html_path)
            assert os.path.exists(html_path)
            print("  ✓ HTML report saved")
        finally:
            for p in (json_path, csv_path, html_path):
                try:
                    if os.path.exists(p):
                        os.unlink(p)
                except Exception:
                    pass

    def run_all_tests():
        """Run all tests"""
        print("\n🔍 Running Debugger Security Analyzer Test Suite\n")
        print("=" * 60)

        tests = [
            test_basic_initialization,
            test_config_loading,
            test_file_hashing,
            test_process_detection,
            test_scan_execution,
            test_report_generation,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                test()
                passed += 1
            except AssertionError as e:
                print(f"  ✗ FAILED: {str(e)}")
                failed += 1
            except Exception as e:
                print(f"  ✗ ERROR: {str(e)}")
                failed += 1

            print("=" * 60)

        print(f"\n✅ Test Results: {passed} passed, {failed} failed")

        if failed == 0:
            print("\n🎉 All tests passed! Debugger is ready for production use.")
        else:
            print("\n⚠️ Some tests failed. Review errors above.")

        return failed == 0

    if __name__ == '__main__':
        success = run_all_tests()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure debugger.py is in the same directory or the package is installed")
    sys.exit(1)
