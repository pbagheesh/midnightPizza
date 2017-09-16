import sys
import data
import datetime
import classifiers
import numpy as np

def buildClassifier(trainFile,testFile,tCats = None, ttCats = None, classType = "NaiveBayes", save=False, K=None):
    '''
        Code inspired by Bruce's code
    '''
    dtrain = data.Data(trainFile)
    dtest = data.Data(testFile)

    if (tCats != None and ttCats != None):
        traincatdata = data.Data(tCats)
        traincats = traincatdata.get_data( [traincatdata.get_headers()[0]], traincatdata.get_num_rows())
        testcatdata = data.Data(ttCats)
        testcats = testcatdata.get_data([testcatdata.get_headers()[0]], testcatdata.get_num_rows())
        A = dtrain.get_data( dtrain.get_headers(), dtrain.get_num_rows())
        B = dtest.get_data( dtest.get_headers(), dtest.get_num_rows())
    else:
        # assume the categories are the last column
        traincats = dtrain.get_data( [dtrain.get_headers()[-1]], dtrain.get_num_rows())
        testcats = dtest.get_data( [dtest.get_headers()[-1]], dtest.get_num_rows())
        A = dtrain.get_data( dtrain.get_headers()[:-1], dtrain.get_num_rows())
        B = dtest.get_data( dtest.get_headers()[:-1], dtest.get_num_rows())

    #default is a naiveBayes Classifier
    nbc = classifiers.NaiveBayes()
    if(classType == "KNN"):
        if K != None:
            nbc = classifiers.KNN(K=K)
            nbc.build( A, traincats)
            ctraincats, ctrainlabels = nbc.classify( A )
            ctestcats, ctestlabels = nbc.classify( B )
        else:
            #default K of 3
            nbc = classifiers.KNN(K=3)
            nbc.build( A, traincats )
            ctraincats, ctrainlabels = nbc.classify( A )
            ctestcats, ctestlabels = nbc.classify( B )
    else:
        # build the classifier using the training data
        nbc.build( A, traincats )

        # use the classifier on the training data
        ctraincats, ctrainlabels = nbc.classify( A )
        ctestcats, ctestlabels = nbc.classify( B )

    if save == True:
        ctestcats.tofile('cTestCats.csv',sep=" ",format="%s")
        ctestlabels.tofile('cTestLabels.csv',sep=" ",format="%s")

    print "Training Data"
    print nbc.confusion_matrix_str( nbc.confusion_matrix(traincats, ctraincats))
    print "Test Data"
    print nbc.confusion_matrix_str( nbc.confusion_matrix(testcats, ctestcats) )

    return nbc

def main(argv):
    start = datetime.datetime.now()
    print "Start Time:", start
    if (len(argv) == 5):
        #Assumes you give command line input as test data, train data, test cols, train cols
        buildClassifier(argv[1],argv[2], argv[3], argv[4])
    elif (len(argv) == 3):
        buildClassifier(argv[1],argv[2], classType = "KNN", K=3)
    end = datetime.datetime.now()


    print "End time: ", end
    print " Time Taken: ", end - start

if __name__ == "__main__":
    main(sys.argv)
