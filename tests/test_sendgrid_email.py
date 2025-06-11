import pytest
from unittest.mock import patch, MagicMock
from viam.proto.app.robot import ComponentConfig
from viam.services.generic import Generic
from src.sendgridEmail import sendgridEmail, Preset
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import base64

@pytest.mark.asyncio
async def test_initialization(mock_component_config, mock_logger, mock_sendgrid_client):
    """Test sendgridEmail initialization and reconfiguration."""
    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        assert isinstance(email_service, Generic)
        assert email_service.from_email == "from@example.com"
        assert email_service.from_email_name == "Test Sender"
        assert email_service.enforce_preset is False
        assert email_service.email_client == mock_sendgrid_client

@pytest.mark.asyncio
async def test_validate_missing_api_key(mock_component_config):
    """Test validation fails with missing API key."""
    mock_component_config.attributes.fields["api_key"].string_value = ""
    with pytest.raises(Exception, match="An api_key must be defined"):
        sendgridEmail.validate(mock_component_config)

@pytest.mark.asyncio
async def test_validate_enforce_preset_no_messages(mock_component_config):
    """Test validation fails when enforce_preset is true but preset_messages is missing."""
    mock_component_config.attributes.fields["enforce_preset"].bool_value = True
    with patch("src.sendgridEmail.struct_to_dict", return_value={"enforce_preset": True}):
        with pytest.raises(Exception, match="preset_messages must be defined"):
            sendgridEmail.validate(mock_component_config)

