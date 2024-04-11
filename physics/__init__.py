import re
import difflib
from language import infinitive, inflecting
from config import question_words, synonym_words
import sqlite3
from typing import List, Tuple, NewType
import asyncio
import sympy
from copy import deepcopy


Value = NewType('Value', str)
Formula = NewType('Formula', str)
Units = NewType('Units', str)
Name = NewType('Name', str)


def collect_info() -> List[Tuple[Value, Formula, Units, Name]]:
    conn = sqlite3.connect('C:/Users/t106o/PycharmProjects/Shcool Project/Physical_formulas_test.db')
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
async def physics_calc(text=None, requested_values=None, provided_values=None, ignore_values=None,
                       ignore_formulas=None, db_info=None):
    if not db_info:
        db_info = collect_info()
    if text:
        required_values, requested_values, provided_values = await text_to_machine_condition_forming(text,
                                                                                                     db_info=db_info)
    print('-', requested_values)
    for i in range(len(requested_values)):
        if ignore_formulas and requested_values[i][1] in ignore_formulas:
            continue
        for elem in requested_values:
            if 'x(t)' in elem:
                return await machine_to_chat_condition_forming(provided_values, requested_values, i,
                                                               ignore_values=['t'], db_info=db_info)
        else:
            print('physics_calc', 'ignore_values:', ignore_values, 'ignore_formulas:', ignore_formulas)
            print('provided_values:', provided_values, 'requested_values:', requested_values)
            print('db_info', db_info)
            result = await machine_to_chat_condition_forming(provided_values, requested_values, i,
                                                             ignore_values=ignore_values,
                                                             ignore_formulas=ignore_formulas, db_info=db_info)
            if result:
                return result
    return None


