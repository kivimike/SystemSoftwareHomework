import lex
import yacc
import re
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
tokens = ('OR', 'POSCLOS', 'KLEENE', 'OPTIONAL', 'CHAR', 'RPAREN', 'LPAREN', 'NAME', 'SYMB', 'REPEAT', 'EOS')

last_paren_type = ''
ErrorsList = []

t_CHAR = r'\.'
t_OR = r'\|'
t_POSCLOS = r'\+'
t_KLEENE = r'\*'
t_OPTIONAL = r'\?'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EOS    = r'\$'

def t_NAME(t):
    r'<[A-Za-z0-9_]+>'
    t.value = str(t.value)[1:-1]
    return t

def t_SYMB(t):
    r"(&[.?|+&{}$()*<>])|([^<>.?+|&()$*{}])"
    sym = str(t.value)
    if len(sym) > 1:
        sym = sym[1]
    t.value = sym
    return t


'''def t_REPEAT(t):
    r"\{(([0-9]+)?,([0-9]+)?)?\}"
    # print(t.value)
    bounds = re.findall(t.value, r'\d+')
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
        print("ERROR! LOWER BOUND > UPPER BOUND " + str(lower) + '>' + str(upper))'''

def t_REPEAT(t):
    r"\{[0-9]*,[0-9]*\}"
    new_value = re.findall("\d+", t.value)
    for i in new_value:
        i = int(i)
    bounds_bool = []
    buf = re.findall(r"\{,", t.value)
    if len(buf) != 0:
        bounds_bool.append(False)
    else:
        bounds_bool.append(True)
    buf = re.findall(r",\}", t.value)
    if len(buf) != 0:
        bounds_bool.append(False)
    else:
        bounds_bool.append(True)
    if len(new_value) == 2:
        if new_value[0] > new_value[1]:
            raise Exception("Syntax error: invalid bounds specified.")
    t.value = new_value
    t.value += bounds_bool
    return t

# проверить, что нижняя меньше верхнйе

