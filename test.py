import unittest
from unittest.mock import patch, MagicMock
import run
import json
import os

class TestRun(unittest.TestCase):

    @patch('run.get_message_ts')
    @patch('run.requests.post')
    @patch('run.requests.get')
    @patch.dict(os.environ, {'GITHUB_OUTPUT': '/tmp/github_output'})
    def test_send_slack_message(self, mock_get, mock_post, mock_get_message_ts):
        # Mock the response for the post request
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'ok'

        # Mock the response for the get request
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "ok": True,
            "messages": [
                {
                    "text": "Notification from GitHub Action",
                    "ts": "1234567890.123456"
                }
            ]
        }

        # Mock the get_message_ts function
        mock_get_message_ts.return_value = "1234567890.123456"

        # Call the function
        run.send_slack_message(
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

        # Check that the post request was called with the correct payload
        expected_payload = {
            "username": "GitHub Action",
            "icon_url": "",
            "attachments": [
                {
                    "fallback": "Notification from GitHub Action",
                    "color": "#36a64f",
                    "author_name": "GitHub Action",
                    "author_link": "",
                    "author_icon": "",
                    "title": "Build Notification",
                    "title_link": "",
                    "text": "Notification from GitHub Action",
                    "fields": [
                        {
                            "title": "Status",
                            "value": "success",
                            "short": False
                        },
                        {
                            "title": "Commit message",
                            "value": "Notification from GitHub Action",
                            "short": False
                        },
                        {
                            "title": "Commit URL",
                            "value": "",
                            "short": False
                        }
                    ]
                }
            ]
        }

        self.assertEqual(mock_post.call_count, 1)
        mock_post.assert_called_once_with(
            "http://example.com",
            data=json.dumps(expected_payload),
            headers={'Content-Type': 'application/json'}
        )
        self.assertTrue(mock_get_message_ts.called)
        self.assertEqual(mock_get_message_ts.call_count, 1)

    @patch('run.requests.post')
    def test_send_reply_message(self, mock_post):
        # Mock the response for the post request
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'ok'

        # Call the function
        run.send_reply_message(
            slack_token="xoxb-1234",
            channel="C12345678",
            thread_ts="1234567890.123456",
            message="Reply message"
        )

        # Check that the post request was called with the correct payload
        expected_payload = {
            "channel": "C12345678",
            "text": "Reply message",
            "thread_ts": "1234567890.123456",
        }
        mock_post.assert_called_once_with(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": "Bearer xoxb-1234",
                "Content-Type": "application/json"
            },
            data=json.dumps(expected_payload)
        )
        self.assertTrue(mock_post.called)

    @patch('run.requests.get')
    def test_get_message_ts(self, mock_get):
        # Mock the response for the get request
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

        # Call the function
        ts = run.get_message_ts(
            slack_token="xoxb-1234",
            channel_id="C12345678",
            message="Notification from GitHub Action"
        )

        # Check that the get request was called with the correct parameters
        mock_get.assert_called_once_with(
            "https://slack.com/api/conversations.history",
            headers={
                "Authorization": "Bearer xoxb-1234",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            params={
                "channel": "C12345678",
                "limit": 1
            }
        )
        self.assertTrue(mock_get.called)
        self.assertEqual(ts, "1234567890.123456")

    @patch('run.send_reply_message')
    @patch('run.send_slack_message')
    def test_main_with_thread_ts(self, mock_send_slack_message, mock_send_reply_message):
        with patch.dict('os.environ', {
            'INPUT_SLACK_WEBHOOK': 'http://example.com',
            'INPUT_STATUS': 'success',
            'INPUT_AUTHOR_NAME': 'GitHub Action',
            'INPUT_AUTHOR_LINK': '',
            'INPUT_AUTHOR_ICON': '',
            'INPUT_TITLE': 'Build Notification',
            'INPUT_TITLE_LINK': '',
            'INPUT_MESSAGE': 'Notification from GitHub Action',
            'INPUT_COLOR': '#36a64f',
            'INPUT_SLACK_TOKEN': 'xoxb-1234',
            'INPUT_CHANNEL_ID': 'C12345678',
            'INPUT_SLACK_THREAD_TS': '1234567890.123456'
        }):
            run.main()
            mock_send_reply_message.assert_called_once_with(
                'xoxb-1234', 'C12345678', '1234567890.123456', 'Notification from GitHub Action'
            )
            mock_send_slack_message.assert_not_called()

    @patch('run.send_reply_message')
    @patch('run.send_slack_message')
    def test_main_without_thread_ts(self, mock_send_slack_message, mock_send_reply_message):
        with patch.dict('os.environ', {
            'INPUT_SLACK_WEBHOOK': 'http://example.com',
            'INPUT_STATUS': 'success',
            'INPUT_AUTHOR_NAME': 'GitHub Action',
            'INPUT_AUTHOR_LINK': '',
            'INPUT_AUTHOR_ICON': '',
            'INPUT_TITLE': 'Build Notification',
            'INPUT_TITLE_LINK': '',
            'INPUT_MESSAGE': 'Notification from GitHub Action',
            'INPUT_COLOR': '#36a64f',
            'INPUT_SLACK_TOKEN': 'xoxb-1234',
            'INPUT_CHANNEL_ID': 'C12345678'
        }):
            run.main()
            mock_send_slack_message.assert_called_once_with(
                'http://example.com', 'success', 'GitHub Action', '', '', 'Build Notification', '', 'Notification from GitHub Action', '#36a64f', 'xoxb-1234', 'C12345678'
            )
            mock_send_reply_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()