async def text_to_machine_condition_forming(text, db_info=None):
    """:return required, requested and provided values"""
    """
        units = map(lambda x: x.split()[1], await input_corr(text))
        print(*units)


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

    # Для начала создаем список из инфинитивов слов запроса и их склонений
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
    print('inf_l:', inf_l)
    print('infl_l', infl_l)
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
    # Текущее слово "средняя", следующее слово "скорость"
    # Найдено: средняя скорость -> пропуск следующего цикла со словом "скорость"
    double_value = False

    print(*db_info, sep='\n')

    value_names = set([value[3] for value in db_info])
    # Данные величины
    provided_values = {}
    # Спрашиваемые величины
    requested_values = []
    # Возможные формулы
    required_values = {}
    test_requir, test_request = {}, []

    for i in range(len(inf_l)):
        if not double_value and (test_requir or test_request):
            for elem in test_requir:
                required_values[elem] = test_requir[elem]
            requested_values += test_request
        test_requir, test_request = {}, []
        print(required_values, requested_values)
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
                    print((text[i], text[i + 1]))
                    # Проверка на составной запрос (текущее слово + следующее слово)
                    if infl_l[i] and (infl_l[i] + ' ' + inf_l[i + 1] == value[3]
                                      or inf_l[i] + ' ' + text[i + 1] == value[3]
                                      or text[i] + ' ' + text[i + 1] == value[3]):
                        print('Составной запрос:', text[i] + ' ' + inf_l[i + 1])

                        double_value = True

                        # Можно просто попробовать написать await request_check(irv, value, requested_values,
                        #                                                                                 required_values)
                        # Должно сработать, т.к. в аргументы передаем ссылки на объекты вне функции, а не создаем новые
                        required_values, requested_values = await request_check(irv, value, requested_values,
                                                                                required_values)
                        print(required_values, requested_values, 'После составного запроса')
                        # res.append(value[0] + ' = ' + value[1])

                    # Проверка на одиночный запрос (текущее слово)
                    elif inf_l[i] == value[3]:
                        print('Одиночный запрос:', inf_l[i])
                        # Записываем результат в отдельную переменную для того, чтобы избежать проблемы нахождения
                        # двух величин в составном запросе ("Сила" и "Сила упругости" в "Силе упругости")
                        print(required_values, requested_values, 'Перед одиночным запросом')
                        test_requir, test_request = await request_check(irv, value, test_request,
                                                                        test_requir)

                        print(required_values, requested_values, test_requir, test_request, 'После одиночного запроса')
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
            if i < len(inf_l) - 3:
                if double_value:
                    if infl_l[i] + ' ' + inf_l[i + 1] in value_names:
                        data = provided_values, infl_l[i] + ' ' + inf_l[i + 1], inf_l, i
                        provided_values = await value_from_text_collecting(*data, db_info=db_info)
                    elif inf_l[i] + ' ' + text[i + 1] in value_names:
                        data = provided_values, inf_l[i] + ' ' + text[i + 1], inf_l, i
                        provided_values = await value_from_text_collecting(*data, db_info=db_info)
                    elif text[i] + ' ' + text[i + 1] in value_names:
                        data = provided_values, text[i] + ' ' + text[i + 1], inf_l, i
                        provided_values = await value_from_text_collecting(*data, db_info=db_info)
                else:
                    if inf_l[i] in value_names:
                        data = provided_values, inf_l[i], inf_l, i
                        provided_values = await value_from_text_collecting(*data, db_info=db_info)
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
    """
    for value in required_values:
        for formula in required_values[value]:
            res.append(value + ' = ' + formula)
    """
    print(f'requested_values: {requested_values}')
    print(f'provided_values: {provided_values}')
    return required_values, requested_values, provided_values


async def machine_to_chat_condition_forming(provided_values, requested_values, i, ignore_values=None,
                                            ignore_formulas=None, provided_formulas=None, provided_result_formula=None,
                                            provided_expr=None, db_info=None):
    if not provided_expr and not provided_formulas:
        expr, formulas = await finding_formulas(requested_values[i][0], requested_values[i][1], provided_values,
                                                ignore_formulas=ignore_formulas, ignore_values=ignore_values,
                                                db_info=db_info)
    else:
        expr, formulas = provided_expr, provided_formulas
    print('expr:', expr, 'formulas:', formulas)
    if expr:
        try:
            print('Формулы:')
            if not provided_formulas:
                for i in range(len(formulas)):
                    formulas[i] = str(i + 1) + ') ' + formulas[i]
            if not provided_result_formula:
                result_formula = formulas[0]
                for i in range(1, len(formulas)):
                    vl, frml = formulas[i].split(' = ')
                    print('replace', vl, frml)
                    result_formula = result_formula.replace(vl[3:], '(' + frml + ')')
            else:
                result_formula = provided_result_formula
            print('Итоговая формула:', result_formula)
            to_find = requested_values[0][0] + ' - ?'
            if not ignore_values:
                if not provided_expr:
                    result = eval(expr)
                    print('Ответ на твою задачу равен:', expr, '=', result)
                    expr = result_formula.split()[1] + ' = ' + ' '.join([expr, '=', str(result)]) + ' ' + \
                           requested_values[0][2]
                else:
                    expr = provided_expr
            else:
                print('ignore_values', ignore_values)
                if 't' in ignore_values:
                    print('not', expr)
                    expr = expr.split('+')
                    expr[2] = expr[2].split('*')
                    expr[2][0] = str(round(eval(expr[2][0])))
                    if expr[2][0] == '1':
                        expr[2] = expr[2][1]
                    else:
                        expr[2] = '*'.join([expr[2][0], expr[2][1]])
                    expr = '+'.join(expr)
                    expr = result_formula.split()[1] + ' = ' + expr
            # Очищаем данные величины от технической составляющей
            given = {}
            k = 0
            for key in provided_values:
                if '_count' not in key:
                    k += 1
                    given[key] = str(k) + ') ' + key + " = " + ''.join(provided_values[key])

            given = "\n".join([given[key] for key in given])
            if not provided_formulas:
                formulas = '\n'.join(formulas)
            else:
                formulas = provided_formulas

            print('✅Решение твоей задачи👇💯: \n'
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
            return given, to_find, formulas, result_formula, expr, provided_values, requested_values, db_info
        except NameError as error:
            print('Не найдена формула для одной из величин формулы:', error)
            return None
        except IndexError as error:
            print('Не найдено ни одной формулы', error)
            return None


async def chat_to_machine_condition_forming(condition):
    """:returns provided_values, requested_values, formulas, result_formula, expr, db_info"""
    print(condition)
    given, to_find, formulas, result_formula, expr, provided_values, requested_values, db_info = condition
    print('not error')
    # При составлении provided_values из условия в чате в provided_values попадает только одна формула неизвестной
    # физической величины - используемая решении
    # provided_values = await provided_values_forming(given)
    # requested_values = await requested_values_forming(formulas, expr)
    return provided_values, requested_values, formulas, result_formula, expr, db_info


async def requested_values_forming(formulas, expr):
    formulas = formulas.split('\n')
    requested_values = []
    formula = formulas[0].split()
    requested_values.append((formula[1], formula[3], expr.split()[-1], None))
    return requested_values


async def provided_values_forming(given):
    given = given.split('\n')
    provided_values = {}
    print('given:', given)
    for elem in given:
        print('elem:', elem)
        if elem[0].isdigit():
            elem = elem[3:]
        phys_value, value = elem.split(' = ')
        digit = ''
        for i in range(len(value)):
            if value[i].isdigit() or value[i] == '.':
                digit += value[i]
            else:
                break
        units = value.replace(digit, '')
        provided_values[phys_value] = [digit, units]
    print(provided_values)
    return provided_values


async def value_from_text_collecting(provided_values, word, inf_l, i, value=None, unit=None, db_info=None):
    # Находим обозначение данной физической величины
    for elem in db_info:
        if word == elem[3]:
            print('value_collecting:', word, elem)
            value = elem[0]
            unit = elem[2]
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
                #   С прочтением второй будет перезаписана запись 'v': '10' на 'v': 2, и будут созданы записи:
                # 'v0': '10' и 'v1': '20'; Запись 'v': 2 будет означать, что есть уже 2 физические величины 'v'
                #   При прочтении третьей скорости будет изменена запись с количеством скоростей на: 'v': 3,
                # и создана еще одна запись 'v3': '30'
                # Также стоит учесть ситуацию, при которой в provided_values уже находится начальная скорость с
                # обозначением v0. Этот случай надо рассматривать отдельно и присваивать последующим скоростям номера
                if value in provided_values or value + '_count' in provided_values or value + '0' in provided_values:
                    print('prvd_vls')
                    # Первое добавление повторной величины
                    if value + '0' in provided_values and type(provided_values[value + '0']) == list:
                        print(1)
                        provided_values[value + '1'] = [inf_l[i + k], unit]
                        provided_values[value + '_count'] = 2
                    elif type(provided_values[value]) == list:
                        print(1)
                        provided_values[value + '0'] = provided_values[value]
                        provided_values[value + '1'] = [inf_l[i + k], unit]
                        del provided_values[value]
                        provided_values[value + '_count'] = 2
                    # Повторное добавление физической величины
                    else:
                        print(2)
                        print(provided_values)
                        provided_values[value + '_count'] += 1
                        provided_values[value + str(provided_values[value] - 1)] = inf_l[i + k]
                else:
                    provided_values[value] = [inf_l[i + k], unit]
                break
    else:
        raise ValueError(f'Такой физической величины не существует: {word}')

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


async def finding_formulas(value_name: str, formula: str, provided_values, result_formulas=None, k=0, digit='',
                           ignore_values=None, ignore_formulas=None, db_info=None):
    # ---Python one love---
    # Сразу указать дефолтное значение для result_formulas нельзя (result_formulas=[] неочевидно работает)
    if not result_formulas:
        result_formulas = []
    if not ignore_values:
        ignore_values = []
    if not ignore_formulas:
        ignore_formulas = []

    # ---------------------
    k += 1
    print('recursion', k)
    print('Начало функции по формуле:', formula, 'result_formulas:', result_formulas, 'k=' + str(k))
    if k == 1:
        result_formulas.append(value_name + ' = ' + formula)
    # Условие выхода из цикла - достижение двойной вложенности k
    # или полное составление итогового алгебраического выражения
    if k > 5:
        print('Неудачный конец рекурсии', formula)
        result_formulas.pop()
        print('result_formulas.pop:', result_formulas)
        return False, result_formulas
    else:
        # Получаем физические величины из формулы
        values = list(dict.fromkeys(await value_selecting(formula, '')))

        # Рекурсивно находим формулы для каждой из полученных физических величин
        for value in values:
            if value in ignore_values:
                continue
            if not value[-1].isdigit():
                value += digit
            print('input value:', value)
            print(provided_values)
            if value in provided_values:
                print('find_value:', value)
                formula = formula.replace(value, provided_values[value][0])

            else:
                if value[-1].isdigit():
                    print('digit')
                    value, digit = value[:-1], value[-1]

                formulas = []
                for elem in db_info:
                    if value == elem[0] and elem[1] and elem[1] not in ignore_formulas \
                            and result_formulas[0].split('=')[0] not in elem[1]:
                        print(elem)
                        if digit and value + digit not in elem[1]:
                            vls = await value_selecting(elem[1], digit)
                            e = deepcopy(elem[1])
                            # Для того чтобы избежать повторных ложных замен переменных в ситуации, когда обозначение
                            # одной переменной может состоять в обозначении другой, сначала заменим переменные на
                            # условное обозначение: [номер переменной в списке vls], а потом уже в отдельном цикле
                            # установим реальные названия
                            for i in range(len(vls)):
                                if vls[i][-1].isdigit() and vls[i][-2].isdigit():
                                    e = e.replace(vls[i][:1] + vls[i][2:], '[' + str(i) + ']')
                                else:
                                    e = e.replace(vls[i][:-1], '[' + str(i) + ']')

                            for i in range(len(vls)):
                                e = e.replace('[' + str(i) + ']', vls[i])

                            formulas.append(e)

                        elif not digit and result_formulas[0].split(' = ')[0] not in elem[1]:
                            print('lol' + '|' + result_formulas[0].split(' = ')[0] + '|' + elem[1])
                            print(result_formulas)
                            print(value, elem[1])
                            formulas.append(elem[1])

                print('formulas', formulas)

                if any(formulas):
                    for f in formulas:
                        result_formulas.append(value + digit + ' = ' + f)
                        print('Рекурсия, value:', value + digit, ', formulas:', formulas)
                        # Костыль с __count=1 в formula.replace. Продумать сложную реализацию проверки составной
                        # физической величины, например: в формуле x-x0 программа подбирает формулу для x и подставляет
                        # ее не только в x, но и в x0, и вместо (x0+v0*t+(a*t**2)/2)-x0
                        # получается (x0+v0*t+(a*t**2)/2)-(x0+v0*t+(a*t**2)/2)0
                        result, test_formulas = await finding_formulas(value, formula.replace(value + digit,
                                                                                              '(' + f + ')', 1),
                                                                       provided_values,
                                                                       result_formulas=deepcopy(result_formulas), k=k,
                                                                       digit=digit, ignore_formulas=ignore_formulas,
                                                                       db_info=db_info)
                        print('test_formulas:', test_formulas)
                        if test_formulas:
                            result_formulas = test_formulas
                        print('result_formulas:', result_formulas)
                        if result:
                            print('result: ', result)
                            try:
                                eval(result)
                                return result, result_formulas
                            except BaseException:
                                pass
                else:
                    print('Нет ни одной подходящей формулы')
                    result_formulas.pop()
                    return False, result_formulas

        print('Last return:', formula)
        if value_name != 'x(t)':
            try:
                eval(formula)
            except:
                result_formulas.pop()

        return formula, result_formulas


async def value_selecting(formula, digit):
    print(formula)
    values = []
    for i in range(len(formula)):
        symb = formula[i]
        if symb.isalpha():
            value = symb
            value += digit
            if i != len(formula) - 1:
                next_symb = formula[i + 1]
                if next_symb.isdigit():
                    value += next_symb
            if i != len(formula) - 1:
                print('value', value, 'next_symb', next_symb, 'digit', digit)
            values.append(value)

    values = list(dict.fromkeys(values))
    print(values)
    return values


'''
asyncio.run(physics_calc('Машина ехала со скоростью 20 м/c в течении времени, равному 5 секундам.'
                         ' Какое расстояние пройдет это тело?'))
# 100
asyncio.run(physics_calc('Тело движется из начального положения 3 м с начальной скоростью 3 м/с в течение времени '
                         'равном 5 секундам. Известно, что конечная скорость тела равна 6 м/с. В какой координате '
                         'окажется это тело?'))
# 25.5
asyncio.run(physics_calc('Тело двигалось по прямой из точки с начальной координатой 3 м с начальной скоростью 5 м/с.'
                         ' Ускорение равно 2 м/с. Записать уравнение движения тела.'))
# x(t) = 3+5*t+t^2
asyncio.run(physics_calc('Тело движется по дороге длиной 100 м с начальной скоростью 10 м/c. Известно, что конечная '
                         'скорость тела равна 6 м/c. За какое время тело завершит свое движение по дороге?'))
# 12.5
asyncio.run(physics_calc('Расстояние 100 м автомобиль двигается со скоростью 69 м/с, расстояние еще в 100 м  - со '
                         'скоростью 111 м/с. Найдите среднюю скорость движения автомобиля.'))
# 85.1
asyncio.run(physics_calc('Тело движется со ускорением 2 м/c^2 в течении времени, равному 5 секундам, сила упругости '
                         'равна 10 дж. Начальная скорость равна 0. Какое расстояние пройдет это тело?'))
# 25.0 -> без ignore_formulas 50.0
asyncio.run(physics_calc('Тело движется по дороге длиной 100 м с начальной скоростью 10 м/c. Известно, что конечная '
                         'скорость тела равна 6 м/c. За какое время тело завершит свое движение по дороге?'))
# 12.5
'''

# При определении расстояния, пройденного телом нужно учесть характер движения(равномерное или равноускоренное).
# Для этого можно проверить наличие ускорения или начальной и конечной скорости в условии.


# Ускорить программу
# Добавить возможность запрета сразу нескольких формул
# Выделить жирным шрифтом маску ввода пользователя + добавить пример добавления физической величины/формулы
# Добавить отмену действия до его совершения при изменении задачи(при миссклике)
# При более, чем 10 шагов в задаче будет возникать ошибка, т.к. программа во многих функциях отбрасывает номер формулы
# напрямую через обрезание строки на 3 пункта: [3:]
