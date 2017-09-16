# Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Naive Bayes class test
#

import sys
import data
import classifiers

def main(argv):

    if len(argv) < 3:
        print 'Usage: python %s <train data file> <test data file> <optional train categories> <optional test categories>' % (argv[0])
        exit(-1)

    dtrain = data.Data(argv[1])
    dtest = data.Data(argv[2])

    if len(argv) > 3:
        traincatdata = data.Data(argv[3])
        traincats = traincatdata.get_data( [traincatdata.get_headers()[0]], traincatdata.get_num_rows())
        testcatdata = data.Data(argv[4])
        testcats = testcatdata.get_data( [testcatdata.get_headers()[0]], testcatdata.get_num_rows())
        A = dtrain.get_data( dtrain.get_headers(), dtrain.get_num_rows())
        B = dtest.get_data( dtest.get_headers(), dtest.get_num_rows())

    else:
        # assume the categories are the last column
        traincats = dtrain.get_data( [dtrain.get_headers()[-1]], dtrain.get_num_rows())
        testcats = dtest.get_data( [dtest.get_headers()[-1]], dtest.get_num_rows())
        A = dtrain.get_data( dtrain.get_headers()[:-1], dtrain.get_num_rows())
        B = dtest.get_data( dtest.get_headers()[:-1], dtest.get_num_rows())

    # create a new classifier
    nbc = classifiers.NaiveBayes()

    # build the classifier using the training data
    nbc.build( A, traincats )

    # use the classifier on the training data
    ctraincats, ctrainlabels = nbc.classify( A )
    ctestcats, ctestlabels = nbc.classify( B )


    print "Confusion Matrix"

    print nbc.confusion_matrix_str( nbc.confusion_matrix(traincats, ctraincats))

    print 'Results on Training Set:'
    print '     True  Est'
    for i in range(ctraincats.shape[0]):
        if int(traincats[i,0]) == int(ctraincats[i,0]):
            print "%03d: %4d %4d" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )
        else:
            print "%03d: %4d %4d **" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )

    print 'Results on Test Set:'
    print '     True  Est'
    for i in range(ctestcats.shape[0]):
        if int(testcats[i,0]) == int(ctestcats[i,0]):
            print "%03d: %4d %4d" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )
        else:
            print "%03d: %4d %4d **" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )
    return

if __name__ == "__main__":
    main(sys.argv)
