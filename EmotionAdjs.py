# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 21:30:18 2020

@author: Gary Zhang

Some important comments on how to use this file:
 - All variables are given in camel case (e.g. wordList)
 - All dictionary entries are given in snake case (e.g. emotion_adj_list), and the variable
   name is always the same as the string they point to. This is simply to make it easier for
   an IDE to suggest the correct entry name when typing, because many IDEs will automatically
   suggest variable names.

"""

import csv
import nltk

# edit these names to be whatever you've named these corpora on your computer
corpusList = ["SachsCorpus.csv", "Brown_Adam_Utterance_Edit2.csv", "Brown_Sarah_Utterance_Edit2.csv",
              "Kuczaj_Utterance_Edit2.csv", "Weist_Matt_Utterance_Edit2.csv"]

emotionAdjs  = ["active", "afraid", "aggressive", "agreeable", "alone", "alright", "amazed",
                "angry", "annoying", "anxious", "ashamed", "awful", "bad", "bashful", "boring",
                "bored","bothered","bothering","brave","calm","calmed","certain","collected",
                "concern","concerned", "confused", "confusing", "courage", "cranky", "curious",
                "disappointed", "disappointing", "disappointment", "discouraged","disgusted",
                "disgusting","distracted","disturbed", "disturbing", "doubted", "enjoyed","enjoying",
                "envious", "evil", "excited", "exciting", "ferocious", "friendly", "frightened", 
                "frightening", "fun", "gay","gentle", "glad", "good", "gracious", "gross", "happy",
                "hated", "hateful", "helpless", "hopeful", "hopeless", "horrible", "impatient",
                "interested", "interesting", "irritated","jealous","jolly","lonely","lonesome",
                "loving", "lucky", "mad", "merry", "miserable", "naughty", "nervous", "nice", "numb",
                "okay", "peaceful", "peppy", "powerful", "proud",#"pleased","pleasing","pleasant",
                "quiet", "rested", "restless", "sad", "safe", "scared", "scary", "serious", "shame",
                "shocked", "shy", "sorry", "still", "stressed", "surprised", "surprising", "tense",
                "unhappy", "unpleasant", "upset", "weird", "well", "wicked", "worried", "worrying"]
emotionNouns = ["admirer","amusement", "calm", "doubt","enjoyment", "fright", "enthusiasm", "fright",
                "grief", "happiness", "hate" ,"hope", "interest", "joy", "love", "panic", "scare",
                "shock", "stress", "stress", "upset", "worry"]
emotionVerbs = ["admire", "bother", "calm", "concern", "disappoint", "disgust", "distract", "disturb",
                "doubt", "enjoy", "frighten", "frustrate", "hate", "hope", "interest", "irritate",
                "love", "panic", "scare", "shock", "stress", "surprise","upset","worry"]
emotionPhrase= ["bad feeling", "feel all right", "feel alright", "feel awful", "feel bad", "feel better",
                "feel good", "feel great","feel nice","feel ok","feel okay","feel well","feel worse",
                "good feeling","have a good time","have fun","to be all right","to be alright"]

verbTags = ["v", "cop", "pos","part"]
# we include participles because then Python can detect progressive tense like "where are you going",
# but it's worth noting this could lead to false positives: in "I see a flying plane", Python will
# classify "flying" is a verb
# I'm not going to include auxiliary verbs since this will almost always be unhelpful, such as in the
# sentence "she is feeling happy", where the only verb that matters for our purposes is "feel". The
# same is true for modals, so I'm not including them here

possibleEmotionWord = ["alive","amazing","appreciate","aw","awake","bitter","blue",
                       "bug", # when it acts as a verb?
                       "busy","cheer","clean","cold","comfortable","cooperative","dreaming","dreamt",
                       "creepy","cried","cry","dirtier","dirtiest","dirty","down","drowsy","drunken",
                       "foggy","free","freezing","funny","fussy","healthy","helpful","hungrier",
                       "hungriest","hungry","hurt","hurting","hurts","itch","kiss","laugh","lazy",
                       "loopy","lost","low","mean","messy","mild","mushy","nicer","offensive","ouch",
                       "ow","pain","poor","rattle","rough","secure","sick","sleepy","smile","smiling",
                       "sore","spoiled","starving","sting","strong","stubborn","tender","terrible",
                       "thirsty","thoughtful","tired","uncomfortable","warm","wild","yuck","yum","slow"]

CorporaRows = [] # creates a Python dictionary for each utterance, plus metadata

# list of dictionary entry names (kind of like metadata names)
# this makes it easier for Spyder to suggest which entries I want
emotion_adj_list    = "emotion_adj_list"     # list of strings
emotion_adv_list    = "emotion_adv_list"     # list of strings
emotion_noun_list   = "emotion_noun_list"    # list of strings
emotion_verb_list   = "emotion_verb_list"    # list of strings
verb_list           = "verb_list"            # list of strings
has_preposition     = "has_preposition"      # bool
negated_emotion_adj = "negated_emotion_adj"  # bool

adj_followed_by_preposition  = "adj_followed_by_preposition"   # bool
noun_followed_by_preposition = "noun_followed_by_preposition"  # bool

adj_environment_list = "adj_environment_list"# list of list of 2-tuples
# example: "I see a happy dog and ten blue cats" should result in
# [ [("a","det"), ("dog","n")] , [("ten", "det"), ("cat","n")] ]

def getUtterance(w):
   """
   Finds the first utterance within the corpora with the exact characteristics specified.

   Parameters
   ----------
   w : str
      The string of words in the utterance.

   Returns
   -------
   utterance : dict
      The utterance within the set of corpora that matches the input. If no utterance has the 
      characteristics specified in the input, the function raises an exception.

   """
   utterance = False
   for u in CorporaRows:
      if u['w'].strip() == w.strip():
         utterance = u
         break
   if not utterance:
      raise Exception("Oops! You just called getUtterance(), but it looks like there isn't an "+
                      "utterance with the exact same words or ID as the one you specified. " +
                      "Check the way you're spelling the words, or check that you're not "+
                      "leaving any stray periods at the end of each sentence.")
   return utterance

def concurrence_EmotionAdjVerb(utterance):
   """
   Given an utterance that has a known list of emotion adjectives, this function finds the verbs
   that precede each emotion adjective. This is a heuristic to find the head of the VP that contains
   the emotion adjective, and it will help us to create reliability cues for each adjective.
   
   Example output: 
   
    -   "I saw a happy dog" → ``[("happy", "see")]``
   
    -   "Is that a happy face or sad face?" → ``[("happy", "be"), ("sad", "be")]``
   
    -   "I feel so happy so happy" → ``[("happy", "feel"), ("happy", "feel")]``
    
    -   "angry" → ``[("angry", None)]``
    
    -   "hello" → ``[(None, None)]``
   
   Duplicates are not removed. If no adjectives are present, then a list containing ``(None, None)``
   is returned. If no verb precedes the adjective, ``None`` is returned. 

   Parameters
   ----------
   utterance :  dict
      The utterance.

   Returns
   -------
   conditions :  list
      A list of the pairings between emotion adjectives and verbs preceding them, in
      the form ``[(adj,verb), (adj,verb), ...]``.
   """
   conditions = []
   
   if len(utterance[ emotion_adj_list ]) == 0: # utterance has no emotion adjectives
      conditions = [(None,None)]
   elif len(utterance[ verb_list ]) == 0: # utterance has no verbs, but it has emotion adjectives
      for adj in utterance[ emotion_adj_list ]:
         conditions.append( (adj,None) )
   else: # utterance has verbs and emotion adjectives
      verbIndices = [ (None,0) ]
      adjIndices  = []
      lastIndex = 0
      for verb in utterance[ verb_list ]:
         lastIndex = utterance["mw_stem"].index(verb, lastIndex)
         if lastIndex == 0:
            # this makes sure "feel good" is [("feel",0)] instead of [(None,0),("feel",0)]
            verbIndices = [] 
         verbIndices.append( (verb,lastIndex) )
         #print(verbIndices)
         lastIndex += 1 # don't include the same index again, such as in "I be what I be", resulting in [("be",2),("be",12)] instead of incorrect [("be",2),("be",2)]
      verbIndices.append( (None, len(utterance['mw_stem'])) ) # prevents IndexErrors in the comparisons below
      
      lastIndex = 0
      for adj in utterance[ emotion_adj_list ]:
         lastIndex = utterance["mw_stem"].index(adj,  lastIndex)
         adjIndices.append( (adj,lastIndex) )
      for (adj,index) in adjIndices:
         for k in range(len(verbIndices) - 1):
            if verbIndices[k][1] <= index and index < verbIndices[k + 1][1]:
               conditions.append( (adj, verbIndices[k][0]) )
   return conditions

def concurrence_EmotionNounVerb(utterance):
   """
   This is TEMPORARY and UNTESTED, and is used to get PRELIMINARY data.
   Do not use this yet!
   """
   conditions = []
   
   if len(utterance[ emotion_noun_list ]) == 0: # utterance has no emotion adjectives
      conditions = [(None,None)]
   elif len(utterance[ verb_list ]) == 0: # utterance has no verbs, but it has emotion adjectives
      for n in utterance[ emotion_noun_list ]:
         conditions.append( (n,None) )
   else: # utterance has verbs and emotion adjectives
      verbIndices = [ (None,0) ]
      nounIndices  = []
      lastIndex = 0
      for verb in utterance[ verb_list ]:
         lastIndex = utterance["mw_stem"].index(verb, lastIndex)
         if lastIndex == 0:
            # this makes sure "feel good" is [("feel",0)] instead of [(None,0),("feel",0)]
            verbIndices = [] 
         verbIndices.append( (verb,lastIndex) )
         #print(verbIndices)
         lastIndex += 1 # don't include the same index again, such as in "I be what I be", resulting in [("be",2),("be",12)] instead of incorrect [("be",2),("be",2)]
      verbIndices.append( (None, len(utterance['mw_stem'])) ) # prevents IndexErrors in the comparisons below
      
      lastIndex = 0
      for n in utterance[ emotion_noun_list ]:
         lastIndex = utterance["mw_stem"].index(n,  lastIndex)
         nounIndices.append( (n,lastIndex) )
      for (n,index) in nounIndices:
         for k in range(len(verbIndices) - 1):
            if verbIndices[k][1] <= index and index < verbIndices[k + 1][1]:
               conditions.append( (n, verbIndices[k][0]) )
   return conditions



for corpus in corpusList: # open CSVs
   with open(corpus, newline='') as csvfile:
      csvReader = csv.reader(csvfile, delimiter=',')
      count = -1
      csvItems = ['rownum', 'utt_len', 'uID', 'langtype', 'corpus', 'file', 'name', 'role',
                  'age', 'sex', 'group', 'SES', 'Y', 'M', 'D', 'agemonth', 'who', 'Target',
                  'Repetition', 'w', 'mw_stem', 'pos_c', 't_type'#, 'Sent_type',
                  #'Search Term/ Infinitive', 'Remainder of Clause, if more',
                  #'Modifying Clause/ Phrase?', 'Conjunction/ Preposition, if any',
                  #'C/P, if "other"', 'Adjectives/ Adverbs?', 'Adj/Adv', 'Birthday'
                  ]
      
      for row in csvReader:
         count += 1
         if count == 0: # check that the header row is the same for all CSV files we're using
            if csvItems[1:] != row[1:]: # we skip element 0, 'rownum', because some CSVs have a Unicode byte-order mark, while others don't
               print(csvItems)
               print(row)
               print(corpus)
               raise Exception("Oops! It looks like the CSV file you entered isn't of the " +
                               "correct format. The first row should be the header, which " +
                               "includes items like " + csvItems[0] + ", " + csvItems[1] +
                               ", " + csvItems[2] + ", and so forth. Somehow, the CSV file " +
                               "you used has a different header. Perhaps a few columns have "+
                               "been accidentally switched, like mw_stem and pos_c. Check to"+
                               "be sure they are in the exact same order, and exact same " +
                               "spelling and capitalization.")
         else:
           
            utterance = {}
            i = 0
            for item in csvItems: # create an utterance (type dict), which stores information about each row in the CSV
               utterance[item] = row[i]
               i += 1
            
            utterance[ emotion_adj_list ]     = [] # a list for all emotion adjectives in the utterance
            utterance[ emotion_noun_list ]    = [] # a list for all emotion nouns in the utterance
            utterance[ emotion_verb_list ]    = [] # a list for all emotion verbs in the utterance
            utterance[ emotion_adv_list ]     = [] # a list for all emotion adverbs in the utterance

            utterance[ verb_list ]            = [] # a list for *all* verbs in the sentence, in order

            utterance[ adj_environment_list ] = [] # a list for the word immediately before and after each adjective
            
            # by default, we assume the utterance does not have these properties
            utterance[ adj_followed_by_preposition ]  = False
            utterance[ noun_followed_by_preposition ] = False
            utterance[ negated_emotion_adj ]          = False
            
            # the list of words, after being stemmed, in each utterance
            wordList = utterance["mw_stem"].split()
            # the list of parts of speech in each utterance
            posList  = utterance["pos_c"].split()
            
            for n in range(len(wordList)):   # n = index for each word in utterance
               word = wordList[n]            # get current word
               pos  = posList[n]             # current word's part of speech
               
               # if current word is an adjective
               if pos == "adj":
                  if word in emotionAdjs:
                     utterance[ emotion_adj_list ].append(word)
                     if n > 0 and wordList[n - 1] == "not":
                        utterance[ negated_emotion_adj ] = True

                  # finds word before current word; if this is the first word in the utterance,
                  # then the previous word is defined as an empty string, and the previous part
                  # of speech is defined as None
                  prevWord = ""
                  prevPos  = None
                  if n > 0:
                     prevWord = wordList[n - 1]
                     prevPos  = posList[n - 1]
                  
                  # finds word after current word; if this is the last word in the utterance,
                  # then the next word is defined as an empty string, and its part of speech
                  # is defined as None
                  nextWord = ""
                  nextPos  = None
                  if n < len(wordList) - 1:
                     nextWord = wordList[n + 1]
                     nextPos  = posList[n + 1]
                     if posList[n + 1] == 'prep':
                        utterance[ adj_followed_by_preposition ] = True

                  utterance[ adj_environment_list ].append([ (prevWord,prevPos) , (nextWord,nextPos) ])

               # if current word is a noun
               elif pos == "n":
                  if word in emotionNouns :
                     utterance[ emotion_noun_list ].append(word)
                  if n < len(wordList) - 1 and posList[n + 1] == 'prep':
                     utterance[ noun_followed_by_preposition ] = True

               # if current word is a verb
               elif pos in verbTags:        
                  utterance[ verb_list ].append(word)
                  if word in emotionVerbs:
                     utterance[ emotion_verb_list ].append(word)

               # if there's an apostrophe inside a word, like in "that's mine" or
               # "Clemont's house", the part of speech is "pro;cop" for "that's" and
               # "n;poss" for "Clemont's", which the other 
               elif ";" in pos:
                  if pos[pos.index(";") + 1:] in verbTags:
                     if ";" in word: # why do we need this if-statement? Some words like "growned" are "v;v" but the mw_stem doesn't contain semicolons
                        word = word[word.index(';') + 1:]
                        # only the part after the apostrophe is the verb (which includes more than
                        # just copula, because some verbs like "write" are "write;write" in mw_stem)
                     utterance[ verb_list ].append(word)
                     if word in emotionVerbs:
                        utterance[ emotion_verb_list ].append(word)
                        
                  if pos[:pos.index(";")] == "n":
                     if ";" in word:
                        word = word[0 : word.index(";")] # only the part before the apostrophe is the noun
                     if word in emotionNouns :
                        utterance[ emotion_noun_list ].append(word)
                     if n < len(wordList) - 1 and posList[n + 1] == 'prep':
                        utterance[ noun_followed_by_preposition ] = True

               elif pos == "adv":
                  # Even though the above if-statement covers adverbs, we check whether the word 
                  # below is in emotionAdjs. This is because we defined each word from mw_stem,
                  # the list of words after stemming. So for example, instances of "usually" shows
                  # up as "usual" after stemming, but it still has the part-of-speech tag of "adv"
                  if word in emotionAdjs:
                     utterance[ emotion_adv_list ].append(word)

               # if current word is a preposition
               elif pos == "prep":
                  utterance[ has_preposition ] = True
   
   
            CorporaRows.append(utterance)


###########################################################

# Examples of what we can do: 

print("\nfirst 13 utterances to have emotion adjectives: \n")
count = 0
for utterance in CorporaRows:
   if len(utterance[ emotion_adj_list ]) > 0: # if list of emotion adjectives is non-empty
      print(utterance["w"])
      print(concurrence_EmotionAdjVerb(utterance))
      count += 1
   
   if count == 100:
      break   


print("\nfirst 13 utterances to have emotion nouns: \n")
count = 0
for utterance in CorporaRows:
   if len(utterance[ emotion_noun_list ]) > 0: # if list of emotion adjectives is non-empty
      print(utterance["w"] + "  " + utterance["pos_c"])
      count += 1
   if count == 13:
      break


print("\nfirst 13 utterances with \"feel\", \"felt\", etc. and an emotion adjective somewhere: \n")
count = 0
for utterance in CorporaRows:
   if "feel" in utterance[ verb_list ] and len(utterance[ emotion_adj_list ]) > 0:
      print(utterance["w"])
      count += 1
   if count == 13:
      break



# the code below has been made into a "comment" so that I can output other stuff
# without it swamping the output with more lines of output
"""
print("\nReliability cues for emotion adjectives\n")

