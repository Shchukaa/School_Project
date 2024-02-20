from graphics import photo_input
from config import bot, keyboard, dp, text_task_input, image_task_input
from physics import physics_calc


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    await bot.send_message(message.from_user.id, 'Привет, я ‍бот🤖 для помощи с решением✅ физичских задач.'
                                                 ' Выбери способ ввода условия задачи, и я попытаюсь помочь'
                                                 ' тебе ее решить 😼', reply_markup=keyboard)


@dp.message_handler(regexp='Текст')
async def start(message):
    global text_task_input
    await bot.send_message(message.from_user.id, 'Введи текст задачи📝:')
    text_task_input = True


@dp.message_handler(regexp='Изображение')
async def start(message):
    global image_task_input
    await bot.send_message(message.from_user.id, 'Загрузи изображение задачи📷:')
    image_task_input = True


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
        responce = await physics_calc(text)
        """
        await bot.send_message(message.from_user.id,
                               f'✅Вот подходящие формулы📃 для решения твоей задачи👇💯:\n{", ".join(formuls)}')
        """
        await bot.send_message(message.from_user.id,
                               f'✅Решение твоей задачи👇💯:{responce}')

        await bot.send_message(message.from_user.id,
                               f'🤠Я готов помочь с решением всех твоих задач! Вводи следующую😤 ',
                               reply_markup=keyboard)
        image_task_input = False


@dp.message_handler()
async def some_send(message):
    global text_task_input
    if text_task_input:
        responce = await physics_calc(message.text)
        await bot.send_message(message.from_user.id,
                               f'✅Решение твоей задачи👇💯:{responce}')
        """
        await bot.send_message(message.from_user.id,
                               f'✅Вот подходящие формулы📃 для решения твоей задачи👇💯:\n{", ".join(formuls)}')
        """
        await bot.send_message(message.from_user.id,
                               f'🤠Я готов помочь с решением всех твоих задач! Вводи следующую😤 ',
                               reply_markup=keyboard)
        text_task_input = False
    else:
        await bot.send_message(message.from_user.id, '❌Я еще не знаю такой команды')
