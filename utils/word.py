def get_translit(string):
    if not string:
        return ''
    result = ''
    to_eng = dict(
        а='a',
        б='b',
        в='v',
        г='g',
        д='d',
        е='e',
        ё='yo',
        ж='zh',
        з='z',
        и='i',
        й='y',
        к='k',
        л='l',
        м='m',
        н='n',
        о='o',
        п='p',
        р='r',
        с='s',
        т='t',
        у='u',
        ф='f',
        х='kh',
        ц='ts',
        ч='ch',
        ш='sh',
        щ='sch',
        я='ya'
    )
    for i in string:
        try:
            result += to_eng.get(i.lower())
        except TypeError:
            pass

    return result
