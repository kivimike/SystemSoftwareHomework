import lexer
import test_range
import re
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&|+?.{}()<>$"
state_id = 0

class FSM:
    states = []
    state_1 = None
    transitions = []
    receiver_states = []
    FP = {}
    F = {}
    symbol_pos = {}
    rt_node = None

    def add_state(self, state):
        self.states.append(state)

    def add_receiver_state(self, state):
        self.receiver_states.append(state)

    def add_transition(self, state1, symb, state2):
        self.transitions.append([state1, symb, state2])

    def specify_state_1(self, state):
        self.state_1 = state

    def process_round(self, symb):
        for tr in self.transitions:
            if tr[0] == self.state_1 and tr[1] == symb:
                self.state_1 = tr[2]
                return
        raise Exception("Couldn't make transition in FSM")

    def string_input(self, string):
        for symb in string:
            self.process_round(symb)

    def in_receiver_state(self):
        if self.state_1 in self.receiver_states:
            return True
        return False

    def __str__(self):
        s = "FSM\nStates:\n"
        for st in self.states:
            s += str(st) + "\n"
        s += "Receiver states:\n"
        for st in self.receiver_states:
            s += str(st) + "\n"
        s += "Transitions:\n"
        for tr in self.transitions:
            s += str(tr) + "\n"
        return s

    def wrap(self, regex):
        regex = test_range.preprocess(regex)
        ls = []
        lexer.lexer.input(regex)
        for token in lexer.lexer:
            ls.append(token)
        c = 0
        for i in range(len(ls)):
            if not isinstance(ls[i], lexer.Node):
                if ls[i].type == "SYMB" or ls[i].type == 'EOS':
                    token_copy = ls[i]
                    ls[i] = lexer.Node()
                    ls[i].update(token_copy.value, "Symbol", [], c)
                    lexer.node_id += 1
                    lexer.pos_set.update([(c, set())])
                    self.symbol_pos.update([(c, token_copy.value)])
                    c += 1

        self.rt_node = lexer.process_in_paren(ls)[0]
        #lexer.dfs_start(self.rt_node)
        lexer.create_nullable_rec(self.rt_node)
        lexer.create_first_rec(self.rt_node)
        lexer.create_last_rec(self.rt_node)
        lexer.create_FP(self.rt_node)
        self.F = lexer.F_for_nodes
        self.FP = lexer.pos_set

    def create_fsm_from_F_FP(self):
        #global state_id
        global alphabet
        unhandled_states = []
        self.add_state(self.F[self.rt_node])
        self.specify_state_1(self.F[self.rt_node])
        #cayley_table.update([(state_id, self.F[self.rt_node])])
        unhandled_states.append(self.F[self.rt_node])
        #state_id += 1
        while len(unhandled_states) != 0:
            for st in unhandled_states:
                break
            for symb in alphabet:
                u = set()
                for pos in st:
                    if self.symbol_pos[pos] == symb:
                        u = u.union(self.FP[pos])
                if u not in self.states:
                    self.add_state(u)
                    unhandled_states.append(u)
                self.add_transition(st, symb, u)
            unhandled_states.remove(st)
        EOS_pos = None
        for item in self.symbol_pos:
            if self.symbol_pos[item] == '$':
                EOS_pos = item
        if EOS_pos == None:
            raise Exception("No position found for EOS")
        for st1 in self.states:
            if EOS_pos in st1:
                self.add_receiver_state(st1)

def findall(regex, data):
    return findall_rec(regex, data, [])

def findall_rec(regex, data, match_list):
    for i in range(len(data)):
        for j in range(len(data)+1, i, -1):
            aut = FSM()
            aut.wrap('('+regex+')$')
            aut.create_fsm_from_F_FP()
            aut.string_input(data[i:j])
            if aut.in_receiver_state():
                #print("match: " + data[i:j])
                match_list.append(data[i:j])
                data = data[:i] + data[j:]
                #print("New data: " + data)
                return findall_rec(regex, data, match_list)
    return match_list

# aut = FSM()
# #template = 'me+|p(hi)+x?'
# template = r'meph(it|m(hi)*){2,5}'
# aut.wrap('('+template+')$')
# aut.create_fsm_from_F_FP()
# aut.string_input()
# print(aut.in_receiver_state())


print(findall(r'me|p(hi)*', 'phimepyfgppphihihihi'))
test = ["hellhellword", "hellohellowordword", "oowordwordword", "hellhe"]
for string in test:
    print(string)
    print(findall(r'(<a>(hel(l|lo)|o+))<a>(word){1,3}', string))
    print("------------------------------")

test = ["ababx","abaoabo", "aabaabxx", "ooxxx", "x", "ababxxadd", "ababxxlol", "oo", "aababxxxxadd", "aabaabxxaddlol",
        "abadd", "ababadd", "oooo", "abx"]
for string in test:
    print(string)
    res = findall(r'(<a>(a(b|ab)|o+))<a>(x){,3}(add|lol)?', string)
    if len(res) == 1 and res[0] == string:
        print("Valid")
    else:
        print("Invalid")
    print("------------------------------")

print("!!!FINDALL!!!")
test = ["aaa9", "aab9aaa9", "aabaaacbcbhello", "aab9aaa9|"]
for string in test:
    print(findall(r"aa(a|b)9?(cb|cbcb)?(&|)?", string))


#print(findall(r'(<a>(a|b))<a>', 'aa'))     #r'(a|b)(a|b)'
# to_check = ['meph']
# for el in to_check:
#     aut = FSM()
#     #template = 'me+|p(hi)+x?'
#     template = r'meph(it|m(hi)*){2,5}'
#     aut.wrap('('+template+')$')
#     aut.create_fsm_from_F_FP()
#     aut.string_input(el)
#     print(el)
#     print(aut.in_receiver_state())
#     print('--------------------------------------------------------------------')
#for key in aut.FP:
#    print(key)
#    print(aut.FP[key])