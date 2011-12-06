#!/usr/bin/env python
import sys
import itertools
from datetime import datetime

VOWELS = set(['a','e','i','o','u'])
FAIL = 'NO SUGGESTION'

class timer():
	def __enter__(self):
		self.start = datetime.now()
	def __exit__(self, *args):
		delta = datetime.now() - self.start
		print "Search took: %s.%ss" % (delta.seconds, delta.microseconds)


""" a generator for finding same character dupes in a word """
def get_dupe(word,min_dupes=1):
	for x, ch in enumerate(word):
		offset = 1
		while (x + offset) < len(word) and word[x] == word[x + offset]:
			offset += 1
		
		if offset > min_dupes:
			yield (x,x + offset)

def clean_duplicate_chars(word):
	matches = []

	""" First check duplicates from the start of the string """
	dupes = 0
	while dupes < len(word) and word[0] == word[dupes + 1]:
		dupes += 1

	word = word[dupes:] # take the last dupe and on

	""" Find and replace all 3+ character dupes down to two """
	try:
		dupe = get_dupe(word,min_dupes=2).next()
		while dupe:
			# + 2 for 2 dupes
			word = ''.join([word[:dupe[0] + 2], word[dupe[1]:]])
			# have to reset the generator since we create a new word
			dupe = get_dupe(word,min_dupes=2).next()
	except StopIteration:
		""" 
		Take these 2-letter dupes and create a product on 1-2 letter differences
		from these dupes creating a large pool of matches
		"""
		matches.append(word)
		dupes = []
		for dupe in get_dupe(word,min_dupes=1):
			if dupe:
				dupes.append(dupe)

		for dupe_arrangement in itertools.product(range(2),repeat=len(dupes)):
			w = list(word)
			offset = 0
			for x, dupe_count in enumerate(dupe_arrangement):
				index = dupes[x][0] - offset
				if dupe_count == 1:
					offset += 1
					w.pop(index)
			
			matches.append(''.join(w))

		return matches

def vowel_product(matches):

	""" 
	find the product of all all vowels based on
	the amount of vowels in the word.
	
	So if we had the word shheepp we have a length of two vowels
	generating a product of.  
	[
		'aa','ai','ae','au','ao',
		'ia','ii','ie','iu','io'
		....	
	]

	Maybe this should be pre-calculated	so that boot up takes a 
	little bit longer but we no longer have	to generate per word check?
	"""
	new_matches = []
	for word in matches:
		vowel_index = []
		for x, ch in enumerate(word):
			if ch in VOWELS:
				vowel_index.append(x)

		for product in itertools.product(VOWELS,repeat=len(vowel_index)):
			w = list(word)
			for x, ch in enumerate(product):
				w[vowel_index[x]] = ch
			
			new_matches.append(''.join(w))

	return new_matches
	
def main():
	piped_words = None
	if not sys.stdin.isatty():
		piped_words = iter(sys.stdin.readlines())

	while 1:
		# Our initial word will be lowercased after we grab them from the user or pipe
		if piped_words:
			try:
				given_word = piped_words.next().replace('\n', '')
				print "> %s" % given_word
				given_word = given_word.lower()
			except StopIteration: # break out of infinite loop to end script if we are given input
				break
		else:
			given_word = raw_input("> ").lower()

		with timer():

			# Attempt to fix duplicate characters
			dupe_fix_matches = clean_duplicate_chars(given_word)
			length_requirement = set([len(m) for m in dupe_fix_matches])

			match = FAIL 
			for word in open("/usr/share/dict/words"):
				w = word.replace('\n', '') # 'the /usr/share/dict/words has a \n we dont want'
				if w:
					if len(w) in length_requirement: # don't bother checking the strings if they don't match lengths
						for m in dupe_fix_matches:
							if m == w:
								match = w
								break

			if match == FAIL:
				# it is faster to check every word in the dupe list before creating the permutations and then searching through them
				vowel_product_matches = vowel_product(dupe_fix_matches)
				for word in open("/usr/share/dict/words"):
					w = word.replace('\n', '') 
					if w:
						if len(w) in length_requirement: 
							# line up all possible vowel matches
							for m in vowel_product_matches:
								if m == w:
									match = w
									break

		print match

if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		print # push the prompt down a line when ctrl+c
		sys.exit(1)

