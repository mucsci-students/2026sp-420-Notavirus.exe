# tests/test_integration/__init__.py
"""
Integration tests for the scheduler application.

These tests verify end-to-end workflows by simulating user interactions
through the SchedulerController. They test complete scenarios including:
- Faculty CRUD operations
- Course CRUD operations  
- Full workflow from adding entities to generating schedules

These tests use mocked input to simulate user interactions and verify
that the entire system works together correctly.

Test files:
- Integration tests for complete user workflows

Note: These tests use temporary config files and mock user input to
test the entire application flow without requiring manual interaction.
"""