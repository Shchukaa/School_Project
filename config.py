from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from data import TOKEN
from dotenv import load_dotenv


load_dotenv()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
text_task_input = False
image_task_input = False
question_words = ('определить', 'записать', 'сколько', 'найти', 'какой', 'какая', 'какое')
synonym_words = ['расстояние;длина;путь']
ci_units = {
    'К': 10**3,
    'к': 10**3,
    'М': 10*6,
    'д': 10**-1,
    'с': 10**-2,
    'м': 10**-3,
    'н': 10**-9
}