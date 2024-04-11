from graphics import photo_input
# text_task_input, image_task_input нужны для первого случайного сообщения пользователя, хоть и отмечаются как ненужные
from config import bot, dp, text_task_input, image_task_input
from physics import physics_calc, chat_to_machine_condition_forming, provided_values_forming, \
    machine_to_chat_condition_forming
from aiogram import types
from copy import deepcopy


@dp.message_handler(commands=['start', 'help'])
async def greetings(message):
    await bot.send_message(message.from_user.id, f'Привет, {message.from_user.full_name}, я ‍бот🤖 для помощи с '
                                                 'решением✅ физических задач.')
    await input(message)


async def input(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ('Текст', 'Изображение')
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Выбери способ ввода условия задачи, '
                           'и я попытаюсь помочь тебе ее решить 😼', reply_markup=keyboard)


@dp.message_handler(regexp='Текст')
async def start(message):
    global text_task_input
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.from_user.id, 'Введи текст задачи📝:', reply_markup=markup)
    text_task_input = True


@dp.message_handler(regexp='Изображение')
async def start(message):
    global image_task_input
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.from_user.id, 'Загрузи изображение задачи📷:', reply_markup=markup)
    image_task_input = True


@dp.message_handler(regexp='Да, решение верное')
async def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ('Вернуться в главное меню', 'Продолжить решать задачи')
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Отлично! Ты можешь продолжить решать задачи или вернуться в '
                                                 'главное меню.', reply_markup=keyboard)


@dp.message_handler(regexp='Продолжить решать задачи')
async def start(message):
    await input(message)


@dp.message_handler(regexp='Вернуться в главное меню')
async def start(message):
    global phys_formula_input
    global phys_value_input
    global text_task_input
    global image_task_input
    phys_formula_input = False
    phys_value_input = False
    image_task_input = False
    text_task_input = False

    await greetings(message)


@dp.message_handler(regexp='Нет, изменить задачу')
async def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ('Добавить недостающую физическую величину в Дано', 'Убрать лишнюю физическую величину в Дано',
               'Запретить неподходящую формулу в решении', 'Добавить недостающую формулу в решении',
               'Изменить вопрос задачи')
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Укажи на мою ошибку одним из предложенных способов и я постараюсь ее '
                                                 'исправить!',
                           reply_markup=keyboard)


@dp.message_handler(regexp='Добавить недостающую формулу в решении')
async def start(message):
    global phys_formula_input
    await bot.send_message(message.from_user.id, 'Введи физическую величину и ее формулу в формате:    '
                                                 'Формула: [Физическая величина] = [формула]')
    phys_formula_input = True


@dp.message_handler(regexp='Запретить неподходящую формулу в решении')
async def start(message):
    global response
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Запретить формулу №' + str(i + 1) for i in range(len(response[2].split('\n')))]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Выбери номер формулы, которую нужно запретить', reply_markup=keyboard)


@dp.message_handler(regexp='Добавить недостающую физическую величину в Дано')
async def start(message):
    global phys_value_input
    await bot.send_message(message.from_user.id, 'Введи физическую величину и ее значение в формате:   '
                                                 'Величина: [Физическая величина] = [значение] [единицы измерения]')
    phys_value_input = True


@dp.message_handler(regexp='Убрать лишнюю физическую величину в Дано')
async def start(message):
    global response
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Убрать ' + elem[3:].split()[0] for elem in response[0].split('\n')]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Выбери физическую величину, которую хочешь удалить',
                           reply_markup=keyboard)


@dp.message_handler(regexp='Формула: ')
async def start(message):
    global phys_formula_input
    if phys_formula_input:
        global response
        print('response:', response)
        provided_values, requested_values, formulas, result_formula, expr, db_info = \
            await chat_to_machine_condition_forming(response)
        global new_db_info
        new_db_info = deepcopy(db_info)
        value, formula = message.text.replace('Формула: ', '').split(' = ')
        new_db_info.insert(0, (value, formula, '', None))
        requested_values.insert(0, (value, formula, '', None))
        response = await machine_to_chat_condition_forming(provided_values, requested_values, 0,
                                                           provided_formulas=formulas,
                                                           provided_result_formula=result_formula, provided_expr=expr,
                                                           db_info=db_info)
        print('new_db_info')
        print(*new_db_info)

        await confirm_changes_question(message)

    phys_formula_input = False


@dp.message_handler(regexp='Запретить')
async def start(message):
    global response
    global forbidden_formula
    print('Запретить формулу №')
    provided_values, requested_values, formulas, result_formula, expr, db_info = \
        await chat_to_machine_condition_forming(response)
    n = str(message.text.split()[2][1:])
    formulas = formulas.split('\n')
    for i in range(len(formulas)):
        print(formulas[i], n)
        if formulas[i].startswith(n):
            forbidden_formula = [formulas[i].split()[-1]]
            print('forbidden_formula', forbidden_formula)
            break

    await confirm_changes_question(message)


