# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, value = None, c = None, type_ = None):
        self.value = value
        if c is None:
            self.children = {}
        self.type = type_

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if not isinstance(key, str) and not isinstance(key, tuple):
            raise TypeError("Key must be immutable ordered sequence")
        if self.type is None:
            self.type = type(key)
        if type(key) != self.type:
            raise TypeError("Key types must all be the same")
        if len(key) == 0: #key is empty
            self.value = value
        else: 
            index = key[:1]
            if index not in self.children: #adds letter if not in trie
                self.children[index] = Trie(type_ = self.type)
            self.children[index][key[1:]] = value  

                
    def find_trie(self, key, pref=False): #find the trie that a given key leads to
        if type(key) != self.type:
            raise TypeError("Key type must match Trie type")
        if key not in self and pref == False:
            raise KeyError("Key not in Trie")
        if len(key) == 0:
            return self
        else:
            index = key[:1] 
            if index in self.children:
                return self.children[index].find_trie(key[1:], pref)   
            else:
                return None
        
        
 
    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        return self.find_trie(key).value

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        if type(key) != self.type:
            raise TypeError("Key type must match Trie type")
        if key not in self:
            raise KeyError("Key not in Trie")
        if len(key) == 0:
            self.value = None #sets value to none to delete it
        else:
            index = key[:1]
            self.children[index].__delitem__(key[1:])

            

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        if len(key) == 0:
            return self.value is not None
        else:
            index = key[:1]
            if index in self.children:
                return self.children[index].__contains__(key[1:])
            else:
                return False #if a letter is not in the trie's children



    def get_keys(self): #generates all keys in trie
        for i in self.children:
            if self.children[i].value is not None:
                yield i
            for j in self.children[i].get_keys():
                yield i + j


        
        
    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        for i in self.get_keys(): #adds keys and values of keys to tuples
            yield (i, self.__getitem__(i))
         
            

        
        
        
        



def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    t = Trie()
    sentences = tokenize_sentences(text)
    for sentence in sentences:
        for word in sentence.split():
            if word in t:
                t[word] = t[word] + 1 #adds 1 to every word's value
            else:
                t[word] = 1
    return t


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    t = Trie()
    sentences = tokenize_sentences(text)
    for sentence in sentences:
        key = tuple(sentence.split())
        if key in t:
            t[key] = t[key] + 1 #adds one to the sentence's value
        else:
            t[key] = 1
    return t

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    words = []
    if prefix in trie:
        words.append((prefix, trie[prefix]))
    t = trie.find_trie(prefix, pref=True)
    if t is None:
        return []
    for k, v in t:
        words.append((prefix + k, v))
    if max_count is None or len(words) < max_count:
        return [w[0] for w in words] #returns every word
    words = sorted(words, key = lambda i: i[1], reverse=True) #sorted words based on frequency
    
    return [w[0] for w in words[:max_count]]
    
    
    
#inserts a character at every index and adds the word if its in trie
def insertion(trie, prefix, used):
    edits = []
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(prefix)):
        for letter in alpha:
            new_prefix = prefix[:i] + letter + prefix[i:]
            if new_prefix not in used:
                used.add(new_prefix)
                if new_prefix in trie:
                    edits.append((new_prefix, trie[new_prefix]))
    return edits
           
#deletes a character at every index and adds the word if its in trie     
def deletion(trie, prefix, used):
    edits = []
    for i in range(len(prefix)):
        new_prefix = prefix[:i] + prefix[i+1:]
        if new_prefix not in used:           
            used.add(new_prefix)
            if new_prefix in trie:
                edits.append((new_prefix, trie[new_prefix]))
    return edits

#replaces a characters at every index with a letter and adds the word if its in trie
def replacement(trie, prefix, used):
    edits = []
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(prefix)):
        for letter in alpha:
            if letter != prefix[i]:
                new_prefix = prefix[:i] + letter + prefix[i+1:]
                if new_prefix not in used:
                    used.add(new_prefix)
                    if new_prefix in trie:
                        edits.append((new_prefix, trie[new_prefix]))
    return edits

#switches characters of every adjacent index and adds the word if its in trie
def transpose(trie, prefix, used):
    edits = []
    for i in range(len(prefix)-1):
        new_prefix = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
        if new_prefix not in used:
            used.add(new_prefix)
            if new_prefix in trie:
                edits.append((new_prefix, trie[new_prefix]))
    return edits

#
def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    auto_complete = autocomplete(trie, prefix, max_count)
    used = set(auto_complete)
    #all four edits keeping track of used words
    edits =  insertion(trie, prefix, used) + deletion(trie, prefix, used) + replacement(trie, prefix, used) + transpose(trie, prefix, used) 
    if max_count is None:
        all_edits = [w[0] for w in edits]
        return auto_complete + all_edits
    if len(auto_complete) < max_count:  
        if len(edits) < max_count - len(auto_complete):
            all_edits = [w[0] for w in edits]
            return auto_complete + all_edits
        edits = sorted(edits, key = lambda i: i[1], reverse=True) #sorts words by most frequent
        frequent_edits = [w[0] for w in edits[:max_count - len(auto_complete)]] #gets # most frequent
        return auto_complete + frequent_edits
    else:
        return auto_complete

