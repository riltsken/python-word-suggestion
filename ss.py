#!/usr/bin/env python
import sys
import numpy
from datetime import datetime

VOWELS = ['a','e','i','o','u']
MATCH_THRESHOLD = 0.50
LO_BOOST = .05
MID_BOOST = .075
HI_BOOST = .1

class timer():
	def __enter__(self):
		self.start = datetime.now()
	def __exit__(self, *args):
		delta = datetime.now() - self.start
		print "Search took: %s.%ss" % (delta.seconds, delta.microseconds)

# Using the Jaro-Winkler Distance algorithm as a base template
def find_distance(first,second,standard_weight=0.1,special_match_boost=0.35):
	len1 = len(first)
	len2 = len(second)
	
	long_word = first 
	long_length = len1
	short_word = second
	short_length = len2
	if len2 > len1:
		long_word = second
		long_length = len2
		short_word = first
		short_length = len1
	
	"""
	This compares the current char from the longer string up to 
	+-match_distance amount of indices in the shorter string to 
	see if it shows up, if it does, add to the matched count
	"""
	matches = 0.0
	# modified from the formula, orginally (l_length / 2) - 1. I found this favored long words too much.
	match_distance = long_length / 2 
	for x, ch_f in enumerate(long_word):
		if x < match_distance: # can't use negative indices so catch that here
			allowed_chars = short_word[0:x + match_distance]
		else:	
			allowed_chars = short_word[x - match_distance:x + match_distance]
		
		if ch_f in allowed_chars:
			matches += 1

	"""
	All this does is check against each vowel in the string provided by the user
	it will then replace that vowel and compare the word to see if it matches up
	if it does, we add a fairly strong boost to that vowel'ed word as per
	the project constraints
	"""
	vowel_boost = False
	for x,ch in enumerate(first):
		if ch in VOWELS:
			for v in VOWELS:
				new_string = list(first)
				new_string.insert(x,v)
				new_string.pop(x+1)
				if ''.join(new_string) == second:
					vowel_boost = True
	
	"""
	Part of the jaro winkler algorithm is that mismatched pairs
	hold a weight as well. For example, hlep -> help where
	le and el are a mismatched pair. We count these for use later.

	Also disregard a one letter word when it comes to mismatches
	"""
	mismatched_count = 0
	mismatched = zip(long_word, short_word)
	for x in xrange(0,long_length):
		try:
			if mismatched[x] == (mismatched[x+1][1],mismatched[x+1][0]):
				mismatched_count += 1
		except IndexError:
			pass

	"""
	Another measurement of jaro winkler is if the words have a common prefix
	we count up to a maximum of 4 for the prefix to be added to the weight 
	formula
	"""
	common_prefix_count = 0
	while common_prefix_count < short_length and common_prefix_count <= 4:
		if not long_word[common_prefix_count] == short_word[common_prefix_count]:
			break
			
		common_prefix_count += 1

	"""
	We are finally going to compute the score here! I have modified the original formula
	to take into account special cases provided
	"""
	jarowinkler_score = 0
	if matches:
		# I noticed that long words were given precedence since they managed to sometimes grab more
		# matches based on the distance... I wanted to give a penalty if our
		# given word has a length difference, the larger the difference the bigger the penalty
		length_penalty = (long_length - short_length) / float(long_length)

		# original formula: 1/3 (m / len1 + m / len2 + (m - mismatch / m))
		jaro_score = .333 * (matches / long_length + matches / short_length + 
			mismatched_count / long_length - length_penalty)

		# here we update the jaro score to take into account a common prefix
		jarowinkler_score = jaro_score + (common_prefix_count * standard_weight * (1 - jaro_score))

		# If the first and last letter match we should boost that word match if it has a good score already
		if first[0] == second[0] and first[-1] == second[-1] and jarowinkler_score > MATCH_THRESHOLD:
			jarowinkler_score = jarowinkler_score + LO_BOOST

		if vowel_boost:
			jarowinkler_score = jaro_score + special_match_boost
		
	return jarowinkler_score

def main():
	piped_words = None
	if not sys.stdin.isatty():
		piped_words = iter(sys.stdin.readlines())

	while 1:
		if piped_words:
			try:
				given_word = piped_words.next().lower().replace('\n', '')
				print "> %s" % given_word
			except StopIteration: # break out of infinite loop to end script if we are given input
				break
		else:
			given_word = raw_input("> ").lower()

		"""
		Just go through each word from the dictionary through iteration
		and pass it to the distance calculator. It goes from 0 to 1 with
		0 being lowest and 1 being highest.
		"""
		with timer():
			top3 = []
			same_word = False
			match = ('NO SUGGESTION',MATCH_THRESHOLD)
			for word in open("/usr/share/dict/words"):
				w = word.replace('\n', '') # 'the /usr/share/dict/words has a \n we dont want'
				if w:
					if given_word == w: # if we found an exact match, use it
						match = (w,1)
						break
					
					# it is unlikely someone will write a word with both
					# the last and first letters incorrect, speeds up algo 
					# by a very large amount
					first_and_last_check = given_word[0] == w[0] or given_word[-1] == w[-1]

					# if an apostrophe doesn't show up in the given word
					# don't use it to check against in the dictionary
					apostrophe_check = '\'' not in given_word and '\'' in w

					one_letter_check = len(w) == 1 and len(given_word) > 1

					if first_and_last_check and not apostrophe_check and not one_letter_check:
						distance = find_distance(given_word,w)

						if match[1] < distance:
							match = (w,distance)

		print match[0]

if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		print # push the prompt down a line when ctrl+c
		sys.exit(1)

