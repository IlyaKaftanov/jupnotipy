import logging
import os
import time
import uuid

import requests

from .funny_messages import generate_funny_login_message, get_random_notification_text

# init logger
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# global vars
TELEGRAM_BASE_URL = "https://api.telegram.org/bot{bot_token}/"


def get_recent_messages(bot_token, offset=0, limit=20):
    params = {"offset": offset, "limit": limit}
    response = requests.get(
        TELEGRAM_BASE_URL.format(bot_token=bot_token) + "getUpdates", params=params
    )

    if response.status_code == 200:
        data = response.json()
        if data["ok"]:
            return data["result"]
        else:
            logger.error("request error: %s", data["description"])
            return None
    else:
        logger.error(
            "Failed to retrieve updates error, response code: %s", response.status_code
        )
        return None


def send_telegram_message(bot_token: str, chat_id: int, message: str):
    send_message_url = TELEGRAM_BASE_URL.format(bot_token=bot_token) + "sendMessage"

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    response = requests.post(send_message_url, json=payload)

    if response.status_code == 200:
        logger.info("Message sent successfully!")
        return True
    else:
        logger.warning(
            "Failed to send message. Status code: %s with response: %s",
            response.status_code,
            response.text,
        )
        return False


class CredentialsCache:
    credentials_path: str = os.path.join(os.path.expanduser("~"), ".jupnotipy")

    @staticmethod
    def exists():
        return os.path.exists(CredentialsCache.credentials_path)

    @staticmethod
    def save_credentials(credentials: dict):
        if "chat_id" not in credentials:
            raise ValueError("missing chat_id")

        # update credentials if not key exists
        # to keep the ability of insert-update like style savings
        if os.path.exists(CredentialsCache.credentials_path):
            prev_credentials = CredentialsCache.load_credentials()
            for key in prev_credentials:
                if key not in credentials:
                    credentials[key] = prev_credentials[key]

        with open(CredentialsCache.credentials_path, "w") as f:
            for key, value in credentials.items():
                f.write(f"{key}={value}\n")

    @staticmethod
    def load_credentials() -> dict:
        data = {}
        if not os.path.exists(CredentialsCache.credentials_path):
            return data

        with open(CredentialsCache.credentials_path, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                data[key] = value
        return data


def login(bot_token: str, polling_freq: int = 3, num_retries: int = 10):
    awaited_text = str(uuid.uuid4())
    logger.info(
        "Please send a text '%s' to you bot. Time left: %s sec",
        awaited_text,
        polling_freq * num_retries,
    )
    chat_id = 0
    while num_retries:
        recent_messages = get_recent_messages(bot_token)
        if recent_messages:
            for update in recent_messages:
                if "message" in update:
                    message = update["message"]
                    message_text = message.get("text", "")
                    # potentially, you could brute-force the uuid, but it's protected
                    # from telegram side.
                    if awaited_text in message_text:
                        chat_id = message["chat"]["id"]
                        break
        time.sleep(polling_freq)
        num_retries -= 1
        logger.info(
            "Send message to you bot around %d sec time left.",
            num_retries * polling_freq,
        )

    if chat_id:
        status = send_telegram_message(
            bot_token, chat_id, generate_funny_login_message()
        )
        if not status:
            logger.info("Failed to send message, please check logs above")
        else:
            CredentialsCache.save_credentials(
                {"chat_id": chat_id, "bot_token": bot_token}
            )
    else:
        logger.error("Failed to obtain chat_id.")


def notify(
    bot_token: str = "",
    chat_id: int = 0,
    message: str = "",
    update_credentials: bool = False,
):
    credentials = CredentialsCache.load_credentials()
    if not bot_token:
        bot_token = credentials.get("bot_token", "")
    if not chat_id:
        chat_id = credentials.get("chat_id", 0)

    if not bot_token or not chat_id:
        raise ValueError("Login first or check the passed `bot_token` and `chat_id`")

    if not message:
        message = get_random_notification_text()

    status = send_telegram_message(bot_token, chat_id, message)
    if not status:
        logger.info("Failed to send message, please check logs above")
    elif status and update_credentials:
        CredentialsCache.save_credentials({"chat_id": chat_id, "bot_token": bot_token})
