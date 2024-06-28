# JupNotiPy

Simple class for Python Telegram bot notifications, ideal for Jupyter notebooks and long-running scripts.

## Features

1. Easy setup: Quickly initialize your Telegram bot and get your chat_id.
2. Customizable notifications: Send messages with custom text.
3. Credential management: Cache and manage your bot credentials seamlessly.

## How this works

JupNotiPy uses your Telegram bot to send you messages. The process involves two main steps:

1. Initialization: Required for obtaining a chat_id.
2. Sending: Used for sending notifications through the given bot.

## Installation

Install JupNotiPy using pip:

```shell
pip install jupnotipy
```

### CLI Usage

#### Step 1: Initialize and Obtain chat_id

To initialize JupNotiPy and obtain your chat_id, use the following command:

```shell
jupnotipy init --bot_token "YOUR_BOT_TOKEN"
```

This will create a credentials file for future use.

#### Step 2: Send a Message

To send a message using the CLI:

```shell
jupnotipy send
```

Or, to send a custom message:

```shell
jupnotipy send --text "MY FANCY MESSAGE"
```

### Python API

#### Step 1: Login and Initialize

To log in and initialize JupNotiPy within your Python script:

```python
import jupnotipy

jupnotipy.login(bot_token="YOUR_BOT_TOKEN")
```

#### Step 2: Send Notifications

Use cached credentials to send a notification:

```python
jupnotipy.notify()
```

Override cached credentials and send a notification:

```python
jupnotipy.notify(bot_token="YOUR_BOT_TOKEN", chat_id=0)
```

Send a custom message:

```python
jupnotipy.notify(message="MY_FANCY_MESSAGE")
```

Update cached credentials:

```python
jupnotipy.notify(bot_token="YOUR_BOT_TOKEN", chat_id=0, update_credentials=True)
```

### Example Code

Here's a sample Python script using JupNotiPy:

```python
import jupnotipy

jupnotipy.login(bot_token="YOUR_BOT_TOKEN")

# use cached credentials
jupnotipy.notify()

# override the cached credentials
jupnotipy.notify(bot_token="YOUR_BOT_TOKEN", chat_id=0)

# define custom message
jupnotipy.notify(message="MY_FANCY_MESSAGE")

# update cached credentials
jupnotipy.notify(bot_token="YOUR_BOT_TOKEN", chat_id=0, update_credentials=True)
```
