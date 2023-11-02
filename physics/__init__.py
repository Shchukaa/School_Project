import re
import sqlite3
import difflib
from language import infinitive


ci_units = {
    'К': 10**3,
    'к': 10**3,
    'М': 10*6,
    'д': 10**-1,
    'с': 10**-2,
    'м': 10**-3,
    'н': 10**-9
}


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
    conn = sqlite3.connect('C:/Users/t106o/PycharmProjects/UchiDoma-NewProject/Physical_formulas.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT value, kinematics_formulas.formula, units, name FROM "values", "kinematics_formulas"
                        WHERE id = kinematics_formulas.value_id
                 ''')
    bd_info = cursor.fetchall()

    cursor.execute('''SELECT value, dynamics_formulas.formula, units, name FROM "values", "dynamics_formulas"
                        WHERE id = dynamics_formulas.value_id
                 ''')
    bd_info += cursor.fetchall()

    cursor.execute('''SELECT value, hydrostatics_formulas.formula, units, name FROM "values", "hydrostatics_formulas"
                        WHERE id = hydrostatics_formulas.value_id
                 ''')

    bd_info += cursor.fetchall()
    print(*bd_info, sep='\n')

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

    cursor.execute('''SELECT name FROM "values"''')
    names = tuple(map(lambda x: x[0], cursor.fetchall()))

    # Вычисление процента совпадений

    # Для начала создаем список из инфинитивов слов запроса
    inf_l = []
    for word in text.split():
        inf_l.append(infinitive(word))

    sims = []
    for word in inf_l:
        pairs_sim = tuple(filter(lambda x: x[2] >= 0.95,
                                 [(name, word, await similarity(name, word)) for name in names]))
        if pairs_sim:
            print(pairs_sim)
            sims.append(pairs_sim[0][0])

    # Добавление формул по совпадениям слов
    exception_words = ['сила', 'энергия']
    res = []
    for elem in sims:
        for line in bd_info:
            if elem in line[3] and elem not in exception_words:
                res.append(line[0] + ' = ' + line[1])

    return list(dict.fromkeys(sorted(res, key=lambda x: -res.count(x))))