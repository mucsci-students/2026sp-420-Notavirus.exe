"""
Test suite for the Observer design pattern (config_observer.py)

Tests the core Observer pattern functionality without requiring UI/controller integration.
Run with: pytest tests/test_observer_pattern.py -v
"""

import pytest
from config_observer import (
    ConfigObserver,
    ConfigChangeListener,
    UINotificationListener,
    get_config_observer,
)


class MockListener(ConfigChangeListener):
    """Mock observer for testing."""

    def __init__(self):
        self.notifications = []

    def on_config_change(self, change_type: str, affected_item: str, **kwargs):
        """Record notifications for testing."""
        self.notifications.append(
            {
                "change_type": change_type,
                "affected_item": affected_item,
                "kwargs": kwargs,
            }
        )


class TestConfigObserver:
    """Test the ConfigObserver subject class."""

    def test_observer_subscribe_and_notify(self):
        """Test that subscribed observers receive notifications."""
        observer = ConfigObserver()
        listener = MockListener()

        observer.subscribe(listener)
        observer.notify_change("added", "course", course_id="CMSC 340")

        assert len(listener.notifications) == 1
        assert listener.notifications[0]["change_type"] == "added"
        assert listener.notifications[0]["affected_item"] == "course"
        assert listener.notifications[0]["kwargs"]["course_id"] == "CMSC 340"

    def test_observer_multiple_subscribers(self):
        """Test that multiple observers all receive notifications."""
        observer = ConfigObserver()
        listener1 = MockListener()
        listener2 = MockListener()
        listener3 = MockListener()

        observer.subscribe(listener1)
        observer.subscribe(listener2)
        observer.subscribe(listener3)

        observer.notify_change("modified", "faculty", faculty_name="Dr. Smith")

        assert len(listener1.notifications) == 1
        assert len(listener2.notifications) == 1
        assert len(listener3.notifications) == 1

        for listener in [listener1, listener2, listener3]:
            assert listener.notifications[0]["affected_item"] == "faculty"

    def test_observer_unsubscribe(self):
        """Test that unsubscribed observers don't receive notifications."""
        observer = ConfigObserver()
        listener = MockListener()

        observer.subscribe(listener)
        observer.notify_change("added", "room", room_name="Roddy 136")

        assert len(listener.notifications) == 1

        observer.unsubscribe(listener)
        observer.notify_change("deleted", "room", room_name="Roddy 205")

        # Still only 1 notification (from before unsubscribe)
        assert len(listener.notifications) == 1

    def test_observer_duplicate_subscribe_error(self):
        """Test that subscribing the same listener twice raises error."""
        observer = ConfigObserver()
        listener = MockListener()

        observer.subscribe(listener)

        with pytest.raises(ValueError, match="already subscribed"):
            observer.subscribe(listener)

    def test_observer_unsubscribe_not_registered_error(self):
        """Test that unsubscribing a non-registered listener raises error."""
        observer = ConfigObserver()
        listener = MockListener()

        with pytest.raises(ValueError, match="not subscribed"):
            observer.unsubscribe(listener)

    def test_observer_subscriber_count(self):
        """Test that subscriber count is accurate."""
        observer = ConfigObserver()
        listener1 = MockListener()
        listener2 = MockListener()

        assert observer.get_subscriber_count() == 0

        observer.subscribe(listener1)
        assert observer.get_subscriber_count() == 1

        observer.subscribe(listener2)
        assert observer.get_subscriber_count() == 2

        observer.unsubscribe(listener1)
        assert observer.get_subscriber_count() == 1

    def test_observer_change_history(self):
        """Test that change history is tracked when enabled."""
        observer = ConfigObserver(track_history=True)

        observer.notify_change("added", "course", course_id="CMSC 161")
        observer.notify_change("modified", "faculty", faculty_name="Dr. Jones")
        observer.notify_change("deleted", "lab", lab_name="Linux Lab")

        history = observer.get_change_history()
        assert len(history) == 3

        assert history[0]["change_type"] == "added"
        assert history[1]["change_type"] == "modified"
        assert history[2]["change_type"] == "deleted"

    def test_observer_no_history_by_default(self):
        """Test that history is not tracked by default."""
        observer = ConfigObserver(track_history=False)

        observer.notify_change("added", "room", room_name="Test Room")

        history = observer.get_change_history()
        assert history == []

    def test_observer_clear_history(self):
        """Test that history can be cleared."""
        observer = ConfigObserver(track_history=True)

        observer.notify_change("added", "course", course_id="CMSC 340")
        observer.notify_change("added", "course", course_id="CMSC 341")

        assert len(observer.get_change_history()) == 2

        observer.clear_history()
        assert len(observer.get_change_history()) == 0

    def test_observer_error_handling(self):
        """Test that one listener's error doesn't break other listeners."""
        observer = ConfigObserver()

        class BrokenListener(ConfigChangeListener):
            def on_config_change(self, change_type: str, affected_item: str, **kwargs):
                raise RuntimeError("Listener is broken!")

        working_listener = MockListener()
        broken_listener = BrokenListener()

        observer.subscribe(broken_listener)
        observer.subscribe(working_listener)

        # Should not raise - should catch error and continue
        observer.notify_change("added", "course", course_id="CMSC 340")

        # Working listener should still get notification
        assert len(working_listener.notifications) == 1


