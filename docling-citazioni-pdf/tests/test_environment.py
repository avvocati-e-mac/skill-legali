"""Read-only inventory checks; no Docling imports, network, or installation."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "docling-citazioni-pdf/scripts/check_environment.py"
spec = importlib.util.spec_from_file_location("docling_environment_inventory", SCRIPT)
environment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(environment)


def inventory(versions, commands=None):
    def version(name):
        if name not in versions:
            raise environment.metadata.PackageNotFoundError(name)
        return versions[name]
    with patch.object(environment.metadata, "version", side_effect=version), \
            patch.object(environment.shutil, "which", side_effect=lambda name: (commands or {}).get(name)):
        return environment.inspect_environment()


class EnvironmentTests(unittest.TestCase):
    def test_absent_packages_are_scoped_to_interpreter_and_do_not_fail_inventory(self):
        result = inventory({})
        self.assertEqual(set(result["packages"]), set(environment.PACKAGES))
        self.assertTrue(all(value["version"] is None for value in result["packages"].values()))
        self.assertTrue(all(value["status"] == "metadata_not_found_in_this_interpreter"
                            for value in result["packages"].values()))
        self.assertEqual(result["docling_implementation_candidates"], [])
        self.assertIn("current_python_interpreter", result["scope"])

    def test_slim_is_implementation_candidate_without_docling_distribution(self):
        result = inventory({"docling-slim": "2.143.1", "docling-core": "2.105.0", "docling-mcp": "3.4.0"})
        self.assertEqual(result["docling_implementation_candidates"], ["docling-slim"])
        self.assertEqual(result["packages"]["docling-slim"]["version"], "2.143.1")
        self.assertIsNone(result["packages"]["docling"]["version"])
        self.assertEqual(result["unverified"]["conversion_readiness"], "not_checked")

    def test_full_distribution_is_implementation_candidate(self):
        result = inventory({"docling": "2.0.0", "mcp": "1.0.0"})
        self.assertEqual(result["docling_implementation_candidates"], ["docling"])
        self.assertEqual(result["packages"]["mcp"]["version"], "1.0.0")

    def test_mcp_metadata_or_command_does_not_certify_chat_connection(self):
        result = inventory({"docling-mcp": "3.4.0"}, {"docling-mcp-server": "/test/bin/docling-mcp-server"})
        self.assertEqual(result["commands"]["docling-mcp-server"], "/test/bin/docling-mcp-server")
        self.assertEqual(result["unverified"]["mcp_chat_connection"], "not_checked")
        self.assertEqual(result["unverified"]["mcp_tool_catalog"], "not_checked")
        self.assertEqual(result["unverified"]["models_available"], "not_checked")

    def test_command_absence_does_not_override_package_metadata(self):
        result = inventory({"docling-mcp": "3.4.0"})
        self.assertIsNone(result["commands"]["docling-mcp-server"])
        self.assertEqual(result["packages"]["docling-mcp"]["status"], "metadata_found")

    def test_metadata_errors_are_not_misreported_as_package_absence(self):
        with patch.object(environment.metadata, "version", side_effect=PermissionError("metadata inaccessible")):
            with self.assertRaises(PermissionError):
                environment.inspect_environment()

    def test_main_returns_two_and_json_error_on_real_inventory_failure(self):
        output, errors = StringIO(), StringIO()
        with patch.object(sys, "argv", [str(SCRIPT)]), \
                patch.object(environment, "inspect_environment", side_effect=OSError("inventory unavailable")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = environment.main()
        self.assertEqual(code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(json.loads(errors.getvalue())["status"], "inventory_error")

    def test_main_missing_packages_is_successful_inventory(self):
        result = inventory({})
        output = StringIO()
        with patch.object(sys, "argv", [str(SCRIPT)]), \
                patch.object(environment, "inspect_environment", return_value=result), redirect_stdout(output):
            code = environment.main()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["docling_implementation_candidates"], [])

    def test_cli_produces_json_without_creating_working_directory_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            before = set(Path(temporary).iterdir())
            completed = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=temporary,
                                       capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["python"]["executable"], sys.executable)
            self.assertEqual(result["unverified"]["mcp_execution_host"], "not_checked")
            self.assertEqual(set(Path(temporary).iterdir()), before)


if __name__ == "__main__":
    unittest.main()
