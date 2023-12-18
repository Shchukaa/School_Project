import re
import difflib
from language import infinitive, inflecting
from config import question_words, synonym_words
from config import db_info
import asyncio


# Выделение физических величин из текста
async def input_corr(text: str) -> list:
    numbers = re.findall(r'\d+(?:,*\d+)*(?:[\-\+]\d+)*\s[а-яА-Я]+(?:\/(?:[а-я])+)*\d*', text)
    # units_transfrom()
    return numbers


# Проверка совпадения
async def similarity(s1: str, s2: str) -> float:
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


"""
# Доделать функцию перевода единиц измерения
def units_transform(numbers: list) -> list:
    for i in range(len(numbers)):
        number = numbers[i].split()[0]
        unit = numbers[i].split()[1]
        for un in ci_units:
            if un in unit and (unit.replace(un, '') in units or len(unit.replace(un, '')) == 0):
                if un == 'с' and unit[2] != 'м':
                    pass
                else:
                    unit = unit.replace(un, '')
                    number = int(number) * ci_units[un]
                print(un, unit, number)
"""


# Основная функция
async def physics_calc(text: str) -> list:
    units = map(lambda x: x.split()[1], await input_corr(text))
    print(*units)

    """
    # Можно сделать из этого дополнительную проверку
    # Не работает, т.к. есть разные величины с одними и теми же единицами измерения
    # Добавление формул по совпадениям единиц измерений
    res = []
    for elem in units:
        for unit in result:
            if unit[3] == elem:
                if unit[1] is not None:
                    res.append(unit[0] + ' = ' + unit[1])
                if unit[2] is not None:
                    res.append(unit[0] + ' = ' + unit[2])
    """

    # Вычисление совпадений

    # Для начала создаем список из инфинитивов слов запроса и их склоненией
    inf_l = []
    infl_l = []
    text = text.replace('.', ' ').replace(',', ' ').lower().split()
    print(text)
    for i in range(len(text) - 1):
        inf = infinitive(text[i])
        inf_l.append(inf)
        infl = inflecting(text[i], text[i + 1])
        infl_l.append(infl)
    inf_l.append(infinitive(text[-1]))
    print(inf_l)
    print(infl_l)
    """ 
    # Можно сделать проверку из этого на человеческий фактор(неправильное написание 1-2 букв)
    cursor.execute('''SELECT name FROM "values"''')
    names = tuple(map(lambda x: x[0], cursor.fetchall()))

    sims = []
    for word in inf_l:
        pairs_sim = tuple(filter(lambda x: x[2] >= 0.95,
                                 [(name, word, await similarity(name, word)) for name in names]))
        if pairs_sim:
            print(pairs_sim)
            sims.append(pairs_sim[0][0])
    """

    # Добавление формул по совпадениям слов + поиск спрашиваемой величины
    # Важно проверять не пару предыдущий+текущий, а пару текущий+следующий, чтобы избежать лишних физических величин
    # Пример:
    # Сила упругости -> сила, сила упругости.
    # Переложить всю обработку в модуль math
    res = []

    # Идентификация спрашиваемых величин(identification requested values)
    irv = False

    # Индикатор отработки двойного запроса
    # (Очевидно, что если в цикле нашлась физическая величина с именем текущее слово + следующее слово, то
    # следующее слово отдельно нам не нужно проверять как одиночный запрос, например:
    # Текущее слово средняя, следующее слово скорость
    # Найдено: средняя скорость -> пропуск следующего цикла со словом скорость
    double_value = False

    print(*db_info, sep='\n')

    value_names = set([value[3] for value in db_info])
    # Данные величины
    provided_values = {}
    # Спрашиваемые величины
    requested_values = []
    # Возможные формулы
    required_values = {}

    for i in range(len(inf_l)):
        if double_value:
            double_value = False
        elif len(inf_l[i]) > 3 and not inf_l[i].isdigit():
            print('-' + inf_l[i] + '-')

            # Индикатор вопроса
            if inf_l[i] in question_words:
                print('------------')
                print('irv')
                print('------------')
                irv = True

            # Проверка на синонимичную идентичность с последующей заменой слова на аналог, представленный в базе данных
            if inf_l[i] in ';'.join(synonym_words):
                for elem in synonym_words:
                    if inf_l[i] in elem:
                        inf_l[i] = elem.split(';')[0]

            # Выделение формул из текста путем проверки совпадения для всех значений из базы данных
            for value in db_info:
                print('Cycle:', value[3], '-', inf_l[i])
                if i != len(inf_l) - 1:
                    print(text[i], inf_l[i + 1])
                    # Проверка на составной запрос (текущее слово + следующее слово)
                    if infl_l[i] and (infl_l[i] + ' ' + inf_l[i + 1] == value[3]
                                      or inf_l[i] + ' ' + text[i + 1] == value[3]
                                      or text[i] + ' ' + text[i + 1] == value[3]):
                        print('Составной запрос:', text[i] + ' ' + inf_l[i + 1])

                        double_value = True

                        required_values, requested_values = await request_check(irv, value, requested_values,
                                                                                required_values)
                        # res.append(value[0] + ' = ' + value[1])

                    # Проверка на одиночный запрос (текущее слово)
                    elif inf_l[i] == value[3]:
                        print('Одиночный запрос:', inf_l[i])
                        required_values, requested_values = await request_check(irv, value, requested_values,
                                                                                required_values)
                        # res.append(value[0] + ' = ' + value[1])
                else:
                    # В последнем цикле делаем проверку только на одиночный запрос без составления условия
                    if inf_l[i] == value[3]:
                        print('Одиночный запрос:', inf_l[i])
                        required_values, requested_values = await request_check(irv, value, requested_values,
                                                                                required_values)
                        # res.append(value[0] + ' = ' + value[1])
            # irv = False

            # Нахождение данных величин
            if inf_l[i] in value_names and i < len(inf_l) - 3:
                provided_values = await value_collecting(provided_values, inf_l, i)
            print('----------')
            print(f'provided_values: {provided_values}')
            print('----------')

    if requested_values:
        requested_values = list(dict.fromkeys(requested_values))
        print('Найти:')
        for elem in requested_values:
            print(elem[0] + ' - ' + elem[3])
    else:
        print('Не могу определить вопрос')

    for key in required_values:
        required_values[key] = list(dict.fromkeys(required_values[key]))
    print(f'required_values: {required_values}')

    for value in required_values:
        for formula in required_values[value]:
            res.append(value + ' = ' + formula)
    print(f'requested_values: {requested_values}')
    print(f'provided_values: {provided_values}')

    return res


