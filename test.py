import unittest
from unittest.mock import patch, MagicMock
import run
import json
import os


class TestRun(unittest.TestCase):

    @patch('run.get_message_ts')
    @patch('run.requests.post')
    def test_send_slack_message(self, mock_post, mock_get_message_ts):
        # Setup mocks
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'ok'
        mock_get_message_ts.return_value = "1234567890.123456"

        # Call the function
        result = run.send_slack_message(
            webhook_url="http://example.com",
            status="success",
            author_name="GitHub Action",
            author_link="",
            author_icon="",
            title="Build Notification",
            title_link="",
            message="Notification from GitHub Action",
            color="#36a64f",
            slack_token="xoxb-1234",
            channel_id="C12345678"
        )

        # Verify the result format
        self.assertIn("SLACK_THREAD_TS=", result)
        self.assertIn("SLACK_CHANNEL=", result)
        self.assertIn("SLACK_MESSAGE_ID=", result)

    @patch('run.requests.post')
    def test_send_reply_message(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'ok'

        result = run.send_slack_message(
            webhook_url="http://example.com",
            status="success",
            author_name="GitHub Action",
            author_link="",
            author_icon="",
            title="Build Notification",
            title_link="",
            message="Reply message",
            color="#36a64f",
            slack_token="xoxb-1234",
            channel_id="C12345678",
            thread_ts="1234567890.123456"
        )

        # Verify the result contains the thread_ts
        self.assertIn("SLACK_THREAD_TS=1234567890.123456", result)

    @patch('run.requests.get')
    def test_get_message_ts(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "ok": True,
            "messages": [
                {
                    "text": "Notification from GitHub Action",
                    "ts": "1234567890.123456",
                    "attachments": [
                        {
                            "text": "Notification from GitHub Action"
                        }
                    ]
                }
            ]
        }

        ts = run.get_message_ts(
            slack_token="xoxb-1234",
            channel_id="C12345678",
            message="Notification from GitHub Action"
        )

        self.assertEqual(ts, "1234567890.123456")

    @patch('run.send_slack_message')
    def test_main_with_thread_ts(self, mock_send_slack_message):
        mock_send_slack_message.return_value = "SLACK_THREAD_TS=1234567890.123456\nSLACK_CHANNEL=C12345678\nSLACK_MESSAGE_ID=1234567890.123456"

        with patch.dict('os.environ', {
            'SLACK_WEBHOOK': 'http://example.com',
            'STATUS': 'success',
            'AUTHOR_NAME': 'GitHub Action',
            'AUTHOR_LINK': '',
            'AUTHOR_ICON': '',
            'TITLE': 'Build Notification',
            'TITLE_LINK': '',
            'MESSAGE': 'Notification from GitHub Action',
            'COLOR': '#36a64f',
            'SLACK_TOKEN': 'xoxb-1234',
            'CHANNEL_ID': 'C12345678',
            'SLACK_THREAD_TS': '1234567890.123456',
            'SLACK_MESSAGE': 'Notification from GitHub Action',
            'MSG_MODE': 'WEBHOOK'
        }):
            run.main()
            mock_send_slack_message.assert_called_once()

    @patch('run.send_slack_message')
    def test_main_without_thread_ts(self, mock_send_slack_message):
        mock_send_slack_message.return_value = "SLACK_THREAD_TS=1234567890.123456\nSLACK_CHANNEL=C12345678\nSLACK_MESSAGE_ID=1234567890.123456"

        with patch.dict('os.environ', {
            'SLACK_WEBHOOK': 'http://example.com',
            'STATUS': 'success',
            'AUTHOR_NAME': 'GitHub Action',
            'AUTHOR_LINK': '',
            'AUTHOR_ICON': '',
            'TITLE': 'Build Notification',
            'TITLE_LINK': '',
            'MESSAGE': 'Notification from GitHub Action',
            'COLOR': '#36a64f',
            'SLACK_TOKEN': 'xoxb-1234',
            'CHANNEL_ID': 'C12345678',
            'SLACK_MESSAGE': 'Notification from GitHub Action',
            'MSG_MODE': 'WEBHOOK'
        }):
            run.main()
            mock_send_slack_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()