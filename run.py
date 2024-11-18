import os
import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
import time
import sys
import logging



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Constants
ENV_VARS = [
    "SLACK_WEBHOOK", "SLACK_CUSTOM_PAYLOAD", "SLACK_ICON", "SLACK_ICON_EMOJI",
    "SLACK_CHANNEL", "SLACK_TITLE", "SLACK_MESSAGE", "SLACK_MESSAGE_ON_SUCCESS",
    "SLACK_MESSAGE_ON_FAILURE", "SLACK_MESSAGE_ON_CANCEL", "SLACK_COLOR",
    "SLACK_USERNAME", "SLACK_FOOTER", "GITHUB_ACTOR", "GITHUB_RUN", "SITE_NAME",
    "HOST_NAME", "MSG_MINIMAL", "SLACK_LINK_NAMES", "SLACK_THREAD_TS",
    "SLACK_FILE_UPLOAD", "MSG_MODE"
]


class Webhook:
    def __init__(self, text="", username="", icon_url="", icon_emoji="", channel="", link_names="", unfurl_links=False, attachments=None, thread_ts=""):
        self.text = text
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji
        self.channel = channel
        self.link_names = link_names
        self.unfurl_links = unfurl_links
        self.attachments = attachments or []
        self.thread_ts = thread_ts


class Attachment:
    def __init__(self, fallback, pretext="", color="", author_name="", author_link="", author_icon="", footer="", fields=None):
        self.fallback = fallback
        self.pretext = pretext
        self.color = color
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.footer = footer
        self.fields = fields or []


class Field:
    def __init__(self, title="", value="", short=False):
        self.title = title
        self.value = value
        self.short = short


def get_env(name, default=""):
    return os.getenv(name, default).strip()


def send_file(filename, message, channel, thread_ts):
    try:
        with open(filename, 'rb') as file:
            m = MultipartEncoder(fields={'file': (filename, file, 'application/octet-stream'), 'initial_comment': message, 'channels': channel, 'thread_ts': thread_ts})
            headers = {"Content-Type": m.content_type, "Authorization": f"Bearer {get_env('SLACK_TOKEN')}"}
            response = requests.post("https://slack.com/api/files.upload", data=m, headers=headers)
            if response.status_code >= 299:
                return f"Error on message: {response.status_code}"
            logging.info(f"File upload response status code: {response.status_code}")
    except Exception as err:
        logging.error(f"Error in send_file: {err}")
        return err


def sanitize_value(value):
    return value.replace('\n', '').replace('\r', '').replace('=', '')


def get_message_ts(slack_token, channel_id, message, author_name, title):
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }
    params = {"channel": channel_id, "limit": 10}

    response = requests.get(url, headers=headers, params=params)
    logging.info(f"GET MSG TS Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Failed to retrieve messages: {response.status_code}")
        logging.error(f"Response body: {response.text}")
        raise ValueError(f"Failed to retrieve messages: {response.status_code}, {response.text}")

    response_data = response.json()
    if not response_data.get("ok"):
        raise ValueError(f"Error from Slack API: {response_data.get('error')}")

    messages = response_data.get("messages", [])
    if not messages:
        raise ValueError("No messages found in the channel.")

    def normalize_text(text):
        # return text.replace('\n', '').replace(' ', '').lower()
        if not text:
            return ""
        return ''.join(c.lower() for c in text if not c.isspace())

    normalized_author = normalize_text(author_name)
    logging.info(f"Looking for author: {author_name}")
    logging.info(f"Normalized author: {normalized_author}")

    for msg in messages:
        msg_username = normalize_text(msg.get('username', ''))
        logging.info(f"Checking message with username: {msg.get('username', '')}")

        if msg_username == normalized_author:
            logging.info(f"Found matching author! Thread TS: {msg.get('ts')}")
            return msg.get('ts')

    raise ValueError(f"No message found with author: {author_name}")