def t_error(t):
    global ErrorsList
    ErrorsList.append("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#data = "sosi*"
lexer = lex.lex()
#lexer.input(data)
#for tok in lexer:
#   print(tok)

print(ErrorsList)


def dfs(nod, iter):
    if nod.children != []:
        print(
            iter * "\t" + "Node " + str(nod.id) + ", type " + str(nod.type) + ', val ' + str(nod.value) + ', F: ' + str(
                nod.F) + ', children: ')
        for child in nod.children:
            dfs(child, iter + 1)
    else:
        print(
            iter * "\t" + "Node " + str(nod.id) + ", type " + str(nod.type) + ', val ' + str(nod.value) + ', F: ' + str(
                nod.F) + ', in N: ' + ", position " + str(nod.position))


def dfs_start(nod):
    dfs(nod, 0)


node_id = 0


class Node:
    def __init__(self):
        global node_id
        self.value = None
        self.type = None
        self.children = []
        # node_id += 1
        self.position = None
        self.F = set()
        # self.L = set()

    def update(self, value, type, children, position):
        self.id = node_id
        self.value = value
        self.type = type
        self.children = children
        self.position = position

    def set_F(self, F):
        if isinstance(F, set):
            self.F = F
        else:
            raise Exception("Passed non-set to Node.set_F(self, set)")

    def __str__(self):
        if self.children == []:
            return "Node " + str(self.id) + ", type " + str(self.type) + ', val ' + str(
                self.value) + ", position " + str(self.position)
        else:
            children = ''
            for node in self.children:
                children += str(node) + '; '
            return "Node " + str(self.id) + ", type " + str(self.type) + ', val ' + str(
                self.value) + ', children: \n [' + children + ']'

def children_to_pair(tok):
    if len(tok.children) == 1:
        tok = tok.children[0]
        return tok
    elif len(tok.children) == 2:
        return tok
    else:
        tok.children[-1] = [tok.children[-2], tok.children[-1]]
        tok.children.pop(-2)
        return children_to_pair(tok)

def make_node_from_range_token(tok, rep_tok):
    global node_id
    return_node = Node()
    if rep_tok.value[-2] == False and rep_tok.value[-1] == False:
        return_node.update(None, "StarNode", [tok], None)
    elif rep_tok.value[-2] == False and rep_tok.value[-1] == True:
        if int(rep_tok.value[0]) == 0:
            raise Exception("Syntax error: zero length specified.")
        elif int(rep_tok.value[0]) == 1:
            return_node.update(None, "OptNode", [tok], None)
        children = []
        for i in range(int(rep_tok.value[0])):
            optnode = Node()
            optnode.update(None, "OptNode", [tok], None)
            node_id += 1
            children.append(optnode)
        return_node.update(None, "ConcatNode", children, None)
        return_node = children_to_pair(return_node)
    elif rep_tok.value[-2] == True and rep_tok.value[-1] == False:
        if int(rep_tok.value[0]) == 0:
            return_node.update(None, "StarNode", [tok], None)
        else:
            children = []
            for i in range(int(rep_tok.value[0])):
                children.append(tok)
            starnode = Node()
            starnode.update(None, "StarNode", [tok], None)
            node_id += 1
            children.append(starnode)
            return_node.update(None, "ConcatNode", children, None)
            return_node = children_to_pair(return_node)
    elif rep_tok.value[-2] == True and rep_tok.value[-1] == True:
        children = []
        for i in range(int(rep_tok.value[0])):
            children.append(tok)
        for i in range(int(rep_tok.value[1]) - int(rep_tok.value[0])):
            optnode = Node()
            optnode.update(None, "OptNode", [tok], None)
            node_id += 1
            children.append(optnode)
        return_node.update(None, "ConcatNode", children, None)
        return_node = children_to_pair(return_node)
    print(return_node)
    return return_node

def process_no_paren(tokens):
    global cap_groups
    global node_id
    # for i in range(len(tokens)):
    #     if not isinstance(tokens[i], Node):
    #         if tokens[i].type == "SYMB":
    #             token_copy = tokens[i]
    #             tokens[i] = Node()
    #             tokens[i].update(token_copy.value, "Symbol", [])

    i = 0
    while i < len(tokens):
        if i - 1 >= 0 and i < len(tokens):
            if not isinstance(tokens[i], Node):
                if tokens[i].type == "POSCLOS" and isinstance(tokens[i - 1], Node):
                    tokens[i] = Node()
                    tokens[i].update(None, "PlusNode", [tokens[i - 1]], None)
                    node_id += 1
                    tokens.pop(i - 1)
                    i -= 1
                elif tokens[i].type == "KLEENE" and isinstance(tokens[i-1], Node):
                    tokens[i] = Node()
                    tokens[i].update(None, "StarNode", [tokens[i-1]], None)
                    node_id += 1
                    tokens.pop(i-1)
                    i -= 1
        i += 1
    i = 0
    while i < len(tokens):
        if i - 1 >= 0 and i < len(tokens):
            if not isinstance(tokens[i], Node):
                if tokens[i].type == "OPTIONAL" and isinstance(tokens[i - 1], Node):
                    tokens[i] = Node()
                    tokens[i].update(None, "OptNode", [tokens[i - 1]], None)
                    node_id += 1
                    tokens.pop(i - 1)
                    i -= 1
        i += 1
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens):
            if isinstance(tokens[i], Node) and isinstance(tokens[i + 1], Node):
                token_copy = tokens[i]
                tokens[i] = Node()
                tokens[i].update(None, "ConcatNode", [token_copy, tokens[i + 1]], None)
                node_id += 1
                tokens.pop(i + 1)
                i -= 1
        i += 1
    i = 0
    while i < len(tokens):
        if i + 2 < len(tokens):
            if isinstance(tokens[i], Node) and tokens[i + 1].type == "OR" and isinstance(tokens[i + 2], Node):
                token_copy = tokens[i]
                tokens[i] = Node()
                tokens[i].update(None, "OrNode", [token_copy, tokens[i + 2]], None)
                node_id += 1
                tokens.pop(i + 1)
                tokens.pop(i + 1)
                i -= 1
        i += 1
    return tokens


def process_in_paren(tokens):
    c_l = 0
    c_r = 0
    l_idx = None
    r_idx = None
    for i in range(len(tokens)):
        if tokens[i].type == "LPAREN":
            l_idx = i
            c_l += 1
        elif tokens[i].type == "RPAREN":
            c_r += 1
    if c_r != c_l:
        raise Exception("NUMBER OF LPAREN AND RPAREN DOESNT MATCH")
    if c_l == 0:
        return process_no_paren(tokens)
    for i in range(l_idx, len(tokens)):
        if tokens[i].type == "RPAREN":
            r_idx = i
            break
    new_tokens = []
    new_tokens += tokens[:l_idx]
    new_tokens += process_no_paren(tokens[l_idx + 1:r_idx])
    new_tokens += tokens[r_idx + 1:]
    return process_in_paren(new_tokens)


def create_nullable_rec(rootnode):
    global N
    if rootnode.type == "OptNode" or rootnode.type == "StarNode":
        create_nullable_rec(rootnode.children[0])
        N.add(rootnode)
        return True
    if rootnode.type == "Epsilon":
        N.add(rootnode)
        return True
    elif rootnode.type == "Symbol":
        return False
    elif rootnode.type == "OrNode":
        flag = False
        for child in rootnode.children:
            belongs = create_nullable_rec(child)
            if belongs:
                flag = True
        if flag:
            N.add(rootnode)
            return True
        else:
            return False
    elif rootnode.type == "ConcatNode":
        flag = True
        for child in rootnode.children:
            belongs = create_nullable_rec(child)
            if not belongs:
                flag = False
        if flag:
            N.add(rootnode)
            return True
        else:
            return False
    elif rootnode.type == "PlusNode":
        belongs = create_nullable_rec(rootnode.children[0])
        if belongs:
            N.add(rootnode)
            return True
        else:
            return False

