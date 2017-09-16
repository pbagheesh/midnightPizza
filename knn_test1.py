# Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# KNN class test
#

import sys
import data
import classifiers

def main(argv):
    '''Builds two KNN classifiers and prints them out.  The first uses all
    of the exemplars, the second uses only 10.

    '''

    # usage
    if len(argv) < 2:
        print 'Usage: python %s <data file> <optional category file>' % (argv[0])
        exit(-1)

    # read the data
    d = data.Data(argv[1])

    # get the categories and data matrix
    if len(argv) > 2:
        catdata = data.Data(argv[2])
        cats = catdata.get_data( [catdata.get_headers()[0]], catdata.get_num_rows())
        A = d.get_data( d.get_headers(), d.get_num_rows())
    else:
        # assume the categories are the last column
        cats = d.get_data( [d.get_headers()[-1]], d.get_num_rows())
        A = d.get_data( d.get_headers()[:-1], d.get_num_rows())

    # create a new classifier
    knnc = classifiers.KNN()

    # build the classifier using all exemplars
    knnc.build( A, cats )

    # print the classifier
    # requires a __str__ method
    print knnc


    # build and print the classifier using 10 exemplars per class
    knnc2 = classifiers.KNN()
    knnc2.build( A, cats, 10 )
    print knnc2

    return

if __name__ == "__main__":
    main(sys.argv)
