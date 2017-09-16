# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions

import sys
import data
import analysis as an
import numpy as np
import math
import scipy.cluster.vq as vq

class Classifier:

    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        self._type = type
        self.name = ""

    def type(self, newtype = None):
        '''Set or get the type with this function'''
        if newtype != None:
            self._type = newtype
        return self._type

    def confusion_matrix( self, truecats, classcats ):
        '''Takes in two Nx1 matrices of zero-index numeric categories and
        computes the confusion matrix. The rows represent true
        categories, and the columns represent the classifier output.
        '''
        codes,mapping = np.unique(np.array(truecats.T), return_inverse=True)
        codesC,mappingC = np.unique(np.array(classcats.T), return_inverse=True)

        numCats = codes.shape[0]
        numCatsC = codesC.shape[0]

        retMatrix = np.matrix(np.zeros(shape=(numCats, numCats)) )

        for i in range (truecats.shape[0]):
            #Make sure to use mapping because it goes from 0-n-1 vs truecats goes for whatever the cat vals are
            retMatrix[int(mapping[i]), int(classcats[i] )] += 1

        return retMatrix

    def confusion_matrix_str( self, cmtx ):
        # '''Takes in a confusion matrix and returns a string suitable for printing.'''

        s = 'Confusion Matrix\n'
        s += '          '
        for i in range(cmtx.shape[0]):
            s += "Pred " + str(i) + " "

        trueHeaderMatrix = (np.matrix(np.array(["Fooo 2 "] * cmtx.shape[0]))).T

        for i in range (cmtx.shape[0]):
            trueHeaderMatrix[i,0] = "True " + str(i) + " "

        cmtx = np.hstack((trueHeaderMatrix,cmtx))

        s += "\n"
        for i in range(cmtx.shape[0]):
            s += str((cmtx[i,:].tolist()[0])).strip("[]") +"\n"
            s = s.replace(" ' ",'')
            s = s.replace(" , ",'')

        return s

    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self._type)

    def getName(self):
        return self.name

    def updateName(self, name):
        self.name = name

class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.
    '''

    def __init__(self, dataObj=None, headers=[], categories=None):
        '''Takes in a Data object with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        '''Takes in a Data object with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')

        # store the headers used for classification
        self.headers = None

        # number of classes and number of features
        self.num_classes = 0
        self.num_features = 0

        # original class labels
        self.class_labels = None
        self.class_means = None
        self.class_vars = None
        self.class_scales = None

        if (dataObj != None):
            self.build( self.dataObj.get_data(headers, self.dataObj.get_num_rows()) , categories)

    def build( self, A, categories ):
        '''Builds the classifier give the data points in A and the categories'''
        # figure out how many categories there are and get the mapping (np.unique)
        unique, mapping = np.unique( np.array(categories.T), return_inverse=True)

        num_C = len(unique)  #Num of Classes
        num_F = A.shape[1]  #Number of Featuers in data set

        self.num_classes = num_C
        self.num_features = num_F
        self.class_labels = categories

        # create the matrices for the means, vars, and scales
        self.class_means = np.matrix( np.zeros(shape=(num_C,num_F))) #Create C x L Matrix to store
        self.class_vars = np.matrix( np.zeros(shape=(num_C,num_F))) #Create C x L Matrix to store
        self.class_scales = np.matrix( np.zeros(shape=(num_C,num_F))) #Create C x L Matrix to store

        # compute the means/vars/scales for each class
        means = []
        variances = []
        scales = []

        for i in range(len(unique)):
            curVal = A[(mapping==i),:]
            means.append(np.mean( curVal, axis = 0))
            vrnc = (np.var(curVal,axis =0, ddof=1))
            variances.append(vrnc)
            pi2 = np.array([2*math.pi])
            scales.append((1/np.sqrt(pi2*vrnc)))   #Sqrt thing

        self.class_means = means
        self.class_vars = variances
        self.class_scales = scales

        # store any other necessary information: # of classes, # of features, original labels

        return

    def classify( self, A, return_likelihoods=False ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the NxC likelihood matrix.
        '''

        # error check to see if A has the same number of columns as
        # the class means
        if (self.class_means[0].shape[1] != A.shape[1]):
            print "Error cols do not match"
            return

        # make a matrix that is N x C to store the probability of each
        P = np.matrix(np.zeros((A.shape[0], self.num_classes)))

        # calculate the probabilities by looping over the classes
        for i in range(self.num_classes):
            P[:,i] = np.prod(np.multiply(self.class_scales[i], np.exp(-(np.square(A - self.class_means[i]))/(2*self.class_vars[i]))),axis=1)

        # calculate the most likely class for each data point
        cats = np.argmax(P, axis=1)

        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_likelihoods:
            return cats, labels, P

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        print type(self.class_means)
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.class_means[i]) + "\n"
            s += 'Var   : ' + str(self.class_vars[i]) + "\n"
            s += 'Scales: ' + str(self.class_scales[i]) + "\n"

        s += "\n"
        return s

    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return


class KNN(Classifier):

    def __init__(self, dataObj=None, headers=[], categories=None, K=3):
        '''Take in a Data object with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')

        # store the headers used for classification
        self.headers = None

        # number of classes and number of features
        self.num_classes = None
        self.num_features = None

        # original class labels
        self.class_labels = None

        # unique data for the KNN classifier: list of exemplars (matrices)
        self.exemplars = []

        self.kVal = K

        if (dataObj != None and len(headers) != 0):
            self.build(dataObj.get_data(headers, dataObj.get_num_rows()), categories, K=self.kVal )

    def build( self, A, categories, K = None ):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        unique, mapping = np.unique(np.array(categories.T), return_inverse= True)
        self.num_classes = len(unique)
        self.num_features = A.shape[0]
        self.class_labels = categories

        for i in range(self.num_classes):
            if (K == None):
                self.exemplars.append(A[mapping==i,:])
            else:
                print "A -->",A[mapping==i,:], K
                codebook,codes = vq.kmeans(A[mapping == i,:],K)
                self.exemplars.append(codebook)
            print "build ==",self.exemplars[-1].shape
        return

    def classify(self, A, K=3, return_distances=False):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_distances is
        True, it also returns the NxC distance matrix.

        The parameter K specifies how many neighbors to use in the
        distance computation. The default is three.'''
        # make a matrix that is N x C to store the distance to each class for each data point
        D = np.matrix(np.zeros((A.shape[0],self.num_classes)))
        print "classify ", self.num_classes, D.shape[0],D.shape[1]
        # if K > self.exemplars[i].shape[1]:
        #     #Makes K = num cols if num cols < K
        #     K = self.exemplars[i].shape[1]


        for i in range(self.num_classes):
            # make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
            print "Classify, shape, exemplars shape", A.shape[0], self.exemplars[i].shape[1],self.exemplars[i].shape[0]
            temp = np.matrix(np.zeros((A.shape[0], self.exemplars[i].shape[0])))
            for j in range (self.exemplars[i].shape[0]):
                temp[:,j] = np.sum(np.square(A - self.exemplars[i][j,:]),axis=1)
            temp = np.sort(temp,axis=1)             # sort the distances by row
            print "Classify, temp Val", temp
            D[:,i] = np.sum(temp[:,K],axis=1)       # sum the first K columns

        # calculate the most likely class for each data point
        cats = np.argmin(D, axis = 1)

        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_distances:
            return cats, labels, D

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):
        '''Writes the KNN classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the KNN classifier from the file'''
        # extension
        return
