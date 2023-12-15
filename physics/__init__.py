import re
import difflib
from language import infinitive, inflecting
from config import question_words, synonym_words
from config import db_info


# Выделение физических феличин из текста
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
def units_tranfrom(numbers: list) -> list:
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

    # Для начала создаем список из инфинитивов слов запроса
    inf_l = []
    text = text.replace('.', ' ').replace(',', ' ').lower().split()
    print(text)
    for word in text:
        inf = infinitive(word)
        inf_l.append(inf)
    print(inf_l)
    """ 
    # Можно сделать проверку из этого на человеческий фактор(неправильное написнаие 1-2 букв)
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
    # Сила упругости -> сила, сила упругости
    # Запихнуть всю обработку в модуль math
    res = []

    # Идентификация спрашиваемых величин(identification requested values)
    irv = False

    requested_value = None
    print(*db_info, sep='\n')
    required_values = {}
    for i in range(len(inf_l)):
        if len(inf_l[i]) > 3 and not inf_l[i].isdigit():
            print('-' + inf_l[i] + '-')

            if inf_l[i] in question_words:
                print('------------')
                print('irv')
                print('------------')
                irv = True

            if inf_l[i] in ';'.join(synonym_words):
                for elem in synonym_words:
                    if inf_l[i] in elem:
                        inf_l[i] = elem.split(';')[0]

            for line in db_info:
                print('Cycle:', line[3], '-', inf_l[i])
                if i != len(inf_l) - 1:
                    print(text[i], inf_l[i + 1])
                    print(re.fullmatch(r"[а-яА-я]{3,}", text[i]), re.fullmatch(r"[а-яА-я]{3,}", inf_l[i + 1]))
                    if re.fullmatch(r"[а-яА-я]{3,}", text[i]) and re.fullmatch(r"[а-яА-я]{3,}", inf_l[i + 1]) \
                        and (inflecting(text[i], inf_l[i + 1]) + ' ' + inf_l[i + 1] == line[3]
                             or inf_l[i] + ' ' + text[i + 1] == line[3]
                             or text[i] + ' ' + text[i + 1] == line[3]):
                        print('Составной запрос:', text[i] + ' ' + inf_l[i + 1])
                        if irv:
                            requested_value = line[0] + ' - ' + line[3]
                            print('------------')
                            print(requested_value)
                            print('------------')
                        if line[0] in required_values:
                            required_values[line[0]].append(line[1])
                        else:
                            required_values[line[0]] = [line[1]]

                        res.append(line[0] + ' = ' + line[1])

                    elif inf_l[i] == line[3]:
                        print('Одиночный запрос:', inf_l[i])
                        if irv:
                            requested_value = line[0] + ' - ' + line[3]
                            print('------------')
                            print(requested_value)
                            print('------------')
                        if line[0] in required_values:
                            required_values[line[0]].append(line[1])
                        else:
                            required_values[line[0]] = [line[1]]

                        res.append(line[0] + ' = ' + line[1])
                else:
                    if inf_l[i] == line[3]:
                        print('Одиночный запрос:', inf_l[i])
                        if irv:
                            requested_value = line[0] + ' - ' + line[3]
                            print('------------')
                            print(requested_value)
                            print('------------')
                        if line[0] in required_values:
                            required_values[line[0]].append(line[1])
                        else:
                            required_values[line[0]] = [line[1]]

                        res.append(line[0] + ' = ' + line[1])
            # irv = False

    if requested_value:
        print('Найти:', requested_value)
    else:
        print('Не могу определить вопрос')
    print(required_values)
    for key in required_values:
        required_values[key] = list(dict.fromkeys(required_values[key]))
    print(required_values)
    res = list(dict.fromkeys(res))

    return res
