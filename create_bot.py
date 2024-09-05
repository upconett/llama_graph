from aiogram import Bot, Dispatcher

from llm import LLM
from database import Database
import config


bot = Bot(
    token=config.TOKEN
)

dp = Dispatcher()

llm = LLM(config.LLAMA_IP)

db = Database(config.DB_FILE)