async def value_collecting(provided_values, inf_l, i, value=None):
    for elem in db_info:
        if inf_l[i] in elem:
            value = elem[0]
            break

    if value:
        for k in range(1, 4):
            if inf_l[i + k].isdigit():
                # Если в словаре с условием уже существует запись о такой физической величине, то
                # мы перезаписываем эту запись на значение количества данных в условии таких физических величин,
                # а для самих физических величин мы делаем отдельные номера(начинающиеся с 0) и записи в словаре
                # Например:
                # В условии даны 3 скорости: 10, 20, 30
                #   С прочтением программой первой скорости будет создана запись 'v': '10'
                #   С прочтением второй будет перезаписана запись 'v': '10' на 'v': 1, и будут созданы записи:
                # 'v0': '10' и 'v1': '20'; Запись 'v': 1 будет означать, что есть уже 2 физические величины 'v'
                #   При прочтении третьей скорости будет изменена запись с количеством скоростей на: 'v': 2,
                # и создана еще одна запись 'v3': '30'
                if value in provided_values:
                    if type(provided_values[value]) == str:
                        provided_values[value + '0'] = provided_values[value]
                        provided_values[value + '1'] = inf_l[i + k]
                        provided_values[value] = 1
                    else:
                        provided_values[value] += 1
                        provided_values[value + str(provided_values[value])] = inf_l[i + k]
                else:
                    provided_values[value] = inf_l[i + k]
                break
    else:
        raise ValueError(f'Такой физической величины не существует: {inf_l[i]}')

    return provided_values


async def request_check(irv, value, requested_values, required_values):
    if irv:
        requested_values.append(value)
        print('------------')
        print(requested_values)
        print('------------')
    else:
        if value[0] in required_values:
            required_values[value[0]].append(value[1])
        else:
            required_values[value[0]] = [value[1]]

    return required_values, requested_values


async def finding_formulas(value: str) -> str:
    pass


async def value_selecting(formula):
    pass


asyncio.run(physics_calc('Первую половину пути автомобиль двигается со скоростью 60 км/ч, а вторую - со скоростью 40 '
                         'км/ч. Найдите среднюю скорость движения автомобиля на всем пути.'))
