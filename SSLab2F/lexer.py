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
{3,}{,3}{,}
Операция ‘именованная группа захвата’: (<name>r) (метасимвол ‘(<name>)’, name – имя группы захвата)
Операция ‘выражение из именованной группы захвата’: <name> (метасимвол ‘<name>’, name – имя группы захвата)

Библиотека должна поддерживать следующие операции:

findall – поиск всех непересекающихся вхождений подстрок в строку соответствующих регулярному выражению

 

Регулярные выражения могут быть заранее скомпилированы в ДКА непосредственно, без построения НКА (РВ->ДКА->минимальный ДКА).'''
tokens = ('OR', 'POSCLOS', 'OPTIONAL', 'CHAR', 'RPAREN', 'LPAREN', 'NAME', 'SYMB', 'REPEAT')


last_paren_type = ''
ErrorsList = []

t_CHAR = r'\.'
t_OR = r'\|'
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
    #print(t.value)
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

    if lower <= upper or (lower == 0 and upper == -1):
        t.value = (lower, upper)
        return t
    else:
        ErrorsList.append(t.value)
        print("ERROR! LOWER BOUND > UPPER BOUND "+ str(lower)+'>'+ str(upper))
#проверить, что нижняя меньше верхнйе

def t_error(t):
    global ErrorsList
    ErrorsList.append("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()


if __name__ == "__main__":
    data = 'me+|p(hi)+'
    #data = '(())'
    ls = []
    lexer.input(data)

    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break
    #     print(tok)
    for token in lexer:
        ls.append(token)

print(ErrorsList)

def dfs(nod, iter):
    if nod.children != []:
        print(iter * "\t" + "Node " + str(nod.value) + ", type: " + str(nod.type) + ", children: ")
        for child in nod.children:
            dfs(child, iter+1)
    else:
        print(iter * "\t" + "Node " + str(nod.value) + ", type: " + str(nod.type))


def dfs_start(nod):
    dfs(nod, 0)

class Node:
    def __init__(self):
        self.value = None
        self.type = None
        self.children = []


    def update(self, value, type, children):
        self.value = value
        self.type = type
        self.children = children


    def __str__(self):
        if self.children == []:
            return str(self.type) + ', val ' + str(self.value)
        else:
            children = ''
            for node in self.children:
                children += str(node) + '; '
            return str(self.type) + ', val ' + str(self.value) + ', children: \n [' + children + ']'

def process_no_paren(tokens):
    for i in range(len(tokens)):
        if not isinstance(tokens[i], Node):
            if tokens[i].type == "SYMB":
                token_copy = tokens[i]
                tokens[i] = Node()
                tokens[i].update(token_copy.value, "Symbol", [])
    i = 0
    while i < len(tokens):
        if i-1 >= 0 and i < len(tokens):
            if not isinstance(tokens[i], Node):
                if tokens[i].type == "POSCLOS" and isinstance(tokens[i-1], Node):
                    tokens[i] = Node()
                    tokens[i].update(None, "PlusNode", [tokens[i-1]])
                    tokens.pop(i-1)
                    i-=1
        i+=1
    i = 0
    while i < len(tokens):
        if i+1 < len(tokens):
            if isinstance(tokens[i], Node) and isinstance(tokens[i+1], Node):
                token_copy = tokens[i]
                tokens[i] = Node()
                tokens[i].update(None, "Concat", [token_copy, tokens[i+1]])
                tokens.pop(i+1)
                i-=1
        i+=1
    i = 0
    while i < len(tokens):
        if i+2 < len(tokens):
            if isinstance(tokens[i], Node) and tokens[i+1].type == "OR" and isinstance(tokens[i+2], Node):
                token_copy = tokens[i]
                tokens[i] = Node()
                tokens[i].update(None, "Or", [token_copy, tokens[i+2]])
                tokens.pop(i+1)
                tokens.pop(i+1)
                i-=1
        i+=1

    return tokens


def process_in_paren(tokens):
    c_l = 0
    c_r = 0
    l_idx = None
    r_idx = None
    for i in range(len(tokens)):
        if tokens[i].type == "LPAREN":
            l_idx = i
            c_l+=1
        elif tokens[i].type == "RPAREN":
            c_r+=1
    if c_r !=  c_l:
        raise Exception("NUMBER OF LPAREN AND RPAREN DOESNT MATCH")
    if c_l == 0:
        return process_no_paren(tokens)
    for i in range(l_idx, len(tokens)):
        if tokens[i].type == "RPAREN":
            r_idx = i
            break
    new_tokens = []
    new_tokens += tokens[:l_idx]
    new_tokens+=process_no_paren(tokens[l_idx+1:r_idx])
    new_tokens += tokens[r_idx+1:]
    return process_in_paren(new_tokens)

print(data)
dfs_start(process_in_paren(ls)[0])



#process_no_paren(ls)
