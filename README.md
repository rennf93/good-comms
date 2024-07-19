# Good Comms

This GitHub Action sends notifications to a Slack channel. It can send a new message or reply to an existing thread based on the provided inputs.

## Features

- Send a new message to a Slack channel.
- Reply to an existing thread in a Slack channel.
- Customize the message with author details, title, and color.

## Inputs

| Input Name         | Description                                     | Required |
| ------------------ | ----------------------------------------------- | -------- |
| `SLACK_WEBHOOK`    | Slack webhook URL for sending messages          | true     |
| `STATUS`           | Status of the notification (e.g., success, fail)| false    |
| `AUTHOR_NAME`      | Name of the message author                      | false    |
| `AUTHOR_LINK`      | Link for the message author                     | false    |
| `AUTHOR_ICON`      | Icon URL for the message author                 | false    |
| `TITLE`            | Title of the message                            | false    |
| `TITLE_LINK`       | Link for the message title                      | false    |
| `MESSAGE`          | The message content                             | true     |
| `COLOR`            | Color of the message attachment                 | false    |
| `SLACK_TOKEN`      | Slack token for sending replies                 | true     |
| `CHANNEL_ID`       | Slack channel ID for sending replies            | true     |
| `SLACK_THREAD_TS`  | Timestamp of the thread to reply to             | false    |

## Outputs

This action sets the following outputs:

| Output Name        | Description                                     |
| ------------------ | ----------------------------------------------- |
| `SLACK_THREAD_TS`  | Timestamp of the Slack thread                   |
| `SLACK_CHANNEL`    | Slack channel ID                                |
| `SLACK_MESSAGE_ID` | ID of the sent Slack message                    |

## Usage

To use this action in your workflow, add the following step:

```yaml
- name: Send Slack Notification
  uses: your-username/slack-notification-action@v1
  with:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    STATUS: 'success'
    AUTHOR_NAME: 'GitHub Action'
    AUTHOR_LINK: 'https://github.com'
    AUTHOR_ICON: 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
    TITLE: 'Build Notification'
    TITLE_LINK: 'https://github.com'
    MESSAGE: 'Your build has completed successfully!'
    COLOR: '#36a64f'
    SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
    CHANNEL_ID: 'C12345678'
    SLACK_THREAD_TS: ${{ steps.previous-step.outputs.SLACK_THREAD_TS }}
```

## Example Workflow

Here is an example of how to integrate this action into a GitHub workflow:

```yaml
name: Example Workflow

on:
  push:
    branches:
      - main

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Send Slack Notification
        uses: your-username/slack-notification-action@v1
        with:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          STATUS: 'success'
          AUTHOR_NAME: 'GitHub Action'
          AUTHOR_LINK: 'https://github.com'
          AUTHOR_ICON: 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
          TITLE: 'Build Notification'
          TITLE_LINK: 'https://github.com'
          MESSAGE: 'Your build has completed successfully!'
          COLOR: '#36a64f'
          SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
          CHANNEL_ID: 'C12345678'
          SLACK_THREAD_TS: ${{ steps.previous-step.outputs.SLACK_THREAD_TS }}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