emotionAdjVerbDist = nltk.probability.ConditionalFreqDist(
    condition for utterance in CorporaRows for condition in concurrence_EmotionAdjVerb(utterance)
)

adjVReliabilityCues = []

print("Adjective   Verb    Occurrences\n-------------------------------")
for cond1 in emotionAdjVerbDist.conditions():
   for cond2 in emotionAdjVerbDist[cond1]:
      occurrences = emotionAdjVerbDist[cond1][cond2]
      adjVReliabilityCues.append(("{0:<11} {1:<10}".format(str(cond1), str(cond2)), occurrences))
      # this last bit is only for formatting; if we wanted to just output to CSV, we'd just concatenate cond1,cond2,occurences

adjVReliabilityCues.sort(key = lambda x: x[1],reverse=True)

# print the reliability cues sorted in order of most to least frequent
for k in adjVReliabilityCues:
   print(k[0] + " {0:>8}".format(k[1]))

# do it again, but swapping verbs and adjectives
vAdjReliabilityCues = []

print("Verb    Adjective   Occurrences\n-------------------------------")
verbEmotionAdjDist = nltk.probability.ConditionalFreqDist(
    (condition[1],condition[0]) for utterance in CorporaRows for condition in concurrence_EmotionAdjVerb(utterance)
)

