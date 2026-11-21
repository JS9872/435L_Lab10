"""Tests for the application behavior and command-line entry point."""

import io
import runpy
import unittest
from contextlib import redirect_stdout

from app import greet, main


class TestApp(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("World"), "Hello, World from Joey Saade!")

    def test_personalized_greeting(self):
        self.assertEqual(greet("Jenkins"), "Hello, Jenkins from Joey Saade!")

    def test_main(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main()
        self.assertEqual(output.getvalue(), "Hello, World from Joey Saade!\n")

    def test_script_entry_point(self):
        output = io.StringIO()
        with redirect_stdout(output):
            runpy.run_module("app", run_name="__main__")
        self.assertEqual(output.getvalue(), "Hello, World from Joey Saade!\n")


if __name__ == "__main__":
    unittest.main()
