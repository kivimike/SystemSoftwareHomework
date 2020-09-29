import AppClass2_sm
alphabet = set("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
#ex_alphabet = set("_.qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
filename = {}

def get_stats(name, filenames):
    if name in filenames:
        filenames[name] += 1
    else:
        filenames[name] = 1

class AppClass:


    def __init__(self):
        self._fsm = AppClass2_sm.AppClass_sm(self)
        self._is_acceptable = False
        self.counter = 0
        self.filename = ''
        self.current_string = ''

    def Counter(self):
        self.counter += 1

    def ResetCounter(self):
        self.counter = 0

    def Acceptable(self):
        self._is_acceptable = True

    def Unacceptable(self):
        self._is_acceptable = False

    def Save_name(self):
        self.filename = self.current_string[-self.counter:]

    def check(self, string):
        self.current_string = string
        self._fsm.enterStartState()
        if(len(string) < 6):
            return False, None
        for c in string[:6]:
            self._fsm.header(self.counter, c)
        for c in string[6:]:
            self._fsm.symb(c, self.counter)
        self._fsm.EOS(self.counter)
        return self._is_acceptable, self.filename

#checker = AppClass()
#print(checker.check("nfs://hello/hell_/_heljbchj"))

try:
    with open("data.txt") as f:
        for string in f:
            checker = AppClass()
            print('---------------------------------------------------------')
            print(string.rstrip('\n'))
            flag, f_name = checker.check(string.rstrip('\n'))
            get_stats(f_name, filename)
            print(str(flag) + " " + f_name)
except IOError as e:
    print("No file found")

print('---------------------------------------------------------')
print(filename)