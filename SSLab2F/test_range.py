import re

def preprocess_group(regex):
    groupcap_pattern = r'\(<[A-Za-z0-9_]+>'
    groupref_pattern = r'<[A-Za-z0-9_]+>'
    captured_groups  = {}
    occur_old = 0
    occur     = 0
    while True:
        mtch = re.search(groupcap_pattern, regex)
        occur = len(re.findall(groupcap_pattern, regex))
        old_occur = occur
        if mtch == None:
            break
        ind_sta = mtch.span()[0] + 1
        ind_end = mtch.span()[1]
        if ind_sta > 0:
            if regex[ind_sta-1] == '(':
                ind_rp = -1
                string_ptr = ind_sta
                parentheses_ctr = -1
                while string_ptr < len(regex):
                    string_ptr += 1
                    if regex[string_ptr] == ')':
                        parentheses_ctr += 1
                    elif regex[string_ptr] == '(':
                        parentheses_ctr -= 1
                    if parentheses_ctr == 0:
                        ind_rp = string_ptr
                        break
                    if string_ptr == len(regex) - 1 and parentheses_ctr != 0:
                        raise Exception("Parentheses must be balanced")
                group_name = regex[ind_sta+1:ind_end-1]
                if group_name in captured_groups:
                    raise Exception("Attempted to capture a group more than once")
                captured_groups[group_name] = regex[ind_end:ind_rp]
                regex = regex[:ind_sta] + regex[ind_end:ind_rp] + regex[ind_rp:]
                occur = len(re.findall(groupcap_pattern, regex))
        if occur == old_occur:
            break
    while True:
        mtch = re.search(groupref_pattern, regex)
        if mtch == None:
            break
        ind_sta = mtch.span()[0]
        ind_end = mtch.span()[1]
        group_name = regex[ind_sta+1:ind_end-1]
        if group_name not in captured_groups:
            raise Exception("Attempted to reference an uncaptured group")
        regex = regex[:ind_sta] + '(' + captured_groups[group_name] + ')' + regex[ind_end:]
    return regex

def preprocess_range(regex):
    range_pattern = r"\{[0-9]*,[0-9]*\}"
    mtch = re.search(range_pattern, regex)
    if mtch == None:
        return regex
    else:
        ind = mtch.span()[0]
        ind_end = mtch.span()[1]
        if regex[ind-1] in '+|*{}<>&[],(':
            raise Exception("SYNTAX ERROR: range rule must be preceded by a symbol or a group.")
        range = regex[mtch.span()[0]:mtch.span()[1]]
        bounds = re.findall(r'\d+', range)
        lower_bound = (re.findall(r'\{,', range) == [])
        upper_bound = (re.findall(r',\}', range) == [])
        if regex[ind-1] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            regex_start = regex[:ind-1]
            regex_end = regex[ind_end:]
            rep_range = regex[ind-1]
        elif regex[ind-1] == ')':
            ind_lp = -1
            string_ptr = ind-1
            parentheses_ctr = -1
            while string_ptr > 0:
                string_ptr -= 1
                if regex[string_ptr] == '(':
                    parentheses_ctr += 1
                elif regex[string_ptr] == ')':
                    parentheses_ctr -= 1
                if parentheses_ctr == 0:
                    ind_lp = string_ptr
                    break
                if string_ptr == 0 and parentheses_ctr != 0:
                    raise Exception("Parentheses must be balanced")
            regex_start = regex[:ind_lp]
            regex_end = regex[ind_end:]
            rep_range = regex[ind_lp:ind]
            #print(regex_start)
            #print(rep_range)
            #print(regex_end)
        if lower_bound == False and upper_bound == False:
            return regex_start + rep_range + '*' + regex_end
        elif lower_bound == False and upper_bound == True:
            return regex_start + (rep_range + '?') * int(bounds[0]) + regex_end
        elif lower_bound == True and upper_bound == False:
            return regex_start + rep_range * int(bounds[0]) + rep_range + '*' + regex_end
        elif lower_bound == True and upper_bound == True:
            if bounds[0] > bounds[1]:
                raise Exception("SYNTAX ERROR: lower bound must be less or equal to upper bound.")
            return regex_start + rep_range * int(bounds[0]) + (rep_range + '?') * (int(bounds[1]) - int(bounds[0])) + regex_end

def preprocess(regex):
    return preprocess_group(preprocess_range(regex))