@dp.message_handler(regexp='Убрать')
async def start(message):
    global response
    provided_values, requested_values, formulas, result_formula, expr, db_info = \
        await chat_to_machine_condition_forming(response)
    provided_values.pop(message.text.split()[1])
    response = await machine_to_chat_condition_forming(provided_values, requested_values, 0, provided_formulas=formulas,
                                                       provided_result_formula=result_formula, provided_expr=expr,
                                                       db_info=db_info)
    await confirm_changes_question(message)


@dp.message_handler(regexp='Величина: ')
async def start(message):
    global phys_value_input
    if phys_value_input:
        global response
        print('response:', response)
        provided_values, requested_values, formulas, result_formula, expr, db_info = \
            await chat_to_machine_condition_forming(response)
        provided_values = provided_values | await provided_values_forming(message.text.replace('Величина: ', ''))
        print('provided_values:', provided_values)
        print('formulas:', formulas)
        response = await machine_to_chat_condition_forming(provided_values, requested_values, 0,
                                                           provided_formulas=formulas,
                                                           provided_result_formula=result_formula, provided_expr=expr,
                                                           db_info=db_info)
        await confirm_changes_question(message)

    phys_value_input = False


async def confirm_changes_question(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ('Да, реши задачу', 'Нет, изменить задачу')
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, 'Это все изменения, которые ты бы хотел внести?',
                           reply_markup=keyboard)


@dp.message_handler(regexp='Да, реши задачу')
async def confirm_changes(message):
    global forbidden_formula
    global new_db_info
    try:
        print(forbidden_formula)
    except:
        forbidden_formula = []
    try:
        print(new_db_info)
    except:
        new_db_info = None
    print('confirm_changes - response', response)
    await solving_physical_task(message, resp=response, ignore_formulas=forbidden_formula, new_db_info=new_db_info)


@dp.message_handler(content_types=['photo'])
async def start(message):
    global image_task_input
    if image_task_input:
        img = message.photo[-1]
        await img.download(destination_file='C:/Users/t106o/PycharmProjects/UchiDomaProject/test_imgs/img.jpg')
        text = await photo_input()
        text = text.replace('\n', '').replace('\r', ' ')
        await bot.send_message(message.from_user.id,
                               f'Текст📄 вашей задачи:\n{text}')
        await solving_physical_task(message)
        image_task_input = False


async def solving_physical_task(message, resp=None, ignore_formulas=None, new_db_info=None):
        bot_message = await bot.send_message(message.from_user.id, 'Ожидайте...')
        global response
        if not resp:
            response = await physics_calc(text=message.text)
        else:
            provided_values, requested_values, formulas, result_formula, expr, db_info = \
                await chat_to_machine_condition_forming(resp)
            response = await physics_calc(provided_values=provided_values, requested_values=requested_values,
                                          ignore_formulas=ignore_formulas, db_info=new_db_info)
        if response:
            given, to_find, formulas, result_formula, expr, provided_values, requested_values, db_info = response
            await bot.edit_message_text(chat_id=bot_message.chat.id, message_id=bot_message.message_id,
                                        text='✅Решение твоей задачи👇💯:\n'
                                             'Дано:\n'
                                             f'{given}\n'
                                             'Найти:\n'
                                             f'{to_find}\n'
                                             'Решение:\n'
                                             f'{formulas}\n'
                                             'Итоговая формула:\n'
                                             f'{result_formula}\n'
                                             'Ответ:\n'
                                             f'{expr}')

            """
            await bot.send_message(message.from_user.id,
                           f'✅Вот подходящие формулы📃 для решения твоей задачи👇💯:\n{", ".join(formuls)}')
            """
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ('Да, решение верное', 'Нет, изменить задачу', 'Вернуться в главное меню')
            keyboard.add(*buttons)
            await bot.send_message(message.from_user.id,
                                   'Правильно ли я решил твою задачу?',
                                   reply_markup=keyboard)
            """
            await bot.send_message(message.from_user.id,
                                   '🤠Я готов помочь с решением всех твоих задач! Вводи следующую😤 ',
                                   reply_markup=keyboard)
            """
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.KeyboardButton('Вернуться в главное меню'))
            await bot.send_message(message.from_user.id,
                                   'К сожалению я не смог решить твою задачу. Она отправлена в бак с другими '
                                   'сложными задачами, но не расстраивайся, скоро меня научат решать и такие '
                                   'задачи. Приходи в следующий раз!',
                                   reply_markup=keyboard)



@dp.message_handler()
async def some_send(message):
    global text_task_input
    if text_task_input:
        await solving_physical_task(message)
        text_task_input = False
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('Вернуться в главное меню'))
        await bot.send_message(message.from_user.id, '❌Я еще не знаю такой команды', reply_markup=keyboard)
