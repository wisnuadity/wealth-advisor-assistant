
from unittest.mock import Mock, patch

import requests
import pytest

from tools.crm_tool import CRMTool


@patch("tools.crm_tool.requests.get")
def test_get_client_profile_success(mock_get):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"client_id": "C001"}
    mock_get.return_value = response

    tool = CRMTool()
    profile = tool.get_client_profile("C001")

    assert profile["client_id"] == "C001"
    mock_get.assert_called_once()


@patch("tools.crm_tool.requests.get")
def test_get_client_profile_not_found(mock_get):
    response = Mock()
    response.status_code = 404
    mock_get.return_value = response

    tool = CRMTool()

    with pytest.raises(ValueError, match="not found"):
        tool.get_client_profile("C999")


@patch("tools.crm_tool.requests.get")
def test_get_client_profile_api_unavailable(mock_get):
    mock_get.side_effect = requests.ConnectionError(
        "Connection refused"
    )

    tool = CRMTool()

    with pytest.raises(RuntimeError, match="Unable to retrieve CRM profile"):
        tool.get_client_profile("C001")