def create_first_rec(rootnode):
    global N
    global F_for_nodes
    if rootnode.type == "OptNode":
        create_first_rec(rootnode.children[0])
        F_for_nodes.update([(rootnode, F_for_nodes[rootnode.children[0]])])
    elif rootnode.type == "Epsilon":
        F_for_nodes.update([(rootnode, set())])
    elif rootnode.type == "Symbol":
        F_for_nodes.update([(rootnode, set([rootnode.position]))])
    elif rootnode.type == "OrNode":
        buf = set()
        for child in rootnode.children:
            create_first_rec(child)
            buf = buf.union(F_for_nodes[child])
        F_for_nodes.update([(rootnode, buf)])
    elif rootnode.type == "ConcatNode":
        create_first_rec(rootnode.children[0])
        create_first_rec(rootnode.children[1])
        buf = F_for_nodes[rootnode.children[0]]
        if rootnode.children[0] in N:
            buf = buf.union(F_for_nodes[rootnode.children[1]])
        F_for_nodes.update([(rootnode, buf)])
    elif rootnode.type == "PlusNode" or rootnode.type == "StarNode":
        create_first_rec(rootnode.children[0])
        F_for_nodes.update([(rootnode, F_for_nodes[rootnode.children[0]])])

def create_last_rec(rootnode):
    global N
    global L_for_nodes
    if rootnode.type == "OptNode":
        create_last_rec(rootnode.children[0])
        L_for_nodes.update([(rootnode, L_for_nodes[rootnode.children[0]])])
    elif rootnode.type == "Epsilon":
        L_for_nodes.update([(rootnode, set())])
    elif rootnode.type == "Symbol":
        L_for_nodes.update([(rootnode, set([rootnode.position]))])
    elif rootnode.type == "OrNode":
        buf = set()
        for child in rootnode.children:
            create_last_rec(child)
            buf = buf.union(L_for_nodes[child])
        L_for_nodes.update([(rootnode, buf)])
    elif rootnode.type == "ConcatNode":
        create_last_rec(rootnode.children[0])
        create_last_rec(rootnode.children[1])
        buf = L_for_nodes[rootnode.children[1]]
        if rootnode.children[1] in N:
            buf = buf.union(L_for_nodes[rootnode.children[0]])
        L_for_nodes.update([(rootnode, buf)])
    elif rootnode.type == "PlusNode" or rootnode.type == "StarNode":
        create_last_rec(rootnode.children[0])
        L_for_nodes.update([(rootnode, L_for_nodes[rootnode.children[0]])])

def create_FP(rootnode):
    global pos_set
    global F_for_nodes
    global L_for_nodes
    for child in rootnode.children:
        create_FP(child)
    if rootnode.type == "ConcatNode":
        for p in L_for_nodes[rootnode.children[0]]:
            for q in F_for_nodes[rootnode.children[1]]:
                pos_set[p].add(q)
    elif rootnode.type == "PlusNode" or rootnode.type == "StarNode":
        for p in L_for_nodes[rootnode.children[0]]:
            for q in F_for_nodes[rootnode.children[0]]:
                pos_set[p].add(q)


def get_symbol_pos(data):
    ls = []
    symbol_pos = {}
    lexer.input(data)
    for token in lexer:
        ls.append(token)
    c = 0
    for i in range(len(ls)):
        if ls[i].type == "SYMB":
            symbol_pos.update([(c, ls[i].value)])
            c += 1
    return symbol_pos

#pos_set = dict()
'''____'''
#data = 'me*|p(hi)*'
ls = []
#symbol_pos = {}
#lexer.input(data)
pos_set = dict()
#for token in lexer:
#    ls.append(token)
c = 0
for i in range(len(ls)):
    if not isinstance(ls[i], Node):
        if ls[i].type == "SYMB":
            token_copy = ls[i]
            ls[i] = Node()
            ls[i].update(token_copy.value, "Symbol", [], c)
            node_id += 1
            pos_set.update([(c, set())])
            c += 1
'''----'''

N = set()
F_for_nodes = dict()
L_for_nodes = dict()
#print(data, len(data))
#rt_node = process_in_paren(ls)[0]
#dfs_start(rt_node)
#print(rt_node)
#create_nullable_rec(rt_node)
#for n in N:
#    print(n)
#create_first_rec(rt_node)
#create_last_rec(rt_node)
#create_FP(rt_node)
#for item in pos_set:
#    print(item)
#    print(pos_set[item])
'''------'''
#print(N)
#for i in list(N):
#    print(i)
#process_no_paren(ls)