class TestUINotificationListener:
    """Test the example UINotificationListener implementation."""

    def test_ui_listener_creation(self):
        """Test that UINotificationListener can be created."""
        listener = UINotificationListener("TestComponent")
        assert listener.component_name == "TestComponent"

    def test_ui_listener_handles_notification(self, capsys):
        """Test that UINotificationListener prints notifications."""
        listener = UINotificationListener("CourseView")
        listener.on_config_change("added", "course", course_id="CMSC 340")

        captured = capsys.readouterr()
        assert "CourseView" in captured.out
        assert "added" in captured.out
        assert "course" in captured.out


class TestGlobalObserverSingleton:
    """Test the global observer singleton."""

    def test_global_observer_exists(self):
        """Test that global observer can be retrieved."""
        observer = get_config_observer()
        assert observer is not None
        assert isinstance(observer, ConfigObserver)

    def test_global_observer_is_singleton(self):
        """Test that get_config_observer returns same instance."""
        observer1 = get_config_observer()
        observer2 = get_config_observer()
        assert observer1 is observer2


class TestIntegrationScenario:
    """Integration test simulating realistic usage."""

    def test_course_add_workflow(self):
        """Simulate: add course -> observer notifies all listeners."""
        observer = ConfigObserver(track_history=True)

        # Multiple UI components subscribe
        view1 = MockListener()  # CourseView
        view2 = MockListener()  # FacultyView (also cares about courses)
        view3 = MockListener()  # ScheduleView (also cares about courses)

        observer.subscribe(view1)
        observer.subscribe(view2)
        observer.subscribe(view3)

        # Simulate controller adding a course
        observer.notify_change(
            "added", "course", course_id="CMSC 340", credits=3, added_by="manual"
        )

        # All views should have been notified
        for view in [view1, view2, view3]:
            assert len(view.notifications) == 1
            assert view.notifications[0]["kwargs"]["course_id"] == "CMSC 340"

        # History should show the change
        history = observer.get_change_history()
        assert len(history) == 1
        assert history[0]["course_id"] == "CMSC 340"

    def test_multiple_changes_workflow(self):
        """Simulate multiple sequential changes."""
        observer = ConfigObserver(track_history=True)
        listener = MockListener()
        observer.subscribe(listener)

        # Simulate a workflow
        observer.notify_change("added", "room", room_name="Roddy 136")
        observer.notify_change("added", "course", course_id="CMSC 161")
        observer.notify_change(
            "modified", "course", course_id="CMSC 161", new_credits=4
        )
        observer.notify_change("deleted", "room", room_name="Roddy 205")

        assert len(listener.notifications) == 4
        assert listener.notifications[0]["affected_item"] == "room"
        assert listener.notifications[1]["affected_item"] == "course"
        assert listener.notifications[2]["change_type"] == "modified"
        assert listener.notifications[3]["change_type"] == "deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
