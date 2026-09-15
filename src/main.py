import os
from dotenv import load_dotenv
from src.bot import client
from src.log_instance import logger
import src.events  # noqa: F401
import src.commands  # noqa: F401

load_dotenv()

token = os.environ.get("BOT_TOKEN")
if not token:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise SystemExit(1)

client.run(token, log_handler=None)