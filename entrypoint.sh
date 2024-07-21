#!/bin/sh -l

# Extract inputs from 'with' GitHub context using the INPUT_ prefix
export SLACK_WEBHOOK="${INPUT_SLACK_WEBHOOK}"
export STATUS="${INPUT_STATUS}"
export AUTHOR_NAME="${INPUT_AUTHOR_NAME:-"GitHub Action"}"
export AUTHOR_LINK="${INPUT_AUTHOR_LINK:-""}"
export AUTHOR_ICON="${INPUT_AUTHOR_ICON:-""}"
export TITLE="${INPUT_TITLE:-"Build Notification"}"
export TITLE_LINK="${INPUT_TITLE_LINK:-""}"
export SLACK_MESSAGE="${INPUT_MESSAGE:-"Notification from GitHub Action"}"
export COLOR="${INPUT_COLOR:-"#36a64f"}"
export SLACK_TOKEN="${INPUT_SLACK_TOKEN}"
export CHANNEL_ID="${INPUT_CHANNEL_ID}"
export SLACK_THREAD_TS="${INPUT_SLACK_THREAD_TS}"

# Check if required inputs are provided
if [ -z "$SLACK_WEBHOOK" ]; then
  echo "SLACK_WEBHOOK is a required input and must be set."
  exit 1
fi

if [ -z "$STATUS" ]; then
  echo "STATUS is a required input and must be set."
  exit 1
fi

if [ -z "$SLACK_TOKEN" ]; then
  echo "SLACK_TOKEN is a required input and must be set."
  exit 1
fi

if [ -z "$CHANNEL_ID" ]; then
  echo "CHANNEL_ID is a required input and must be set."
  exit 1
fi

# Ensure SLACK_MESSAGE is set
if [ -z "$SLACK_MESSAGE" ]; then
  echo "SLACK_MESSAGE is a required input and must be set."
  exit 1
fi

# Run the Python script with the provided inputs and capture the output
output=$(python3 /usr/src/app/run.py)

# Mask the output in the logs
echo "::add-mask::$output"

# Extract environment variables from the output
env_vars=$(echo "$output" | grep -E 'SLACK_THREAD_TS|SLACK_CHANNEL|SLACK_MESSAGE_ID')

# Set the output as environment variables
echo "$env_vars" >> $GITHUB_ENV