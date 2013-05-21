from itertools import ifilter, imap
import re

SEQ_ARITHMETIC = 0
SEQ_GEOMETRIC = 1
SEQ_REPEATING = 2

def err_none(proc, default=None):
    """
    Return a wapper function that will execute proc,
    catching any errors and returning the default value
    """
    def wrap(*args):
        try: return proc(*args)
        except: return default
    return wrap

def match_group_or_none(regex, value):
    #print "matching %s to %s" % (regex, value)
    try: return re.match(regex, value).groups()
    except: return None

def int_or_none(match, group=0):
    try: return int(match[group])
    except: return None

def seconds(match):
    "Takes a 3-tuple of strings for hour/min/sec, eg ('12','01','30') and returns the seconds since 00:00:00"
    return int_or_none(match, 0) * 3600 + int_or_none(match, 1) * 60 + (int_or_none(match, 2) or 0)

sequences = [
        {'name': 'integers', 'repeats': False, 'matches':lambda test_value: int(err_none( lambda regex, value: re.match(regex, value).groups())('([+\-]?\d+$)', test_value)[0]), 'finder': lambda x: x},
        {'name': 'floats', 'repeats': False, 'matches': lambda test_value: float(err_none( lambda regex, value: re.match(regex, value).groups())('([+\-]?\d+\.\d+$)', test_value)[0]), 'finder': lambda x: x},
        #{'name': 'weekdays', 'repeats': True, 'repeat_length': 7, 'matches': ['m(on(day)?)?', 't(ue(sday)?)?', 'w(ed(nesday)?)?', 't(hu(rsday)?)?', 'f(ri(day)?)?', 's(at(urday)?)?', 's(un(day)?)?']},
        #{'name': 'months', 'repeats': True, 'repeat_length': 12, 'matches': ['j(an(uary)?)?', 'f(eb(ruary)?)?', 'm(ar(ch)?)?', 'a(pr(il)?)?', 'm(ay)?', 'j(une?)?', 'j(uly?)?', 'a(ug(ust)?)?', 's(ep(tember)?)?', 'o(ct(ober)?)?', 'n(ov(ember)?)?', 'd(ec(ember)?)?', ]},
        {'name': 'weekdays', 'repeats': True, 'repeat_length': 7, 'matches': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
        {'name': 'weekdays', 'repeats': True, 'repeat_length': 7, 'matches': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},
        {'name': 'weekdays', 'repeats': True, 'repeat_length': 7, 'matches': ['M', 'T', 'W', 'T', 'F', 'S', 'S']},
        {'name': 'months', 'repeats': True, 'repeat_length': 12, 'matches': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']},
        {'name': 'months', 'repeats': True, 'repeat_length': 12, 'matches': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
        {'name': 'months', 'repeats': True, 'repeat_length': 12, 'matches': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']},
        {'name': 'chemical elements', 'repeats': False, 'matches': ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar']},
        {'name': 'hour:min', 'repeats': True, 'repeat_length': 86400, 'matches': lambda test_value: seconds(err_none(lambda regex, value: re.match(regex, value).groups())('(\d?\d):(\d\d)()$', test_value)), 'finder': lambda x: "%02d:%02d" % (x//3600, (x-(x//3600*3600))/60)},
        {'name': 'hour:min:sec', 'repeats': True, 'repeat_length': 86400, 'matches': lambda test_value: seconds(err_none(lambda regex, value: re.match(regex, value).groups())('(\d?\d)?:(\d\d):(\d\d)', test_value)), 'finder': lambda x: "%02d:%02d:%02d" % (x//3600, (x-(x//3600*3600))/60, x % 60)},
]

def recognise(input_sequence):
    analysis = analyse(input_sequence)
    return analysis[0]['name'] if analysis else None

def analyse(input_sequence):
    """
    Return the most likely match for the input_sequence or None
    if a match could not be found. A match is foud if all elements
    of the input_sequence match a single test_sequence. Matches are
    prioritised if a pattern can be found in them. 
    """

    def matching_indices(input_sequence, test_sequence):
        """
        Generator for getting the indices in the test_sequence that match
        sucessive elements from the input_sequence. It remembers the position
        of the last match found, so that searches for subsequent items in the 
        input_sequence will start from the next position along. Eg. when
        searching for weekdays with the sequence ['s','s'] the first will match
        Saturday, and the next will match Sunday. 
        """
        start_at = 0
        matches = test_sequence['matches']
        for test_value in input_sequence:
            if callable(matches):
                yield err_none(matches)(str(test_value))
            else:
                n = len(matches)
                default_matcher = lambda matches, index, test_value: index if re.match('^%s$' % matches[index], str(test_value), re.I) else None
                match_iter = imap(lambda i: default_matcher(matches, (i+start_at)%n, test_value), range(n))
                match = next((m for m in match_iter if m != None), None)
                start_at = match + 1 if match != None else 0
                yield match

    indices = [list(matching_indices(input_sequence, s)) for s in sequences]
    patterns = [pattern(i) for i in indices]
    results = zip(sequences, indices, patterns)
    results = filter(lambda r: (r[1] and all(x != None for x in r[1])), results) #remove ones that don't have every element match
    results = sorted(results, cmp=lambda x, y: 2 * cmp(x[2],y[2]) + cmp(x[1],y[1]), reverse=True) #sort with pattern priority over indices
    return next(iter(results), None)

def extend(input_sequence, extend_by):
    """
    Take the given input sequence, analyse it, and, if it
    is recognised as a sequence, compute and return the 
    next extend_by values from the sequence
    """
    analysis = analyse(input_sequence)
    if analysis == None: return None
    matched_sequence, match_indices, pattern = analysis
    if pattern == None: return None

    n = len(input_sequence)
    extended_indices = [get_value_at(pattern[0], i) for i in range(n, n + extend_by)]
    extended_values = []
    for ei in extended_indices:
        if matched_sequence['repeats']: 
            ei = ei % matched_sequence['repeat_length']
        if callable(matched_sequence.get('finder')):
            extended_values.append(matched_sequence['finder'](ei))
        else:
            extended_values.append(matched_sequence['matches'][int(round(ei))])
        
    return extended_values

def pattern(input_sequence):
    """
    Find a pattern in a given input_sequence.
    input_sequence should be a list of numeric values. 
    """
    if not input_sequence or any(i == None for i in input_sequence):
        return None
    steps_arith = get_steps(input_sequence)
    repeats_arith = detect_repeats(input_sequence)
    step_repeats_arith = detect_repeats(steps_arith)

    steps_geom = get_steps(input_sequence, err_none(float.__truediv__, 0))
    step_repeats_geom = detect_repeats(steps_geom)

    if len(set(steps_arith)) == 1:
        return ([[input_sequence[0]], [steps_arith[0]]], SEQ_ARITHMETIC)
    elif repeats_arith:
        return ([repeats_arith], SEQ_REPEATING)
    elif step_repeats_arith:
        return ([[input_sequence[0]], step_repeats_arith], SEQ_ARITHMETIC)
    elif len(set(steps_geom)) == 1:
        return ([[input_sequence[0]], [steps_geom[0]]], SEQ_GEOMETRIC)
    elif step_repeats_geom:
        return ([[input_sequence[0]], step_repeats_geom], SEQ_GEOMETRIC)

def get_steps(input_sequence, diff_function=float.__sub__):
    """ Returns the difference between sucessive elements in the 
    sequence using the diff function (by default, subtraction)"""
    return [round(diff_function(float(input_sequence[i]), float(input_sequence[i-1])), 3) for i in range(1,len(input_sequence))]

def detect_repeats(input_sequence):
    """
    Try and find repeating runs of any length up to 1/2
    of the length of the input_sequence

    We try lengths successively as the variable l. 
    For each i from 0..l, try and verify that
    the i'th element is the same for each repetition (r)
    
    ((n - i - 1)/l + 1) is the number of positions we 
    can test for the given sequence, 
    eg, for the sequence [1,2,3,1,2,3,1] testing repetitions
    of length 3, when i=0 we can check 3 positions (0, 3, and 6)
    for equality, but when i=1, we just check positions 1 and 4
    """
    n = len(input_sequence)
    for l in range(1, n/2 + 1): 
        if all([len(set([input_sequence[r*l+i] for r in range((n - i - 1)/l + 1)])) == 1 for i in range(l)]):
            return input_sequence[:l]
    return None
         
def get_value_at(pattern, index):
    """
    Takes a pattern representation from the pattern() function
    and an index, and returns the value we would expect at that
    index in a series built from that pattern.
    """
    if pattern == None:
        return None
    if len(pattern) == 1:
        return pattern[0][index % len(pattern[0])]
    elif len(pattern) == 2 and len(pattern[1]) == 1: #Optimization, single step sequence, can just multiply step by index
        return pattern[0][0] + (index * pattern[1][0])
    elif index == 0:
        return pattern[0][index]
    else:
        return get_value_at(pattern, index - 1) + get_value_at(pattern[1:], index - 1)
