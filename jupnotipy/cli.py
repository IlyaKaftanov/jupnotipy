import argparse

from .core import login, notify


def init(bot_token: str):
    login(bot_token)
    print(
        "If you got some messages from bot everything is ready. Try to send message manually"
    )


def send(text: str):
    notify(text)


def main():
    parser = argparse.ArgumentParser(description="jupnotipy CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init", help="Initialize jupnotipy notifier")
    parser_init.add_argument(
        "--bot_token", type=str, required=True, help="Telegram bot token."
    )
    parser_init.set_defaults(func=lambda args: init(args.bot_token))

    parser_send = subparsers.add_parser("send", help="Send a message")
    parser_send.add_argument(
        "--text", type=str, default="", help="User defined text to send"
    )
    parser_send.set_defaults(
        func=lambda args: send(
            args.text,
        )
    )

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
