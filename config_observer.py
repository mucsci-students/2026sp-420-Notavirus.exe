"""
ConfigObserver - Observer design pattern for configuration change notifications

This module implements the Observer design pattern to notify multiple components
(subscribers) whenever the configuration is modified. This decouples the data model
from the views and controllers that depend on it.

Design Pattern: Observer
  - Subject: ConfigObserver (manages observers and notifies them)
  - Observers: Any component implementing ConfigChangeListener interface
  - Notifications: Called when config is added, modified, or deleted
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict


class ConfigChangeListener(ABC):
    """
    Abstract base class for components that want to be notified of config changes.

    Subclasses must implement on_config_change() to handle notifications.
    """

    @abstractmethod
    def on_config_change(self, change_type: str, affected_item: str, **kwargs) -> None:
        """
        Called when a configuration change occurs.

        Parameters:
            change_type (str): Type of change: 'added', 'modified', 'deleted'
            affected_item (str): The item that changed (e.g., 'course', 'faculty', 'room', 'lab')
            **kwargs: Additional context about the change

        Returns:
            None
        """
        pass


class ConfigObserver:
    """
    Subject class that manages observers and broadcasts configuration changes.

    This class maintains a list of subscribers and notifies them whenever
    configuration data is modified. Multiple observers can be registered
    and will all be notified of changes.

    Attributes:
        _listeners (List[ConfigChangeListener]): List of subscribed observers
        _change_history (List[Dict]): Optional history of all changes
    """

    def __init__(self, track_history: bool = False) -> None:
        """
        Initialize the ConfigObserver.

        Parameters:
            track_history (bool): If True, maintain a history of all changes

        Returns:
            None
        """
        self._listeners: List[ConfigChangeListener] = []
        self._change_history: List[Dict[str, Any]] | None = (
            [] if track_history else None
        )
        self._track_history = track_history

    def subscribe(self, listener: ConfigChangeListener) -> None:
        """
        Register a new observer to receive notifications.

        Parameters:
            listener (ConfigChangeListener): Observer to subscribe

        Returns:
            None

        Raises:
            ValueError: If listener is already subscribed
        """
        if listener in self._listeners:
            raise ValueError("Listener is already subscribed")
        self._listeners.append(listener)

    def unsubscribe(self, listener: ConfigChangeListener) -> None:
        """
        Unregister an observer from receiving notifications.

        Parameters:
            listener (ConfigChangeListener): Observer to unsubscribe

        Returns:
            None

        Raises:
            ValueError: If listener is not subscribed
        """
        if listener not in self._listeners:
            raise ValueError("Listener is not subscribed")
        self._listeners.remove(listener)

    def notify_change(self, change_type: str, affected_item: str, **kwargs) -> None:
        """
        Broadcast a configuration change to all subscribed observers.

        Parameters:
            change_type (str): Type of change: 'added', 'modified', 'deleted'
            affected_item (str): The item that changed (e.g., 'course', 'faculty')
            **kwargs: Additional context about the change

        Returns:
            None
        """
        # Record change if history tracking is enabled
        if self._track_history and self._change_history is not None:
            self._change_history.append(
                {"change_type": change_type, "affected_item": affected_item, **kwargs}
            )

        # Notify all subscribed listeners
        for listener in self._listeners:
            try:
                listener.on_config_change(change_type, affected_item, **kwargs)
            except Exception:
                # Silently continue notifying other observers
                pass

    def get_subscriber_count(self) -> int:
        """
        Get the number of currently subscribed observers.

        Parameters:
            None

        Returns:
            int: Number of subscribed listeners
        """
        return len(self._listeners)

    def get_change_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all configuration changes (if tracking is enabled).

        Parameters:
            None

        Returns:
            List[Dict]: List of recorded changes, or empty list if tracking disabled
        """
        return self._change_history if self._change_history is not None else []

    def clear_history(self) -> None:
        """
        Clear the change history.

        Parameters:
            None

        Returns:
            None
        """
        if self._change_history is not None:
            self._change_history.clear()


# Global singleton instance for application-wide use
_global_observer: ConfigObserver = ConfigObserver(track_history=True)


def get_config_observer() -> ConfigObserver:
    """
    Get the global ConfigObserver instance.

    This provides a convenient way for any component to access the observer
    without passing it through the entire object hierarchy.

    Parameters:
        None

    Returns:
        ConfigObserver: The global observer instance
    """
    return _global_observer
