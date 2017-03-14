import math
import nltk
import time

# Constants to be used by you when you fill the functions
START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
MINUS_INFINITY_SENTENCE_LOG_PROB = -1000

# TODO: IMPLEMENT THIS FUNCTION
# Calculates unigram, bigram, and trigram probabilities given a training corpus
# training_corpus: is a list of the sentences. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function outputs three python dictionaries, where the keys are tuples expressing the ngram and the value is the log probability of that ngram
def calc_probabilities(training_corpus):
    unigram_p = {}
    bigram_p = {}
    trigram_p = {}
    
    unigram = {}
    bigram = {}
    trigram = {}

    uni_count = 0

    for sentence in training_corpus:
        sentence += STOP_SYMBOL
        tokens = nltk.word_tokenize(sentence)

        # build unigram dictionary
        for word in tokens:
            uni_count += 1
            if word in unigram:
                unigram[word] += 1
            else:
                unigram[word] = 1

        # build bigram dictionary, it should add a '*' to the beginning of the sentence first
        tokens = [START_SYMBOL] + tokens
        bigram_tuples = tuple(nltk.bigrams(tokens))

        for item in bigram_tuples:
            if item in bigram:
                bigram[item] += 1
            else:
                bigram[item] = 1

        # build trigram dictionary, it should add another '*' to the beginning of the sentence
        tokens = [START_SYMBOL] + tokens
        trigram_tuples = tuple(nltk.trigrams(tokens))

        for item in trigram_tuples:
            if item in trigram:
                trigram[item] += 1
            else:
                trigram[item] = 1

    # calculate unigram probability
    for word in unigram:
        temp = [word]
        unigram_p[tuple(temp)] = math.log(float(unigram[word])/uni_count, 2)

    # calculate bigram probability
    for word in bigram:
        if word[0] == START_SYMBOL:
            bigram_p[tuple(word)] = math.log(float(bigram[word])/unigram[STOP_SYMBOL], 2)
        else:
            bigram_p[tuple(word)] = math.log(float(bigram[word])/unigram[word[0]], 2)

    # calculate trigram probability
    for word in trigram:
        if word[0] == START_SYMBOL and word[1] == START_SYMBOL:
            trigram_p[tuple(word)] = math.log(float(trigram[word])/unigram[STOP_SYMBOL], 2)
        else:
            trigram_p[tuple(word)] = math.log(float(trigram[word])/bigram[(word[0], word[1])], 2)



    return unigram_p, bigram_p, trigram_p

# Prints the output for q1
# Each input is a python dictionary where keys are a tuple expressing the ngram, and the value is the log probability of that ngram
def q1_output(unigrams, bigrams, trigrams, filename):
    # output probabilities
    outfile = open(filename, 'w')

    unigrams_keys = unigrams.keys()
    unigrams_keys.sort()
    for unigram in unigrams_keys:
        outfile.write('UNIGRAM ' + unigram[0] + ' ' + str(unigrams[unigram]) + '\n')

    bigrams_keys = bigrams.keys()
    bigrams_keys.sort()
    for bigram in bigrams_keys:
        outfile.write('BIGRAM ' + bigram[0] + ' ' + bigram[1]  + ' ' + str(bigrams[bigram]) + '\n')

    trigrams_keys = trigrams.keys()
    trigrams_keys.sort()    
    for trigram in trigrams_keys:
        outfile.write('TRIGRAM ' + trigram[0] + ' ' + trigram[1] + ' ' + trigram[2] + ' ' + str(trigrams[trigram]) + '\n')

    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence
# ngram_p: python dictionary of probabilities of uni-, bi- and trigrams.
# n: size of the ngram you want to use to compute probabilities
# corpus: list of sentences to score. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function must return a python list of scores, where the first element is the score of the first sentence, etc. 
def score(ngram_p, n, corpus):
    scores = []

    for sentence in corpus:
        total_score = 0
        #calculate unigram
        if n == 1:
            sentence += STOP_SYMBOL
            tokens = nltk.word_tokenize(sentence)
            for word in tokens:
                #print ngram_p[tuple([word])]
                if tuple([word]) in ngram_p:
                    total_score += ngram_p[tuple([word])]
            scores.append(total_score)
        
        #calculate bigram
        if n == 2:
            sentence = START_SYMBOL + sentence + STOP_SYMBOL
            tokens = nltk.word_tokenize(sentence)
            for word1,word2 in zip(tokens[0::1], tokens[1::1]):
                #print ngram_p[(word1, word2)]
                if (word1, word2) in ngram_p:
                    total_score += ngram_p[(word1, word2)]
            scores.append(total_score)

        #calculate trigram
        if n == 3:
            sentence = START_SYMBOL + START_SYMBOL + sentence + STOP_SYMBOL
            tokens = nltk.word_tokenize(sentence)
            for word1,word2,word3 in zip(tokens[0::1], tokens[1::1], tokens[2::1]):
                #print ngram_p[(word1, word2, word3)]
                if (word1, word2, word3) in ngram_p:
                    total_score += ngram_p[(word1, word2, word3)]
            scores.append(total_score)

    return scores