def send_slack_message(webhook_url, status, author_name, author_link, author_icon, title, title_link, message, color, slack_token, channel_id, thread_ts=None):
    is_webhook = not webhook_url.startswith('https://slack.com/api/')

    headers = {
        'Content-Type': 'application/json'
    }

    if not is_webhook:
        headers['Authorization'] = f'Bearer {slack_token}'

    payload = {
        "username": author_name,
        "icon_url": author_icon,
        "icon_emoji": author_icon,
        "channel": channel_id,
        "attachments": [
            {
                "fallback": message,
                "color": color,
                "author_name": get_env("GITHUB_ACTOR", ""),
                "author_link": f"{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_ACTOR')}",
                "author_icon": f"{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_ACTOR')}.png?size=32",
                "title": title,
                "title_link": title_link,
                "fields": [
                    {
                        "title": "Ref",
                        "value": get_env("GITHUB_REF"),
                        "short": True
                    },
                    {
                        "title": "Event",
                        "value": get_env("GITHUB_EVENT_NAME"),
                        "short": True
                    },
                    {
                        "title": "Actions URL",
                        "value": f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}/checks|{get_env('GITHUB_WORKFLOW')}>",
                        "short": True
                    },
                    {
                        "title": "Commit",
                        "value": f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}|{get_env('GITHUB_SHA')[:6]}>",
                        "short": True
                    },
                    {
                        "title": "Message",
                        "value": message,
                        "short": False
                    },
                    {
                        "title": "Status",
                        "value": status,
                        "short": True
                    },
                    {
                        "title": "Commit URL",
                        "value": title_link,
                        "short": True
                    }
                ]
            }
        ]
    }

    if thread_ts:
        payload["thread_ts"] = thread_ts

    response = requests.post(webhook_url, json=payload, headers=headers)
    logging.info(f"Slack API Response Status: {response.status_code}")
    logging.info(f"Slack API Response Body: {response.text}")

    if response.status_code != 200:
        error_msg = f"Request to Slack returned an error {response.status_code}, response: {response.text}"
        logging.error(error_msg)
        return error_msg

    try:
        # WebHook
        if is_webhook:
            try:
                message_ts = get_message_ts(slack_token, channel_id, message, author_name=payload["attachments"][0]["author_name"], title=title)
                thread_ts = message_ts
                channel = channel_id
                message_id = message_ts
                logging.info(f"Webhook mode - Retrieved timestamp: {thread_ts}")
            except Exception as e:
                logging.error(f"Failed to get message ts: {e}")
                current_ts = f"{time.time():.6f}"
                thread_ts = thread_ts or current_ts
                channel = channel_id
                message_id = thread_ts
                logging.info(f"Webhook mode - Using fallback timestamp: {thread_ts}")
        else:
            # API
            response_data = response.json()
            if response_data.get('ok'):
                thread_ts = response_data.get('ts')
                channel = response_data.get('channel')
                message_id = thread_ts
                logging.info(f"API mode - Message sent successfully. Thread TS: {thread_ts}")
            else:
                error_msg = f"Slack API error: {response_data.get('error')}"
                logging.error(error_msg)
                return error_msg
    except json.JSONDecodeError:
        error_msg = f"Failed to parse JSON response: {response.text}"
        logging.error(error_msg)
        return error_msg

    # Sanitize
    thread_ts = sanitize_value(thread_ts)
    channel = sanitize_value(channel)
    message_id = sanitize_value(message_id)

    github_env_path = os.getenv('GITHUB_ENV')
    if github_env_path:
        with open(github_env_path, 'a') as env_file:
            env_file.write(f"SLACK_THREAD_TS={thread_ts}\n")
            env_file.write(f"SLACK_CHANNEL={channel}\n")
            env_file.write(f"SLACK_MESSAGE_ID={message_id}\n")

    return f"SLACK_THREAD_TS={thread_ts}\nSLACK_CHANNEL={channel}\nSLACK_MESSAGE_ID={message_id}\n"


