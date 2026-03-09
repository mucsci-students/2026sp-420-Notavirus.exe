# tests/__init__.py
"""
Test package for the Scheduler Application.

This package contains all test modules organized by layer:
- test_models/: Tests for Model layer (data operations)
- test_controllers/: Tests for Controller layer (workflow orchestration)
- test_views/: Tests for View layer (user interface)

To run all tests:
    pytest tests/

To run only model tests:
    pytest tests/test_models/

To run a specific test file:
    pytest tests/test_models/test_faculty_model.py

To run a specific test:
    pytest tests/test_models/test_faculty_model.py::test_add_faculty_success
"""