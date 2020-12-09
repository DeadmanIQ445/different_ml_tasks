import en_core_web_sm
nlp = en_core_web_sm.load()

import nltk
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()


class Person():
    def __init__(self, name):
        self.name = name
        self.attr = {}
        self.verb = {}
        self.bag = {}
entities = []


def process(inp):
    if '?' in inp or 'who ' in inp.lower() or 'what ' in inp.lower():
        question(inp)
    else:
        statement(inp)

def decompose(doc):
    """    
    :param doc: result of nlp(sentence)

    :return root: root of the sentence, usually a verb
    :return nsubj:
    :return attr: attribute of nsubj or of root
    :return flag_not: marks if the sentence is negated
    """
    root = [token for token in doc if token.head == token][0]
    subject = [token for token in root.subtree if token.dep_=='nsubj']
    flag_not = True
    attr = None
    if len(subject)>0: 
        subject = subject[0]
    else: 
        None 
    if subject.head != root:
        for tok in doc:
            if tok.dep_ == 'neg':
                flag_not = False
            if tok.dep_ == 'nsubj':
                attr = root
                subject = tok
                root = tok.head
        return root, subject, attr, flag_not
                
    for tok in root.children:
        if tok.dep_ == 'neg':
            flag_not = False
        if tok.dep_ == 'attr' or tok.dep_ == 'acomp' or tok.dep_ == 'dobj' or tok.dep_ == 'prep':
            attr = tok
    return root, subject, attr, flag_not

def proc_attr(attr, doc, root):
    for i in attr.subtree:
        if root == i:
            return attr.text
    slc = doc[attr.left_edge.i : attr.right_edge.i+1]
    return " ".join([tok.lemma_ for tok in slc if tok.text != 'a' and tok.text != 'the'])
    

def statement(inp):
    doc = nlp(inp)
    root, subj, atr,flag_not = decompose(doc)
    obj = get_entity(str(subj.text))
    atr = proc_attr(atr, doc, root)    
    if 'be' == root.lemma_:        
        obj.attr[atr] = flag_not
    elif 'have' == root.lemma_:
        obj.bag[atr] = flag_not
    else:
        if flag_not:
            obj.verb.setdefault(root.lemma_, set([])).add(atr)
        else:
            obj.verb[root.lemma_].discard(atr)

    # Noting implicit mention of atribute        
    for tok in subj.subtree:
        if tok.dep_ == 'compound':
            obj.attr[tok.lemma_.lower()] = True

    
def get_entity(name):
    """Retreives the entity by name. If not found create new entity."""
    for i in entities:
        if i.name == name:
            return i
    ret = Person(name)
    entities.append(ret)
    return ret

def decompose_question(doc):
    """Same as decompose, but covers some corner cases with questions."""
    root = [token for token in doc if token.head == token][0]
    subject = [token for token in root.subtree if token.dep_=='nsubj']
    subject = subject[0] if len(subject)>0 else None
    flag_not = True
    attr = None
    

    for tok in root.subtree:
        if tok.dep_ == 'neg':
            flag_not = False
        if tok.dep_ == 'attr' or tok.dep_ == 'acomp' or tok.dep_ == 'dobj' or tok.dep_ == 'prep':
            attr = tok
            if subject is None :
                subject = [token for token in tok.subtree if token.dep_=='compound'][0]
            if subject.lemma_=='who':
                subject = None
    return root, subject, attr, flag_not

def question(inp):
    doc = nlp(inp)

    root, subj, atr,flag_not = decompose_question(doc)
    atr = proc_attr(atr, doc, root)    
    if 'who' in inp.lower():
        if 'be' == root.lemma_:
            print(", ".join([ent.name for ent in entities if ent.attr.get(atr, None) is not None and ent.attr.get(atr, None)==flag_not]))
        elif 'have' == root.lemma_:
            print(", ".join([ent.name for ent in entities if ent.bag.get(atr, False) == flag_not]))
        else:
            print(", ".join([ent.name for ent in entities if atr in ent.verb.get(root.lemma_, [])]))
    elif 'what' in inp.lower():
        obj = get_entity(str(subj.text))
        if 'have' == root.lemma_:
            print(", ".join([elem for (elem,val) in obj.bag.items() if val]))
        else:
            print(obj.verb.get(root.lemma_, []))
            
    else:
        obj = get_entity(str(subj.text))
        if 'be' == root.lemma_:
            print(obj.attr.get(atr, "Unknown"))
        elif 'ha' == root.lemma_:
            print(obj.bag.get(atr, "Unknown"))
        else:
            print(obj.verb.get(root.lemma_, "Unknown"))


print("Names are case-sensitive.")
print("On question like 'Who is not [adj|noun]?' program returns\nonly entities that are explicitly said to not be [adj|noun].")
print("On quesion like 'Whoe does not have [XXX]]?' program returns\nboth entities that are said to not have [XXX] and entities that are uknown to.")
print("Exit through 'ctrl+c' or through empty input")
a = input("> ")
while a:
    try:
        process(a)
    except:
        print("Input is wrong, please english grammar.")
    a = input("> ")


print("Here are all entities")
for ent in entities:
    print(ent.__dict__)
