import os
import pytest
from unittest.mock import Mock
from controllers.chatbot_controller import ChatbotController


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_chatbot_what_can_you_do():
    """
    Integration test to see if the chatbot works by prompting it 'What can you do?'.
    Requires OPENAI_API_KEY to be set in the environment.
    """
    mock_lab_model = Mock()
    mock_room_model = Mock()
    mock_course_model = Mock()
    mock_faculty_model = Mock()
    mock_conflict_model = Mock()

    # The controller's _no_config() returns self.lab_model is None, so lab_model must be a Mock, not None
    controller = ChatbotController(
        mock_lab_model,
        mock_room_model,
        mock_course_model,
        mock_faculty_model,
        mock_conflict_model,
    )

    import asyncio

    response = asyncio.run(controller.chat("What can you do?"))
    assert isinstance(response, str)
    assert len(response) > 0
