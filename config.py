from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from data import TOKEN
from dotenv import load_dotenv
import sqlite3
from typing import List, Tuple, NewType


Value = NewType('Value', str)
Formula = NewType('Formula', str)
Units = NewType('Units', str)
Name = NewType('Name', str)


def collect_info() -> List[Tuple[Value, Formula, Units, Name]]:
    conn = sqlite3.connect('C:/Users/t106o/PycharmProjects/Shcool Project/Physical_formulas.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT value, kinematics_formulas.formula, units, name FROM "values", "kinematics_formulas"
                            WHERE id = kinematics_formulas.value_id
                     ''')
    db = cursor.fetchall()

    cursor.execute('''SELECT value, dynamics_formulas.formula, units, name FROM "values", "dynamics_formulas"
                            WHERE id = dynamics_formulas.value_id
                     ''')
    db += cursor.fetchall()

    cursor.execute('''SELECT value, hydrostatics_formulas.formula, units, name FROM "values", "hydrostatics_formulas"
                            WHERE id = hydrostatics_formulas.value_id
                     ''')
    db += cursor.fetchall()

    cursor.execute('''SELECT value, units, name FROM "values"
                                WHERE id NOT IN (SELECT value_id FROM kinematics_formulas) AND
                                id NOT IN (SELECT value_id FROM dynamics_formulas) AND
                                id NOT IN (SELECT value_id FROM hydrostatics_formulas)
                         ''')

    data = cursor.fetchall()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i].insert(1, False)

    db += data

    conn.close()

    return db

"""
db = collect_info()
for elem in db:
    print(elem)
"""
load_dotenv()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
text_task_input = False
image_task_input = False
question_words = ('определить', 'сколько', 'найти', 'какой', 'какая', 'какое')
db_info = collect_info()
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


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton('Текст'))
keyboard.add(types.KeyboardButton('Изображение'))