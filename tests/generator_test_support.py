from pathlib import Path
from unittest import TestCase


class GeneratorTestCase(TestCase):
    maxDiff = None

    def assert_generated_files(self, output_dir: str, node_name: str, *suffixes: str) -> None:
        """Compare text so LF and CRLF match, but extra blank lines do not."""
        expected_dir = Path(__file__).with_name("expected_gen")
        generated_dir = Path(output_dir)
        for suffix in suffixes:
            filename = f"ApxNode_{node_name}{suffix}"
            expected = (expected_dir / filename).read_text(encoding="utf-8")
            generated = (generated_dir / filename).read_text(encoding="utf-8")
            self.assertMultiLineEqual(expected, generated, msg=filename)
