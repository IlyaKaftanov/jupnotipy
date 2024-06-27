# JupNotiPy

Simple class for Python Telegram bot notifications, ideal for Jupyter notebooks and long-running scripts.

## How this works

JupNotiPy uses your Telegram bot to send you messages. The process involves two main steps:

1. Initialization: Required for obtaining a chat_id.
2. Sending: Used for sending notifications through the given bot.

### Basic usage scenario:

1. Create a Telegram bot and get the bot token.
2. Initialize the notifier in a Jupyter notebook or any long-running script.
3. Send a message after work is done.

```python
from jupnotipy import TNotifier

notifier = TNotifier(bot_token="YOUR_BOT_TOKEN")
notifier.init_notification()

# do some work or execute jupyter cells

notifier.notify(text="Define some text to send after work is done")
```

### Advanced usage scenario:

1. After the first initialization, you obtain your chat_id for the bot.
2. Pass this chat_id on initialization to skip the initialization part.
3. Use as usual.

```python
from jupnotipy import TNotifier

notifier = TNotifier(bot_token="YOUR_BOT_TOKEN", chat_id=00000, username="MyLord")

notifier.notify(text="")
```

## Security Note

- The initialization process uses a unique text (UUID) to identify the user, which provides a basic level of security.
- However, users should be cautious about sharing their bot tokens or chat IDs.

## Limitations

- The polling mechanism in init_notification() has a default timeout, which can be adjusted using the polling_freq
  parameter.
- The module assumes a stable internet connection for API communication.