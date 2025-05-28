import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock
from viam.proto.app.robot import ComponentConfig
from viam.utils import struct_to_dict

# Add the module's root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def mock_logger():
    """Return a mock logger for testing."""
    return MagicMock()

@pytest.fixture
def mock_sendgrid_client():
    """Return a mock SendGridAPIClient for testing."""
    client = MagicMock()
    client.send = MagicMock()  # Synchronous send method
    return client

@pytest.fixture
def mock_component_config():
    """Return a mock ComponentConfig for testing."""
    config = MagicMock(spec=ComponentConfig)
    config.name = "test-config"
    config.attributes = MagicMock()
    config.attributes.fields = {
        "api_key": MagicMock(string_value="SG.test-key"),
        "default_from": MagicMock(string_value="from@example.com"),
        "default_from_name": MagicMock(string_value="Test Sender"),
        "enforce_preset": MagicMock(bool_value=False),
        "preset_messages": MagicMock(struct_value={})
    }
    return config

@pytest.fixture
def mock_struct_to_dict():
    """Mock struct_to_dict to return preset messages."""
    def _struct_to_dict_side_effect(struct):
        return {
            "api_key": struct.fields["api_key"].string_value,
            "default_from": struct.fields["default_from"].string_value,
            "default_from_name": struct.fields["default_from_name"].string_value,
            "enforce_preset": struct.fields["enforce_preset"].bool_value,
            "preset_messages": {}
        }
    mock = MagicMock(side_effect=_struct_to_dict_side_effect)
    return mock