import subprocess
import unittest


SCRIPT = "/workspace/deploy.sh"


class DeployScriptTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([SCRIPT, *args], text=True, capture_output=True)

    def test_dry_run_succeeds_without_deploying(self):
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Dry run complete.")
        self.assertEqual(result.stderr, "")

    def test_help_prints_usage(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)

    def test_unknown_argument_fails_safely(self):
        result = self.run_script("--production")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)

    def test_missing_argument_fails_safely(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
