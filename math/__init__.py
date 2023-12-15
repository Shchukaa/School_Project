import re
import sympy
from config import db_info


def splitting(formula):
    required_values = {}
    variables = re.findall(r"[^ =/*+%-]", formula)[1:]
    # variables = sympy.symbols()
    print(formula)
    return variables


def finding_formulas(var):
    res = []
    for elem in db_info:
        if elem[0] == var:
            res.append(elem[1])
    return res


print(splitting("v = S/t*y**t-5"))
print('-----')
print(finding_formulas('S'))