@pytest.mark.asyncio
async def test_send_basic_email(mock_component_config, mock_sendgrid_client):
    """Test sending a basic email without preset or attachments."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_sendgrid_client.send.return_value = mock_response

    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "to": ["test@example.com"],
            "subject": "Test Subject",
            "body": "<p>Test Body</p>"
        }
        result = await email_service.do_command(command)
        assert result == {"status_code": 202}
        mock_sendgrid_client.send.assert_called_once()

@pytest.mark.asyncio
async def test_send_with_attachment(mock_component_config, mock_sendgrid_client):
    """Test sending an email with multiple Base64-encoded attachments, verifying order."""
    mock_response = MagicMock()
    mock_response.status_code = 202

    # Mock the Mail object and its attachments
    mock_mail = MagicMock()
    mock_attachment1 = MagicMock()
    mock_attachment1.file_name = "report.xlsx"
    mock_attachment1.file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    mock_attachment2 = MagicMock()
    mock_attachment2.file_name = "chart.png"
    mock_attachment2.file_type = "image/png"
    mock_mail.attachments = [mock_attachment1, mock_attachment2]

    def send_side_effect(mail):
        mock_sendgrid_client.send.call_args = [(mock_mail,)]
        return mock_response
    mock_sendgrid_client.send.side_effect = send_side_effect

    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "to": ["test@example.com"],
            "subject": "Multi-Attachment Test",
            "body": "<p>Here’s the report and chart.</p>",
            "attachments": [
                {
                    "content": "U1BSSU5H",  # Placeholder for Excel
                    "filename": "report.xlsx",
                    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                },
                {
                    "content": "iVBORw0KGgo=",  # Minimal PNG
                    "filename": "chart.png",
                    "mime_type": "image/png"
                }
            ]
        }
        result = await email_service.do_command(command)
        assert result == {"status_code": 202}
        call_args = mock_sendgrid_client.send.call_args[0][0]
        assert len(call_args.attachments) == 2
        assert call_args.attachments[0].file_name == "report.xlsx"
        assert call_args.attachments[0].file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert call_args.attachments[1].file_name == "chart.png"
        assert call_args.attachments[1].file_type == "image/png"

@pytest.mark.asyncio
async def test_send_with_common_mime_types(mock_component_config, mock_sendgrid_client):
    """Test sending an email with attachments of common MIME types."""
    mock_response = MagicMock()
    mock_response.status_code = 202

    # Mock the Mail object and its attachments
    mock_mail = MagicMock()
    mock_attachment1 = MagicMock()
    mock_attachment1.file_name = "test.xlsx"
    mock_attachment1.file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    mock_attachment2 = MagicMock()
    mock_attachment2.file_name = "test.pdf"
    mock_attachment2.file_type = "application/pdf"
    mock_attachment3 = MagicMock()
    mock_attachment3.file_name = "test.jpg"
    mock_attachment3.file_type = "image/jpeg"
    mock_attachment4 = MagicMock()
    mock_attachment4.file_name = "test.csv"
    mock_attachment4.file_type = "text/csv"
    mock_attachment5 = MagicMock()
    mock_attachment5.file_name = "test.txt"
    mock_attachment5.file_type = "text/plain"
    mock_mail.attachments = [
        mock_attachment1,
        mock_attachment2,
        mock_attachment3,
        mock_attachment4,
        mock_attachment5
    ]

    def send_side_effect(mail):
        mock_sendgrid_client.send.call_args = [(mock_mail,)]
        return mock_response
    mock_sendgrid_client.send.side_effect = send_side_effect

    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "to": ["test@example.com"],
            "subject": "Common MIME Types Test",
            "body": "<p>Testing various attachment types.</p>",
            "attachments": [
                {
                    "content": "U1BSSU5H",  # Placeholder for Excel
                    "filename": "test.xlsx",
                    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                },
                {
                    "content": "JVBERi0xLjAK",  # Minimal PDF
                    "filename": "test.pdf",
                    "mime_type": "application/pdf"
                },
                {
                    "content": "/9j/4AAQSkZJRgABAAEAAAAAAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAAD/2Q==",  # 1x1 JPEG
                    "filename": "test.jpg",
                    "mime_type": "image/jpeg"
                },
                {
                    "content": "bmFtZSxhZ2UKQWxpY2UsMzA=",  # Simple CSV
                    "filename": "test.csv",
                    "mime_type": "text/csv"
                },
                {
                    "content": "SGVsbG8sIFdvcmxkIQ==",  # Plain text
                    "filename": "test.txt",
                    "mime_type": "text/plain"
                }
            ]
        }
        result = await email_service.do_command(command)
        assert result == {"status_code": 202}
        call_args = mock_sendgrid_client.send.call_args[0][0]
        assert len(call_args.attachments) == 5
        assert call_args.attachments[0].file_name == "test.xlsx"
        assert call_args.attachments[0].file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert call_args.attachments[1].file_name == "test.pdf"
        assert call_args.attachments[1].file_type == "application/pdf"
        assert call_args.attachments[2].file_name == "test.jpg"
        assert call_args.attachments[2].file_type == "image/jpeg"
        assert call_args.attachments[3].file_name == "test.csv"
        assert call_args.attachments[3].file_type == "text/csv"
        assert call_args.attachments[4].file_name == "test.txt"
        assert call_args.attachments[4].file_type == "text/plain"

@pytest.mark.asyncio
async def test_send_with_preset(mock_component_config, mock_sendgrid_client):
    """Test sending an email using a preset with template variables."""
    mock_response = MagicMock(status_code=202)
    mock_sendgrid_client.send.return_value = mock_response

    preset_config = {
        "preset_messages": {
            "alert": {
                "subject": "Alert: <<issue>>",
                "body": "Issue detected: <<issue>>"
            }
        }
    }
    with patch("src.sendgridEmail.struct_to_dict", return_value=preset_config), \
         patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):

        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "to": ["test@example.com"],
            "preset": "alert",
            "template_vars": {"issue": "Test Issue"}
        }
        result = await email_service.do_command(command)

        assert result == {"status_code": 202}

        # Grab and inspect the Mail payload
        mail_obj: Mail = mock_sendgrid_client.send.call_args[0][0]
        payload = mail_obj.get()

        # Verify the subject was templated
        assert payload.get("subject") == "Alert: Test Issue"
        
        # Verify the HTML content was templated
        content_list = payload.get("content")
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert content_list[0].get("value") == "Issue detected: Test Issue"

@pytest.mark.asyncio
async def test_send_missing_to(mock_component_config, mock_sendgrid_client):
    """Test error when 'to' field is missing."""
    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "subject": "Test Subject",
            "body": "<p>Test Body</p>"
        }
        result = await email_service.do_command(command)
        assert result == {"error": "'to' must be defined"}

@pytest.mark.asyncio
async def test_send_api_failure(mock_component_config, mock_sendgrid_client):
    """Test handling of SendGrid API failure."""
    mock_sendgrid_client.send.side_effect = Exception("API Error")

    with patch("src.sendgridEmail.SendGridAPIClient", return_value=mock_sendgrid_client):
        email_service = sendgridEmail.new(mock_component_config, {})
        command = {
            "command": "send",
            "to": ["test@example.com"],
            "subject": "Test Subject",
            "body": "<p>Test SendGrid API Failure</p>"
        }
        result = await email_service.do_command(command)
        assert result == {"error": "API Error"}