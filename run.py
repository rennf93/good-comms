import os
import requests
import json
import time

def send_slack_message(webhook_url, status, author_name, author_link, author_icon, title, title_link, message, color, slack_token, channel_id):
    payload = {
        "attachments": [
            {
                "fallback": message,
                "color": color,
                "author_name": author_name,
                "author_link": author_link,
                "author_icon": author_icon,
                "title": title,
                "title_link": title_link,
                "text": message,
                "fields": [
                    {
                        "title": "Status",
                        "value": status,
                        "short": False
                    }
                ]
            }
        ]
    }
    response = requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

    if response.text.strip() == "ok":
        print("Message sent successfully, but no JSON response to parse.")
        time.sleep(5)
        thread_ts = get_message_ts(slack_token, channel_id, message)
        channel = channel_id
        message_id = thread_ts
    else:
        try:
            response_data = response.json()
            thread_ts = response_data.get('ts')
            channel = response_data.get('channel')
            message_id = response_data.get('message', {}).get('ts', thread_ts)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response: {response.text}")

    with open(os.getenv('GITHUB_OUTPUT'), 'a') as output_file:
        print(f"SLACK_THREAD_TS={thread_ts}\n", file=output_file)
        print(f"SLACK_CHANNEL={channel}\n", file=output_file)
        print(f"SLACK_MESSAGE_ID={message_id}\n", file=output_file)

    # Send the same message as a reply
    send_reply_message(slack_token, channel, thread_ts, message)

def send_reply_message(slack_token, channel, thread_ts, message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": message,
        "thread_ts": thread_ts
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Reply response status code: {response.status_code}")
    print(f"Reply response text: {response.text}")
    if response.status_code != 200:
        raise ValueError(f"Failed to send reply message: {response.status_code}, {response.text}")

def get_message_ts(slack_token, channel_id, message):
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "channel": channel_id,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve messages: {response.status_code}, {response.text}")

    response_data = response.json()
    if not response_data.get("ok"):
        raise ValueError(f"Error from Slack API: {response_data.get('error')}")

    messages = response_data.get("messages", [])
    if not messages:
        raise ValueError("No messages found in the channel.")

    for msg in messages:
        print(f"Checking message: {msg.get('text')}")
        if 'attachments' in msg:
            for attachment in msg['attachments']:
                print(f"Checking attachment text: {attachment.get('text')}")
                if attachment.get('text') == message:
                    return msg.get('ts')

    raise ValueError("Message not found in the channel.")

def main():
    webhook_url = os.getenv('INPUT_SLACK_WEBHOOK')
    status = os.getenv('INPUT_STATUS')
    author_name = os.getenv('INPUT_AUTHOR_NAME', 'GitHub Action')
    author_link = os.getenv('INPUT_AUTHOR_LINK', '')
    author_icon = os.getenv('INPUT_AUTHOR_ICON', '')
    title = os.getenv('INPUT_TITLE', 'Build Notification')
    title_link = os.getenv('INPUT_TITLE_LINK', '')
    message = os.getenv('INPUT_MESSAGE', 'Notification from GitHub Action')
    color = os.getenv('INPUT_COLOR', '#36a64f')
    slack_token = os.getenv('INPUT_SLACK_TOKEN')
    channel_id = os.getenv('INPUT_CHANNEL_ID')
    thread_ts = os.getenv('INPUT_SLACK_THREAD_TS')

    if thread_ts:
        send_reply_message(slack_token, channel_id, thread_ts, message)
    else:
        send_slack_message(webhook_url, status, author_name, author_link, author_icon, title, title_link, message, color, slack_token, channel_id)

if __name__ == "__main__":
    main()