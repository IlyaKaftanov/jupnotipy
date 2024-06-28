import random


def get_random_notification_text() -> str:
    items = [
        "🐔 a rubber chicken",
        "🧥 an invisible cloak",
        "🦄 a magical unicorn",
        "🧞‍♂️ a flying carpet",
        "🐶 a talking dog",
        "🐹 a ninja hamster",
        "💃 a disco ball",
        "🧁 a giant cupcake",
        "🦜 a pirate parrot",
        "🤖 a dancing robot",
        "⏳ a time-traveling toaster",
        "🎩 a wizard's hat",
    ]

    actions = [
        "💃 danced around",
        "🎤 sang a song",
        "🪄 performed a magic trick",
        "💃 started a conga line",
        "🔥 juggled flaming torches",
        "🤸‍♂️ did a backflip",
        "📢 gave a motivational speech",
        "👀 won a staring contest",
        "🔍 solved a mystery",
        "🎂 baked a giant cake",
        "🚀 built a spaceship",
        "🕺 invented a new dance move",
    ]

    item = random.choice(items)
    action = random.choice(actions)

    notification_text = f"✨ <b>Work is done even when</b> <i>{item.capitalize()} {action}!</i> ✨"
    return notification_text


def generate_funny_login_message():
    messages = [
        "Welcome back, superstar! 🌟",
        "Look who's here! The party can start now! 🎉",
        "You made it! Let's do this! 🚀",
        "Access granted. Time to conquer the world! 🦸‍♂️",
        "Guess who's back, back again... You are! 😎",
        "You're in! Time to unleash your inner ninja. 🥷",
        "Welcome aboard, Captain! 🛳️",
        "The legend has returned! 🏆",
        "You're in! Let's make some magic happen. ✨",
        "All systems go! Welcome back, hero! 💪",
        "Login successful. Adventure awaits! 🗺️",
        "You did it! Ready to rock and roll? 🎸",
        "Welcome back, master of the universe! 🌌",
        "Access granted. Prepare for awesomeness! 🚀",
        "Look out world, [Your Name] is back! 🌍",
    ]
    return random.choice(messages)