#gets next character in pattern, combining adjacent stars
def next_char(pattern):
    if len(pattern) == 1:
        return None
    if pattern[1] == '*':
        if pattern[0] == '*':            
            pattern = pattern[1:]
            return next_char(pattern)
        else:
            pattern = pattern[0] + pattern[2:]
            return next_char(pattern)
    return pattern[1], pattern

#gets sequences of letters that end in the character
def up_to_next(trie, nextchar):
    for i in trie.children:
        if i == nextchar:
            yield i
        for j in up_to_next(trie.children[i], nextchar):
            yield i + j
#gets the rest of the words if the last charcter in the pattern is a star
def get_therest(trie, pattern, word):
    yield from trie.get_keys()
    pattern = pattern[1:]

#recursive matching function
def pattern_matching(trie, pattern, word):  
    if len(pattern) != 0:
        char = pattern[0]
        if char == '*':
            if next_char(pattern) is None: #if there are only stars left
                yield from get_therest(trie, '*', word)
            else:
                nextchar, pattern = next_char(pattern)
                if nextchar == '?': #if next is a ?, switch the * and ?
                    pattern = pattern[1] + pattern[0] + pattern[2:]
                    yield from pattern_matching(trie, pattern, word)
                else:
                    pattern = pattern[1:]
                    for i in up_to_next(trie, nextchar): #gets all words up to next letter
                        if i in trie and next_char(pattern) is None:
                            yield i
                        t = trie.find_trie(i, pref=True)
                        for j in pattern_matching(t, pattern[1:], word+i):
                            if i + j in trie:
                                yield i + j
              
        elif char == '?':            
            if (len(pattern) > 1 and next_char(pattern) is None) or len(pattern) == 1:
                for i in trie.children: #yields children if the last character in pattern or only stars left
                    if i in trie:
                        yield i
            for i in trie.children: #yields acceptable children of children
                t = trie.find_trie(i, pref=True)
                for j in pattern_matching(t, pattern[1:], word + i):
                    if i + j in trie:
                        yield i + j 
        else:
            if char in trie.children:
                if (len(pattern) > 1 and next_char(pattern) is None) or len(pattern) == 1:
                    if char in trie: #yields children if the last character in pattern or only stars left
                        yield char
                t = trie.find_trie(char, pref=True)                  
                for j in pattern_matching(t, pattern[1:], word+char): #yields accepatble children of character
                    if char + j in trie:
                        yield char + j
    
        


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    return [(w, trie[w]) for w in pattern_matching(trie, pattern, '')]

        
    
    


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    {'children': {'c': {'children': {'a': {'children': {'t': {'children': {}, 'value': 'kitten'}, 'r': {'children': {'p': {'children': {'e': {'children': {'t': {'children': {}, 'value': 'rug'}}, 'value': None}}, 'value': None}}, 'value': 'tricycle'}}, 'value': None}}, 'value': None}}, 'value': None}
    p = make_word_trie('toonces was a cat who could drive a car car car crashed very fast until he crashed.')
    z = make_word_trie("a an ant anteater a an ant anteater aratt a antester, anteating")
    m = make_word_trie("man mat mattress map me met a man a a a map man met meet")
    #print([(k, v) for k, v in z])
    #print(autocomplete(z, 'a', 3))
    used = set()
#    print(insertion(z, 'abc', used))
#    print(deletion(z, 'anteatera', used))
#    print(replacement(z, 'ant', used))
#    print(transpose(z, 'anteatign', used))
    print(word_filter(m, 'm*p'))
    #print('' in m)
    #r = Trie()
    #print(list(up_to_next(m, 'a')))
    print(next_char('G**'))
    #print(sorted(used))
    #print('abc' in used)
    
    with open("11-0.txt", encoding="utf-8") as f:
        text = f.read()
    words = []
    x = make_phrase_trie(text)
    z = make_word_trie(text)
    count = 0
    for k, v in x:
        words.append((k,v))
        count+=v
    print(count)
    words = sorted(words, key = lambda i: i[1], reverse=True)
    print([s[0] for s in words[:6]])
    ac = autocorrect(z, 'hear', 12)
    print(ac)
    with open("pg5200.txt", encoding="utf-8") as f:
        text = f.read()
    words = []
    x = make_word_trie(text)
    print(word_filter(x, 'c*h'))
    
    with open("98-0.txt", encoding="utf-8") as f:
        text = f.read()
    x = make_word_trie(text)
    print(word_filter(x, 'r?c*t'))
    
    with open("1342-0.txt", encoding="utf-8") as f:
        text = f.read()
    x = make_word_trie(text)
    ac = autocorrect(x, 'hear')
    print(ac)
    
    with open("pg345.txt", encoding="utf-8") as f:
        text = f.read()
    x = make_word_trie(text)
    counter = 0
    counter2 = 0
    for i, j in x:
        counter += 1
        counter2 += j
    print(counter)
    print(counter2)
        
    
#    for k, v in x:
#        words.append((k,v))
#    words = sorted(words, key = lambda i: i[1], reverse=True)
#    print([s[0] for s in words[:6]])
    
    
    
    
    
    