for cond1 in verbEmotionAdjDist.conditions():
   for cond2 in verbEmotionAdjDist[cond1]:
      occurrences = verbEmotionAdjDist[cond1][cond2]
      vAdjReliabilityCues.append(("{0:<11} {1:<10}".format(str(cond1), str(cond2)), occurrences))
vAdjReliabilityCues.sort(key = lambda x: x[1],reverse=True)
for k in vAdjReliabilityCues:
   print(k[0] + " {0:>7}".format(k[1]))


print("\nhow do children change in the frequency of negated emotion words as they age?\n")
# note that "unhappy" is not treated any differently from other emotion adjectives, and is NOT
# counted as a negated emotion adjective according to this

# conditional frequency distribution of age versus presence of any emotion adjective
emotionAdjAgeDist = nltk.probability.ConditionalFreqDist(
                  (utterance['Y'], len(utterance[ emotion_adj_list ]) > 0)
                  for utterance in CorporaRows if utterance['who'] == 'CHI'
                 )
# conditional frequency distribution of age versus presence of negated emotion adjective
negations = nltk.probability.ConditionalFreqDist(
            (utterance['Y'], utterance[ negated_emotion_adj ])
             for utterance in CorporaRows if utterance['who'] == 'CHI'
            )

print("Age   Negated emotion adj     All emotion adjs    All utterances") # these counts are for all five corpora
for c in negations.conditions():
   print(" " + str(c) + "            " + " " * int(negations[c][True] < 10) + str(negations[c][True]) + "                    " + 
         str(emotionAdjAgeDist[c][True]) + "              " +
         " " * (3-len(str(emotionAdjAgeDist[c][True]))) + str(negations[c][False]))