def build_fields(text, commit_sha):
    minimal = get_env("MSG_MINIMAL")
    fields = []
    if minimal == "true":
        fields.append(Field(get_env("SLACK_TITLE"), text, False))
    elif minimal:
        required_fields = minimal.split(",")
        fields.append(Field(get_env("SLACK_TITLE"), text, False))
        for required_field in required_fields:
            if required_field.lower() == "ref":
                fields.append(Field("Ref", get_env("GITHUB_REF"), True))
            elif required_field.lower() == "event":
                fields.append(Field("Event", get_env("GITHUB_EVENT_NAME"), True))
            elif required_field.lower() == "actions url":
                fields.append(Field("Actions URL", f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}/checks|{get_env('GITHUB_WORKFLOW')}>", True))
            elif required_field.lower() == "commit":
                fields.append(Field("Commit", f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}|{commit_sha}>", True))
    else:
        fields.extend([
            Field("Ref", get_env("GITHUB_REF"), True),
            Field("Event", get_env("GITHUB_EVENT_NAME"), True),
            Field("Actions URL", f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}/checks|{get_env('GITHUB_WORKFLOW')}>", True),
            Field("Commit", f"<{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_REPOSITORY')}/commit/{get_env('GITHUB_SHA')}|{commit_sha}>", True),
            Field(get_env("SLACK_TITLE"), text, False)
        ])

    host_name = get_env("HOST_NAME")
    if host_name:
        fields.extend([
            Field(get_env("SITE_TITLE"), get_env("SITE_NAME"), True),
            Field(get_env("HOST_TITLE"), get_env("HOST_NAME"), True)
        ])
    return fields


def build_attachments(text, color, fields):
    return [
        Attachment(
            fallback=get_env("SLACK_MESSAGE", f"GITHUB_ACTION={get_env('GITHUB_ACTION')} \n GITHUB_ACTOR={get_env('GITHUB_ACTOR')} \n GITHUB_EVENT_NAME={get_env('GITHUB_EVENT_NAME')} \n GITHUB_REF={get_env('GITHUB_REF')} \n GITHUB_REPOSITORY={get_env('GITHUB_REPOSITORY')} \n GITHUB_WORKFLOW={get_env('GITHUB_WORKFLOW')}"
            ),
            color=color,
            author_name=get_env("GITHUB_ACTOR", ""),
            author_link=f"{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_ACTOR')}",
            author_icon=f"{get_env('GITHUB_SERVER_URL')}/{get_env('GITHUB_ACTOR')}.png?size=32",
            footer=get_env("SLACK_FOOTER", f"<Powered by Good Comms GitHub Action|https://github.com/rennf93/good-comms>"),
            fields=fields
        )
    ]


def main():
    endpoint = get_env("SLACK_WEBHOOK")
    logging.info(f"Using endpoint: {endpoint}")
    logging.info(f"Message mode: {get_env('MSG_MODE')}")

    custom_payload = get_env("SLACK_CUSTOM_PAYLOAD", "")
    if not endpoint:
        if not get_env("SLACK_CHANNEL"):
            logging.error("Channel is required for sending message using a token")
            sys.exit(1)
        if get_env("MSG_MODE") == "TOKEN":
            endpoint = "https://slack.com/api/chat.postMessage"
        else:
            logging.error("URL is required")
            sys.exit(2)
    if custom_payload:
        response = requests.post(endpoint, data=custom_payload.encode(), headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            logging.error(f"Error sending custom payload: {response.status_code}, {response.text}")
            sys.exit(2)
    else:
        text = get_env("SLACK_MESSAGE")
        if not text:
            logging.error("Message is required")
            sys.exit(3)
        if get_env("GITHUB_WORKFLOW").startswith(".github"):
            try:
                os.environ["GITHUB_WORKFLOW"] = "Link to action run.yaml"
            except Exception as err:
                logging.error(f"Unable to update the workflow's variables: {err}")
                sys.exit(4)

        long_sha = get_env("GITHUB_SHA")
        commit_sha = long_sha[:6]

        slack_color = get_env("COLOR").lower()
        color = {
            "success": "good",
            "cancelled": "#808080",
            "failure": "danger"
        }.get(slack_color, get_env("COLOR", "good"))

        if slack_color == "success":
            text = get_env("SLACK_MESSAGE_ON_SUCCESS", text)
        elif slack_color == "cancelled":
            text = get_env("SLACK_MESSAGE_ON_CANCEL", text)
        elif slack_color == "failure":
            text = get_env("SLACK_MESSAGE_ON_FAILURE", text)

        if not text:
            text = "EOM"

        # fields = build_fields(text, commit_sha)
        thread_ts = get_env("SLACK_THREAD_TS")

        result = send_slack_message(
            webhook_url=endpoint,
            status=get_env("STATUS"),
            author_name=get_env("AUTHOR_NAME"),
            author_link=get_env("AUTHOR_LINK"),
            author_icon=get_env("AUTHOR_ICON"),
            title=get_env("TITLE"),
            title_link=get_env("TITLE_LINK"),
            message=text,
            color=color,
            slack_token=get_env("SLACK_TOKEN"),
            channel_id=get_env("CHANNEL_ID"),
            thread_ts=thread_ts if thread_ts else None
        )

        if result.startswith("Error"):
            logging.error(f"Error sending message: {result}")
            sys.exit(1)
        else:
            print(result)
            logging.info("Successfully sent the message!")


if __name__ == "__main__":
    main()