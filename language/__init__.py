from pymorphy2 import MorphAnalyzer
import functools


@functools.lru_cache(maxsize=None)
def infinitive(word: str) -> str:
    morph = MorphAnalyzer()
    inf = morph.parse(word)[0].normal_form
    return inf


def inflecting(word1: str, word2: str):
    """
    Случай 1: \n
    word1 прилагательное\n
    return: word1 в начальной форме, склоненное под род слова word2\n
    Случай 2:\n
    word1: все, кроме прилагательного\n
    return: word1\n
    Случай 3:\n
    word1 и/или word2 не может быть использовано\n
    return None
    """
    morph = MorphAnalyzer()
    w1_tags = morph.parse(infinitive(word1))[0]
    if 'ПРИЛ' in w1_tags.tag.cyr_repr:
        w2_tags = morph.parse(word2)[0]
        w2_gender = w2_tags.tag.gender
        if not w2_gender:
            return
        word1 = w1_tags.inflect({w2_gender}).word
    return word1


print(inflecting('сила', 'упругость'))