"""



print("\nReliability cues for emotion nouns (preliminary)\n")

emotionNounVerbDist = nltk.probability.ConditionalFreqDist(
    condition for utterance in CorporaRows for condition in concurrence_EmotionNounVerb(utterance)
)

nounVerbReliabilityCues = []

print("  Noun      Verb    Occurrences\n-------------------------------")
for cond1 in emotionNounVerbDist.conditions():
   for cond2 in emotionNounVerbDist[cond1]:
      occurrences = emotionNounVerbDist[cond1][cond2]
      nounVerbReliabilityCues.append(("{0:<11} {1:<10}".format(str(cond1), str(cond2)), occurrences))
      # this last bit is only for formatting; if we wanted to just output to CSV, we'd just concatenate cond1,cond2,occurences

nounVerbReliabilityCues.sort(key = lambda x: x[1],reverse=True)

# print the reliability cues sorted in order of most to least frequent
for k in nounVerbReliabilityCues:
   print(k[0] + " {0:>8}".format(k[1]))

# do it again, but swapping verbs and nouns
vNounReliabilityCues = []

print("Verb      Noun      Occurrences\n-------------------------------")
verbEmotionNounDist = nltk.probability.ConditionalFreqDist(
    (condition[1],condition[0]) for utterance in CorporaRows for condition in concurrence_EmotionNounVerb(utterance)
)

for cond1 in verbEmotionNounDist.conditions():
   for cond2 in verbEmotionNounDist[cond1]:
      occurrences = verbEmotionNounDist[cond1][cond2]
      vNounReliabilityCues.append(("{0:<11} {1:<10}".format(str(cond1), str(cond2)), occurrences))
vNounReliabilityCues.sort(key = lambda x: x[1],reverse=True)
for k in vNounReliabilityCues:
   print(k[0] + " {0:>7}".format(k[1]))
























#for utterance in CorporaRows:
#   if utterance['corpus'] == 'Sarah' and len(utterance[ adj_environment_list ]) > 0:
#      if utterance[ adj_environment_list ][0][1][1] == "prep":
#         print(utterance['rownum'] + "," + utterance[ adj_environment_list ][0][0][0] + ","
#               + utterance[ adj_environment_list ][0][1][0] + "," + utterance['w'] + ",preposition" +
#               ",emotion adj" * int(len(utterance["emotion_adj_list"]) > 0))
#      if utterance[ adj_environment_list ][0][1] == ("that",'pro'):
#         print(utterance['rownum'] + "," + utterance[ adj_environment_list ][0][0][0] + ","
#               + utterance[ adj_environment_list ][0][1][0] + "," + utterance['w'] + ",that"
#               + ",emotion adj" * int(len(utterance["emotion_adj_list"]) > 0))






   
   
   #for utterance in CorporaRows:
   #   if utterance[ negated_emotion_adj ] == True:
   #      print(utterance['w'])