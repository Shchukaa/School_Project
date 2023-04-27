import re
import sqlite3
import difflib


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

    cursor.execute('''SELECT value, dynamics_formulas.formula, kinematics_formulas.formula, units, name FROM "values"
                    LEFT JOIN dynamics_formulas
                    ON dynamics_formulas.value_id = id
                    LEFT JOIN kinematics_formulas
                    ON kinematics_formulas.value_id = id
                    ORDER BY value
    ''')

    result = tuple(filter(lambda x: not (x[1] is None and x[2] is None), cursor.fetchall()))

    numbers = map(lambda x: x.split()[1], await input_corr(text))

    # Добавление формул по совпадениям единиц измерений
    res = []
    for elem in numbers:
        for unit in result:
            if unit[3] == elem:
                if unit[1] is not None:
                    res.append(unit[0] + ' = ' + unit[1])
                if unit[2] is not None:
                    res.append(unit[0] + ' = ' + unit[2])

    cursor.execute('''SELECT name FROM "values"''')
    names = tuple(map(lambda x: x[0], cursor.fetchall()))

    # Вычисление процента совпадений
    sims = []
    for word in text.split():
        pairs_sim = tuple(filter(lambda x: x[2] >= 0.75, [(name, word, await similarity(name, word)) for name in names]))
        if pairs_sim:
            sims.append(pairs_sim)

    # Добавление формул по совпадениям слов
    for elem in sims:
        elem = elem[0][0]
        for el in result:
            if elem in el:
                if el[1] is not None:
                    res.append(el[0] + ' = ' + el[1])
                if el[2] is not None:
                    res.append(el[0] + ' = ' + el[2])

    return list(dict.fromkeys(sorted(res, key=lambda x: -res.count(x))))