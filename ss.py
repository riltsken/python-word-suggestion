#!/usr/bin/env python
import sys
import numpy
from datetime import datetime

VOWELS = ['a','e','i','o','u']

class timer():
	def __enter__(self):
		self.start = datetime.now()
	def __exit__(self, *args):
		delta = datetime.now() - self.start
		print "Search took: %s.%ss" % (delta.seconds, delta.microseconds)

# Using the Jaro-Winkler Distance algorithm as a base template
def find_distance(first,second,standard_weight=0.1,vowel_match_boost=0.35):
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
	matches = 0
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
	"""
	mismatched_count = 0
	mismatched = map(lambda x,y: (x,y), long_word, short_word)
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
		# I felt mismatch should increase and not decrease a score so mine is modified
		jaro_score = .333 * (float(matches)/long_length + float(matches)/short_length + 
			float(mismatched_count)/long_length - length_penalty)
	
		# vowel boost rocks a pretty sweet percent increase	
		if vowel_boost:
			jaro_score = jaro_score + vowel_match_boost

		# here we update the jaro score to take into account a common prefix
		jarowinkler_score = jaro_score + (common_prefix_count * standard_weight * (1 - jaro_score))
	
	return jarowinkler_score

def main():
	piped_words = None
	if not sys.stdin.isatty():
		piped_words = iter(sys.stdin.readlines())

	while 1:
		if piped_words:
			try:
				given_word = piped_words.next()
				print "> %s" % given_word.replace('\n', '')
			except StopIteration:
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
			match = ('NO SUGGESTION',0.50)
			for word in open("/usr/share/dict/words"):
				w = word.replace('\n', '')
				if w:
					if given_word == w:
						match = (w,1)
						top3.append(match)
						break
		
					distance = find_distance(given_word,w)

					if match[1] < distance:
						match = (w,distance)

					if len(top3) < 3:
						top3.append((w,distance))
					else:
						for x in xrange(0,len(top3)):
							if distance > top3[x][1]:
								top3.insert(x, (w,distance))
								top3.pop(x+1)
								break
		
		top3.sort(key=lambda x: x[1],reverse=True)
		#print match[0]
		for t in top3:
			print t[0],t[1]

if __name__ == "__main__":
		sys.exit(main())
