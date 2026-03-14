import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("IG_USER")
PASSWORD = os.getenv("IG_PASS")

WELCOME_MSG = "🎉 Welcome {name} to the group!"
PING_MSG = "👀 {mentions} কেউ online আছো?"

INACTIVE_HOURS = 3
PING_USERS = 4
