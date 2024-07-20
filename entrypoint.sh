#!/bin/sh -l

# Extract inputs from 'with' GitHub context using the INPUT_ prefix
export SLACK_WEBHOOK="${INPUT_SLACK_WEBHOOK}"
export STATUS="${INPUT_STATUS}"
export AUTHOR_NAME="${INPUT_AUTHOR_NAME:-"GitHub Action"}"
export AUTHOR_LINK="${INPUT_AUTHOR_LINK:-""}"
export AUTHOR_ICON="${INPUT_AUTHOR_ICON:-""}"
export TITLE="${INPUT_TITLE:-"Build Notification"}"
export TITLE_LINK="${INPUT_TITLE_LINK:-""}"
export MESSAGE="${INPUT_MESSAGE:-"Notification from GitHub Action"}"
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

# Run the Python script with the provided inputs and capture the output
output=$(python3 /usr/src/app/run.py)

# Mask the output in the logs
echo "::add-mask::$output"

# Debugging: Print the output to check its content
echo "Output from Python script: $output"

# Extract environment variables from the output
env_vars=$(echo "$output" | grep -E 'SLACK_THREAD_TS|SLACK_CHANNEL|SLACK_MESSAGE_ID')

# Debugging: Print the extracted environment variables
echo "Extracted environment variables: $env_vars"

# Set the output as environment variables
echo "$env_vars" >> $GITHUB_ENV

# Debugging: Print the content of the GITHUB_ENV file after writing
echo "Content of GITHUB_ENV after writing:"
cat $GITHUB_ENV