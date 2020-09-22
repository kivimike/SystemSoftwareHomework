import re

filename = {}

def get_stats(res, filenames):
    name = res.group(1)
    if name in filenames:
        filenames[name] += 1
    else:
        filenames[name] = 1

def check(string, filenames):
    res = re.match(r"nfs://[a-zA-Z]{1,15}(?:/[a-zA-Z_.]{1,20})?/([a-zA-Z_.]{1,12})$", string)
    if res != None:
        get_stats(res, filenames)
        return True
    return False

with open("data.txt") as f:
    for string in f:
        print('---------------------------------------------------------')
        print(string.rstrip('\n'))
        print(check(string, filename))

print('---------------------------------------------------------')
print(filename)
