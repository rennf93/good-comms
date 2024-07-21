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
        response = run.send_slack_message(
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
            "icon_emoji": "",
            "channel": "C12345678",
            "attachments": [
                {
                    "fallback": "Notification from GitHub Action",
                    "color": "#36a64f",
                    "author_name": os.getenv("GITHUB_ACTOR", ""),
                    "author_link": f"{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_ACTOR', '')}",
                    "author_icon": f"{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_ACTOR', '')}.png?size=32",
                    "title": "Build Notification",
                    "title_link": "",
                    "fields": [
                        {
                            "title": "Ref",
                            "value": os.getenv("GITHUB_REF", ""),
                            "short": True
                        },
                        {
                            "title": "Event",
                            "value": os.getenv("GITHUB_EVENT_NAME", ""),
                            "short": True
                        },
                        {
                            "title": "Actions URL",
                            "value": f"<{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_REPOSITORY', '')}/commit/{os.getenv('GITHUB_SHA', '')}/checks|{os.getenv('GITHUB_WORKFLOW', '')}>",
                            "short": True
                        },
                        {
                            "title": "Commit",
                            "value": f"<{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_REPOSITORY', '')}/commit/{os.getenv('GITHUB_SHA', '')}|{os.getenv('GITHUB_SHA', '')[:6]}>",
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": "Notification from GitHub Action",
                            "short": False
                        },
                        {
                            "title": "Status",
                            "value": "success",
                            "short": True
                        },
                        {
                            "title": "Commit URL",
                            "value": "",
                            "short": True
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
        response = run.send_slack_message(
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

        # Check that the post request was called with the correct payload
        expected_payload = {
            "username": "GitHub Action",
            "icon_url": "",
            "icon_emoji": "",
            "channel": "C12345678",
            "attachments": [
                {
                    "fallback": "Reply message",
                    "color": "#36a64f",
                    "author_name": os.getenv("GITHUB_ACTOR", ""),
                    "author_link": f"{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_ACTOR', '')}",
                    "author_icon": f"{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_ACTOR', '')}.png?size=32",
                    "title": "Build Notification",
                    "title_link": "",
                    "fields": [
                        {
                            "title": "Ref",
                            "value": os.getenv("GITHUB_REF", ""),
                            "short": True
                        },
                        {
                            "title": "Event",
                            "value": os.getenv("GITHUB_EVENT_NAME", ""),
                            "short": True
                        },
                        {
                            "title": "Actions URL",
                            "value": f"<{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_REPOSITORY', '')}/commit/{os.getenv('GITHUB_SHA', '')}/checks|{os.getenv('GITHUB_WORKFLOW', '')}>",
                            "short": True
                        },
                        {
                            "title": "Commit",
                            "value": f"<{os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_REPOSITORY', '')}/commit/{os.getenv('GITHUB_SHA', '')}|{os.getenv('GITHUB_SHA', '')[:6]}>",
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": "Reply message",
                            "short": False
                        },
                        {
                            "title": "Status",
                            "value": "success",
                            "short": True
                        },
                        {
                            "title": "Commit URL",
                            "value": "",
                            "short": True
                        }
                    ]
                }
            ],
            "thread_ts": "1234567890.123456"
        }

        mock_post.assert_called_once_with(
            "http://example.com",
            data=json.dumps(expected_payload),
            headers={'Content-Type': 'application/json'}
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

    @patch('run.send_slack_message')
    def test_main_with_thread_ts(self, mock_send_slack_message):
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
            with self.assertRaises(SystemExit) as cm:
                run.main()
            self.assertEqual(cm.exception.code, 1)
            mock_send_slack_message.assert_called_once_with(
                webhook_url='http://example.com', status='success', author_name='GitHub Action', author_link='', author_icon='', title='Build Notification', title_link='', message='Notification from GitHub Action', color='#36a64f', slack_token='xoxb-1234', channel_id='C12345678', thread_ts='1234567890.123456'
            )

    @patch('run.send_slack_message')
    def test_main_without_thread_ts(self, mock_send_slack_message):
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
            with self.assertRaises(SystemExit) as cm:
                run.main()
            self.assertEqual(cm.exception.code, 1)
            mock_send_slack_message.assert_called_once_with(
                webhook_url='http://example.com', status='success', author_name='GitHub Action', author_link='', author_icon='', title='Build Notification', title_link='', message='Notification from GitHub Action', color='#36a64f', slack_token='xoxb-1234', channel_id='C12345678', thread_ts=None
            )

if __name__ == '__main__':
    unittest.main()