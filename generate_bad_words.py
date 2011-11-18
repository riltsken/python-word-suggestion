#!/usr/bin/env python
import random
import re

VOWELS = ['a','e','i','o','u']
ALPHABET = re.compile('[\w]') 

def replace_character(word,char,index):
	word = list(word)
	word.insert(index, char)
	word.pop(index + 1)
	return ''.join(word)

def duplicate_char(word):
	index = random.randint(0,len(word) - 1)
	if ALPHABET.match(word[index]):
		word = list(word)
		word.insert(index, word[index])
		return ''.join(word)
	return word

def capitalize_char(word):
	index = random.randint(0,len(word) - 1)
	if ALPHABET.match(word[index]):
		upper = word[index].upper()
		return replace_character(word,upper,index)
	return word

def modify_vowel(word):
	index = random.randint(0,len(word) - 1)
	if ALPHABET.match(word[index]):
		vowel = VOWELS[random.randint(0,len(VOWELS) - 1)]
		return replace_character(word,vowel,index)
	return word

sample = random.sample(xrange(98000),15)
words = []
mutators = [duplicate_char, capitalize_char, modify_vowel]
for x,word in enumerate(open('/usr/share/dict/words')):
	if x in sample and word and word != '\n':
		for m in xrange(random.randint(1,3)):
			word = mutators[random.randint(0,2)](word)
		words.append(word)

print ''.join(words)