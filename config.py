from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from data import TOKEN
from dotenv import load_dotenv


load_dotenv()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
text_task_input = False
image_task_input = False


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton('Текст'))
keyboard.add(types.KeyboardButton('Изображение'))