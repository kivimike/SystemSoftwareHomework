import lex
import yacc
'''Разработать библиотеку для работы с регулярными выражениями. В качестве алфавита могут использовать любые печатные символы, метасимволы экранируются символом ‘&’.

Регулярный выражения должны поддерживать следующие операции:
Операция ‘или’: r1|r2 (метасимвол ‘|’)
Операция ‘конкатенация’: r1r2
Операция ‘позитивное замыкание’: r+ (метасимвол ‘+’)
Операция ‘опциональная часть’: r? (метасимвол ‘?’)
Операция ‘любой символ’: . (метасимвол ‘.’)
Операция ‘повтор выражения в диапазоне’: r{x,y} (метасимвол ‘{х, y}’, где x – нижняя граница, y – верхняя граница), границы могут отсутствовать.
Операция ‘именованная группа захвата’: (<name>r) (метасимвол ‘(<name>)’, name – имя группы захвата)
Операция ‘выражение из именованной группы захвата’: <name> (метасимвол ‘<name>’, name – имя группы захвата)

Библиотека должна поддерживать следующие операции:

findall – поиск всех непересекающихся вхождений подстрок в строку соответствующих регулярному выражению

 

Регулярные выражения могут быть заранее скомпилированы в ДКА непосредственно, без построения НКА (РВ->ДКА->минимальный ДКА).'''
tokens = ('OR', 'POSCLOS', 'OPTIONAL', 'CHAR', 'RPAREN', 'LPAREN', 'NAME', 'SYMB', 'REPEAT')


last_paren_type = ''
ErrorsList = []

# t_CHAR = r'\.'
# t_OR = r'\|'
t_POSCLOS = r'\+'
t_OPTIONAL = r'\?'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_NAME(t):
    r'<[A-Za-z0-9_]+>'
    t.value = str(t.value)[1:-1]
    return t


def t_SYMB(t):
    r"(&[.?|+&{}()<>])|([^<>.?+|&(){}])"
    sym = str(t.value)
    if len(sym) > 1:
        sym = sym[1]
    t.value = sym
    return t


def t_REPEAT(t):
    r"\{(([0-9]+)?,([0-9]+)?)?\}"
    print(t.value)
    bounds = str(t.value)[1:-1]
    if bounds:
        lower, upper = bounds.split(",")
        if not lower:
            lower = 0
        else:
            lower = int(lower)
        if not upper:
            upper = -1
        else:
            upper = int(upper)
    else:
        lower, upper = 0, -1


    t.value = (lower, upper)
    return t


def t_error(t):
    global ErrorsList
    ErrorsList.append("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()


if __name__ == "__main__":
    data = '(a.bc&.)<hello>a|b{}{1,5}{,6}{4,}(<hello>).()'
    #data = '(())'
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)