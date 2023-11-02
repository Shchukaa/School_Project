from pymorphy2 import MorphAnalyzer
import functools


@functools.lru_cache(maxsize=None)
def infinitive(word):
    morph = MorphAnalyzer()
    inf = morph.parse(word)[0].normal_form
    return inf
