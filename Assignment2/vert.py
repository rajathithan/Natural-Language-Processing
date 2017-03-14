def viterbi(brown, taglist, knownwords, qvalues, evalues):
    tagged = []
    for sentWords_raw in brown:
	sentWords_raw = ["*", "*"] + sentWords_raw + ["STOP"]
	sentWords = sentWords_raw[:]
	for i, w in enumerate(sentWords):
            if(not(w in knownwords)):
                sentWords[i] = "_RARE_"
        taggedWords = viterbilet(sentWords, sentWords_raw, taglist, qvalues, evalues)
        tagged.append(" ".join(taggedWords[2:-1]))#ignore the * * and STOP
        #print tagged
    return tagged

#viterbilet is a unit for processing a sentence by viterbi algorithm.
#sentWords is a list of words of 1 sentence, with * * and STOP, and with RARE replaced.
#sentWords_raw is same list of words of the sentence,but preserve the original words instead of RARE tag.
def viterbilet(sentWords, sentWords_raw, taglist, qvalues, evalues):
    print "TAGLIST:", taglist
    taggedWords = []
    m = len(taglist) # number of tags
    n = len(sentWords) # number of words
    #3D array with dimension m*n*m
    #A is the DP array storing the best trigram prob.
    #A[j][i][k] represents:
    #for the i-th word, if the tag is tag[j], and previous word is tag[k], 
    #then the best prob now for [anyBestTags],word[i-1]/tag[k],word[i]/tag[j] is A[j][i][k]
    #and D[j][i][k] indicates the best tag for word[i-2], the tag 2 behind i-th word
    A = [[[0]*m for ii in range(0,n)] for jj in range(0,m)]
    D = [[[0]*m for ii in range(0,n)] for jj in range(0,m)]
    for i, word in enumerate(sentWords):# each word
        if(i < 2):
            for j in range(0,m):
                for k in range(0,m):
                    A[j][i][k] = 0
            continue
        for j in range(0,m):# index of current tag for this word
            tag = taglist[j]# current tag
            for k in range(0,m):# index of tag 1 behind
                maxi = -100000000000000 #init with some very small number
                maxtag = 0
                for kk in range(0,m):# index of tag 2 behind
                    tri_tuple = tuple([taglist[kk], taglist[k], taglist[j]])
                    if(i==2):
                        tri_tuple = tuple(["*", "*", taglist[j]])
                    elif(i==3):
                        tri_tuple = tuple(["*", taglist[k], taglist[j]])

                    cur = A[k][i-1][kk] + qvalues.get(tri_tuple, -1000) + evalues.get(tuple([word, tag]), -1000)
                    #print qvalues.get(tri_tuple, -1000), evalues.get(tuple([word, tag]), -1000)
                    if(cur > maxi):
                        maxi = cur
                        maxtag = kk
                A[j][i][k] = maxi
                D[j][i][k] = maxtag

    curmax = -100000000000000
    curmaxI = 0
    prevI = 0
    # for the last word, find the best 1 behind tag, and best 2 behind tag
    for j in range(0,m):
        for k in range(0,m):
            tri_tuple = tuple([taglist[k], taglist[j], "STOP"])
            if(A[j][n-2][k]+qvalues.get(tri_tuple, -1000) > curmax):
		curmax = A[j][n-2][k]+qvalues.get(tri_tuple, -1000)
                curmaxI = j
                prevI = k
    print D
    input('pause')
    revTagList = ["STOP", taglist[curmaxI], taglist[prevI]]
    #for each loop, using curmaxI and prevI, we could find the previous 1 best tag.
    for i in range(n-2,3,-1):
        tmp = D[curmaxI][i][prevI]
        #print "curmaxI:", curmaxI, " i:", i, " prevI:", prevI
        #print "D = ", tmp
        curmaxI = prevI
        prevI = tmp
        revTagList.append(taglist[tmp])

    #at beginning, there are 2 *
    revTagList.append("*")
    revTagList.append("*")
    revTagList.reverse()

    #form the tagwords
    #print revTagList
    for i, word in enumerate(sentWords_raw):
        taggedWords.append(word+"/"+revTagList[i])
    del A
    del D
    return taggedWords