# Outputs a score to a file
# scores: list of scores
# filename: is the output file name
def score_output(scores, filename):
    outfile = open(filename, 'w')
    for score in scores:
        outfile.write(str(score) + '\n')
    outfile.close()

# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence with a linearly interpolated model
# Each ngram argument is a python dictionary where the keys are tuples that express an ngram and the value is the log probability of that ngram
# Like score(), this function returns a python list of scores
def linearscore(unigrams, bigrams, trigrams, corpus):
    scores = []

    for sentence in corpus:
        total_score = 0
        mark = 0

        sentence = START_SYMBOL + START_SYMBOL + sentence + STOP_SYMBOL
        tokens = nltk.word_tokenize(sentence)

        # for all the (word1, word2, word3) tuple in sentence, calculate probabilities
        for word1, word2, word3 in zip(tokens[0::1], tokens[1::1], tokens[2::1]):
            word_score = 0

            # the first tuple is ('*', '*', WORD), so we begin unigram with word3
            uni_score = 0
            if tuple([word3]) in unigrams:
                uni_score = 2**unigrams[tuple([word3])]

            bi_score = 0
            if (word2, word3) in bigrams:
                bi_score = 2**bigrams[(word2, word3)]

            tri_score = 0
            if (word1, word2, word3) in trigrams:
                tri_score = 2**trigrams[(word1, word2, word3)]

            # if all the unigram, bigram, trigram scores are 0 then the sentence's probability should be -1000
            if uni_score != 0 or bi_score != 0 or tri_score != 0:
                word_score = math.log((uni_score + bi_score + tri_score), 2) + math.log(1, 2) - math.log(3, 2)
                total_score += word_score
            else:
                mark = 1

        if mark == 1:
            total_score = MINUS_INFINITY_SENTENCE_LOG_PROB

        scores.append(total_score)

    return scores

DATA_PATH = 'data/'
OUTPUT_PATH = 'output/'

# DO NOT MODIFY THE MAIN FUNCTION
def main():
    # start timer
    time.clock()

    # get data
    infile = open(DATA_PATH + 'Brown_train.txt', 'r')
    corpus = infile.readlines()
    infile.close()

    # calculate ngram probabilities (question 1)
    unigrams, bigrams, trigrams = calc_probabilities(corpus)

    # question 1 output
    q1_output(unigrams, bigrams, trigrams, OUTPUT_PATH + 'A1.txt')

    # score sentences (question 2)
    uniscores = score(unigrams, 1, corpus)
    biscores = score(bigrams, 2, corpus)
    triscores = score(trigrams, 3, corpus)

    # question 2 output
    score_output(uniscores, OUTPUT_PATH + 'A2.uni.txt')
    score_output(biscores, OUTPUT_PATH + 'A2.bi.txt')
    score_output(triscores, OUTPUT_PATH + 'A2.tri.txt')

    # linear interpolation (question 3)
    linearscores = linearscore(unigrams, bigrams, trigrams, corpus)

    # question 3 output
    score_output(linearscores, OUTPUT_PATH + 'A3.txt')

    # open Sample1 and Sample2 (question 5)
    infile = open(DATA_PATH + 'Sample1.txt', 'r')
    sample1 = infile.readlines()
    infile.close()
    infile = open(DATA_PATH + 'Sample2.txt', 'r')
    sample2 = infile.readlines()
    infile.close() 

    # score the samples
    sample1scores = linearscore(unigrams, bigrams, trigrams, sample1)
    sample2scores = linearscore(unigrams, bigrams, trigrams, sample2)

    # question 5 output
    score_output(sample1scores, OUTPUT_PATH + 'Sample1_scored.txt')
    score_output(sample2scores, OUTPUT_PATH + 'Sample2_scored.txt')

    # print total time to run Part A
    print "Part A time: " + str(time.clock()) + ' sec'

if __name__ == "__main__": main()
