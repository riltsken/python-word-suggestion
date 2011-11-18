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
	we are comparing the current char from the longer string to 
	+-3 indices in the shorter string to see if it shows up, if 
	it does, add to the matched count
	"""
	matches = 0
	match_distance = long_length / 2
	for x, ch_f in enumerate(long_word):
		if x < match_distance:
			allowed_chars = short_word[0:x + match_distance]
		else:	
			allowed_chars = short_word[x - match_distance:x + match_distance]
		
		if ch_f in allowed_chars:
			matches += 1

	vowel_boost = False
	for x,ch in enumerate(first):
		if ch in VOWELS:
			for v in VOWELS:
				new_string = list(first)
				new_string.insert(x,v)
				new_string.pop(x+1)
				if ''.join(new_string) == second:
					vowel_boost = True
	
	mismatched_count = 0
	mismatched = map(lambda x,y: (x,y), long_word, short_word)
	for x in xrange(0,long_length):
		try:
			if mismatched[x] == (mismatched[x+1][1],mismatched[x+1][0]):
				mismatched_count += 1
		except IndexError:
			pass

	common_prefix_count = 0
	while common_prefix_count < short_length and common_prefix_count <= 4:
		if not long_word[common_prefix_count] == short_word[common_prefix_count]:
			break
			
		common_prefix_count += 1

	jarowinkler_score = 0
	if matches:
		length_penalty = (long_length - short_length) / float(long_length) 

		# formula: 1/3 (m / len1 + m / len2 + (m - mismatch / m))
		# I felt mismatch should increase and not decrease a score so mine is modified
		jaro_score = .333 * (float(matches)/long_length + float(matches)/short_length + 
			float(mismatched_count)/long_length - length_penalty)
		
		if vowel_boost:
			jaro_score = jaro_score + vowel_match_boost

		# here we update the jaro score to take into account a common prefix
		jarowinkler_score = jaro_score + (common_prefix_count * standard_weight * (1 - jaro_score))
	
	return jarowinkler_score

def main():
	while 1:
		given_word = raw_input("> ").lower()

		with timer():
			top10 = []
			match = ('NO SUGGESTION',0.50)
			for word in open("/usr/share/dict/words"):
				w = word.replace('\n', '')
				if w:
					if given_word == w:
						match = (w,1)
						break
		
					distance = find_distance(given_word,w)

					if match[1] < distance:
						match = (w,distance)
						if len(top10) < 10:
							top10.append((w,distance))
						else:
							for x in xrange(0,len(top10)):
								if distance > top10[x][1]:
									top10.insert(x)
									top10.pop(x+1)
		
		top10.sort(key=lambda x: x[1],reverse=True)
		for t in top10:
			print t[0],t[1]

if __name__ == "__main__":
		sys.exit(main())
