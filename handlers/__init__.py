from graphics import photo_input
from config import bot, keyboard, dp, text_task_input, image_task_input
from physics import physics_calc
import time
import random
from threading import Thread


async def m_loading(m):
    print('m_loading')
    loading = 15
    for count in range(100):
        loading += count + random.randint(1, 15)  # рандомно добавляем загрузку
        if loading >= 100:
            await bot.edit_message_text(chat_id=m.chat.id, message_id=m.message_id,
                                  text=f"Обработка завершена... 100%")
            break  # останавливаем цикл
        await bot.edit_message_text(chat_id=m.chat.id, message_id=m.message_id,
                              text=f"{m.text} {loading}%")  # изменяем сообщение
        time.sleep(1)  # задержка


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    await bot.send_message(message.from_user.id, 'Привет, я ‍бот🤖 для помощи с решением✅ физических задач.'
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
        try:
            Thread(target=m_loading, args=(await bot.send_message(message.chat.id, "Идёт обработка..."), )).start()
            """
            m = await bot.send_message(message.chat.id, "Идёт обработка...")
            await m_loading(m)
            """
            responce = await physics_calc(message.text)
            if responce:
                given, to_find, formulas, result_formula, expr = responce
                await bot.send_message(message.from_user.id,
                                       '✅Решение твоей задачи👇💯:\n'
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
                await bot.send_message(message.from_user.id,
                                       'Правильно ли я решил твою задачу?',
                                       reply_markup=keyboard)
                await bot.send_message(message.from_user.id,
                                       '🤠Я готов помочь с решением всех твоих задач! Вводи следующую😤 ',
                                       reply_markup=keyboard)
            else:
                await bot.send_message(message.from_user.id,
                                       'К сожалению я не смог решить твою задачу. Она отправлена в бак с другими '
                                       'сложными задачами, но не расстраивайся, скоро меня научат решать и такие '
                                       'задачи. Приходи в следующий раз!',
                                       reply_markup=keyboard)
                text_task_input = False
        except:
            await bot.send_message(message.from_user.id,
                                   'К сожалению я не смог решить твою задачу. Она отправлена в бак с другими сложными '
                                   'задачами, но не расстраивайся, скоро меня научат решать и такие задачи. Приходи в '
                                   'следующий раз!',
                                   reply_markup=keyboard)
            text_task_input = False
    else:
        await bot.send_message(message.from_user.id, '❌Я еще не знаю такой команды')
