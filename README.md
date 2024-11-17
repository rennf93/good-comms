# Good Comms

This GitHub Action sends notifications to a Slack channel. It can send a new message or reply to an existing thread based on the provided inputs.

Inspired by [rtCamp/action-slack-notify](https://github.com/rtCamp/action-slack-notify).

## Features

- Send a new message to a Slack channel.
- Reply to an existing thread in a Slack channel.
- Customize the message with author details, title, and color.

## Setup

1. Create a Slack App in your workspace
2. Add these Bot Token Scopes:
   - `chat:write`
   - `chat:write.public`
   - `channels:history`
   - `groups:history`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token
5. Create a webhook for your channel
6. Add both the token and webhook URL as GitHub secrets

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
- name: Send Slack Communication
  uses: rennf93/good-comms@v1
  with:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    STATUS: 'success'
    AUTHOR_NAME: 'GitHub Action'
    AUTHOR_LINK: 'https://github.com'
    AUTHOR_ICON: 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
    TITLE: 'Build Notification'
    TITLE_LINK: 'https://github.com'
    MESSAGE: 'Your build has completed successfully!'
    COLOR: 'warning'
    SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
    CHANNEL_ID: 'C12345678'
    SLACK_THREAD_TS: ${{ steps.previous-step.outputs.SLACK_THREAD_TS }}
```

## Usage

### Basic Example

```yaml
- name: Send Initial Slack Message
  id: send_initial_slack
  uses: rennf93/good-comms@master
  with:
    SLACK_WEBHOOK: '${{ secrets.SLACK_WEBHOOK }}'
    SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
    STATUS: 'Started'
    CHANNEL_ID: '${{ secrets.SLACK_CHANNEL }}'
    AUTHOR_NAME: 'Deployment'
    AUTHOR_LINK: 'https://github.com/rennf93/good-comms'
    AUTHOR_ICON: ':rocket:'
    TITLE: 'Deployment Started'
    TITLE_LINK: 'https://github.com/rennf93/good-comms/actions'
    MESSAGE: 'Starting deployment...'
    COLOR: warning
```

### Threaded Messages Example

```yaml
- name: Send Initial Slack Message
  id: send_initial_slack
  uses: rennf93/good-comms@master
  with:
    SLACK_WEBHOOK: '${{ secrets.SLACK_WEBHOOK }}'
    SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
    STATUS: 'Started'
    CHANNEL_ID: '${{ secrets.SLACK_CHANNEL }}'
    AUTHOR_NAME: 'Deployment'
    AUTHOR_LINK: 'https://github.com/rennf93/good-comms'
    AUTHOR_ICON: ':rocket:'
    TITLE: 'Deployment Started'
    TITLE_LINK: 'https://github.com/rennf93/good-comms/actions'
    MESSAGE: 'Starting deployment...'
    COLOR: warning

- name: Notify Success on Slack Channel
      uses: rennf93/good-comms@master
      with:
        SLACK_WEBHOOK: '${{ secrets.SLACK_WEBHOOK }}'
        SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
        STATUS: 'Success'
        CHANNEL_ID: '${{ secrets.SLACK_CHANNEL }}'
        AUTHOR_NAME: 'Deployment'
        AUTHOR_LINK: 'https://github.com/rennf93/good-comms'
        AUTHOR_ICON: ':gem:'
        TITLE: 'Deployment Successful'
        TITLE_LINK: 'https://github.com/rennf93/good-comms/actions'
        MESSAGE: 'Deplyment Successful'
        COLOR: good
        SLACK_THREAD_TS: ${{ steps.send_initial_slack.outputs.SLACK_THREAD_TS }}
```


## Notes

- The action requires both webhook URL and Bot token because:
  - Webhooks are used for basic message posting
  - Bot token is used for threading and file uploads
- Thread timestamps are automatically handled when replying to messages
- Message IDs are the same as thread timestamps for consistency

## License

This project is licensed under the MIT License - see the LICENSE file for details.
