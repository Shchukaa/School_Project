from pymorphy2 import MorphAnalyzer
import functools


@functools.lru_cache(maxsize=None)
def infinitive(word):
    morph = MorphAnalyzer()
    inf = morph.parse(word)[0].normal_form
    return inf


def inflecting(word1, word2):
    morph = MorphAnalyzer()
    w1_tags = morph.parse(infinitive(word1))[0]
    if 'ПРИЛ' in w1_tags.tag.cyr_repr:
        w2_tags = morph.parse(word2)[0]
        w2_gender = w2_tags.tag.gender
        word1 = w1_tags.inflect({w2_gender}).word
    return word1


print(inflecting('среднюю', 'скорость'))