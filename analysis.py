import numpy as np
import pcaData
import os.path
import datetime
import scipy.stats
import scipy.cluster.vq as vq
import random

class Analysis:
    #Analyzes data
    def data_range(self, columnHeaders, dataObject):
        #Returns a list which has 2 element long lists that store the min, max value of the column
        retList = []
        for i in range (len(columnHeaders)):
            tempList = [columnHeaders[i]]
            maxVal = dataObject.get_data(tempList,dataObject.get_raw_num_rows()).max()
            minVal = dataObject.get_data(tempList,dataObject.get_raw_num_rows()).min()
             #I store the min and max val in separate local variables just to improve the readibility of the code
            minMaxList = [minVal,maxVal]
            retList.append(minMaxList)
        return retList

    def mean(self, columnHeaders,  dataObject):
        #Calculates the mean of all the columns as specified by the list of column headers
        #passed in as the initial parameters for the object
        retList = []
        # cols = dataObject.get_columns(columnHeaders)
        for i in range (len(columnHeaders)):
            tempList = [columnHeaders[i]]
            mean = [dataObject.get_data(tempList, dataObject.get_raw_num_rows()).mean()]
            # mean = np.around(mean,decimals=4)
            # I dont know why but this adds array when I print it so I didnt know whether to use it or not
            retList.append(mean)
        return retList

    def stddev(self,columnHeaders, dataObject):
        retList = []
        for i in range (len(columnHeaders)):
            tempList = [columnHeaders[i]]
            std = [dataObject.get_data(tempList, dataObject.get_raw_num_rows()).std()]
            # mean = np.around(mean,decimals=4)
            # I dont know why but this adds array when I print it so I didnt know whether to use it or not
            retList.append(std)
        return retList

    def var(self, columnHeaders,  dataObject):
        #Calculates the variance of all the columns as specified by the list of column headers
        retList = []
        for i in range (len(columnHeaders)):
            tempList = [columnHeaders[i]]
            mean = [dataObject.get_data(tempList, dataObject.get_raw_num_rows()).var()]
            # mean = np.around(mean,decimals=4)
            # I dont know why but this adds array when I print it so I didnt know whether to use it or not
            retList.append(mean)
        return retList

    def median(self, columnHeaders, dataObject):
        cols = dataObject.get_columns(columnHeaders)
        retList = []
        for i in range (len(columnHeaders)):
            retList.append(np.median(cols[:, [i]], axis=0))
        return retList

    def normalize_columns_separately(self, columnHeaders, dataObject):
        #Normalizes the data values by column headers
        #returns a numpy matrix object
        cols = dataObject.get_columns(columnHeaders)
        for i in range (len(columnHeaders)):
            cols[: ,[i]] = cols[: ,[i]] - cols[: ,[i]].min()
            cols[: ,[i]] = cols[: ,[i]] / cols[: ,[i]].max()
        return cols

    def normalize_columns_together(self, columnHeaders, dataObject):
        #Normalizes the data values together
        #returns a numpy matrix object
        cols = dataObject.get_columns(columnHeaders)
        cols = cols - cols.min()
        cols = cols / cols.max()
        return cols

    def linear_regression(self, data, ind, dep, saveFile = False):
        #does a linear regression according to instructions provided by the project page
        ones = np.matrix(np.ones(data.get_raw_num_rows())).transpose()
        A = np.hstack((data.get_columns(ind),ones))  #Add the third column as ones
        if (len(dep) == 1):
            y = data.get_columns(dep)
            AAinv = np.linalg.inv(np.dot(A.transpose(), A))

            x = np.linalg.lstsq(A,y)

            b = x[0]

            N =y.shape[0]
            C = b.shape[0]

            df_e = N-C
            df_r = C-1

            error = y - np.dot(A,b)

            sse = np.dot(error.transpose(), error)/df_e

            stderr = np.sqrt(np.diagonal(sse[0,0]* AAinv))

            t = b.transpose()/ stderr

            p = 2*(1- scipy.stats.t.cdf(abs(t), df_e))

            r2 = 1 - error.var()/ y.var()

            if (saveFile == True):
                self.output_linearRegression(b, sse, r2, t, p, ind, dep)
        else:
            print "Please select only one dependent variable"

        return b, sse, r2, t, p

    def output_linearRegression(self, b, sse, r2, t, p,ind, dep):
        #Saves the output of calling linear regression as a txt file in a folder called linearRegressions
        now = datetime.datetime.now()
        curTime = str(now.day)+str(now.hour)+str(now.minute) + str(now.second)
        if (os.path.exists("linearRegressions") == True):
            fileObject  = open("linearRegressions/linearRegression"+str(curTime)+".txt", "w+")
            fileObject.write("                   " + str(ind)+" vs "+ str(dep) + "\n")
            fileObject.write("m0 :" + str(b[0]))
            fileObject.write("\nm1 :" + str(b[1]))
            fileObject.write("\nb :" + str(b[2]))
            fileObject.write("\nSSE :"+ str(sse))
            fileObject.write("\nR2 :"+ str(r2))
            fileObject.write("\nT :"+ str(t))
            fileObject.write("\nP :"+ str(p))
            fileObject.close()
        else:
            os.mkdir("linearRegressions",0755)
            fileObject  = open("linearRegressions/linearRegression"+str(curTime)+".txt", "w+")
            fileObject.write("                   " + str(ind)+" vs "+ str(dep) + "\n")
            fileObject.write("m0 :" + str(b[0]))
            fileObject.write("\nm1 :" + str(b[1]))
            fileObject.write("\nb :" + str(b[2]))
            fileObject.write("\nSSE :"+ str(sse))
            fileObject.write("\nR2 :"+ str(r2))
            fileObject.write("\nT :"+ str(t))
            fileObject.write("\nP :"+ str(p))
            fileObject.close()

    # This version uses SVD
    def pca(self, d, headers, normalize=False):
        if (normalize==True):
            A = self.normalize_columns_separately(headers,d)
        else:
            A = d.get_data(headers, d.get_num_rows())

        m = np.mean(A, axis=0) #Need to transpose becaus`e my mean returns as a list and need it to be in matrix for to create D
        D = A - m

      # assign to U, S, V the result of running np.svd on D, with full_matrices=False
        U, S, V = np.linalg.svd(D, full_matrices=False)
      # the eigenvalues of cov(A) are the squares of the singular values (S matrix)
      #   divided by the degrees of freedom (N-1). The values are sorted.

        eigenValues = (S**2)/(len(A)-1)
        eigenVectors = V

        projectedData = (V * D.T).T

        pcaDataObj = pcaData.PCAData(headers, projectedData, eigenValues,eigenVectors, m)
        return pcaDataObj

    def kmeans_numpy(self, d, headers, K, whiten= True):
        '''
        Takes in a Data object, a set of headers, and the number of clusters to create
        Computes and returns the codebook, codes, and representation error.
        '''
        if (d == None or headers == None or K == None):
            return
        else:
            A = d

            if (whiten == True):
                W = vq.whiten(A)
            else:
                W = A

            codebook,bookerror = vq.kmeans(W,K)
            codes, error = vq.vq(W, codebook)

        return codebook, codes , error

    def kmeans_init(self, d, K, categories = None):
        if (categories == None):
            retMatrix = np.matrix(np.zeros((K, d.shape[1])))
            # retMatrix = np.matrix(np.zeros(shape=(K,len(d) )))
            kvals = {}
            for i in range (K):
                randomInt = random.randint(0,d.shape[0])
                while (randomInt in kvals.values()):
                    #Makes sure the same random integer is not chosen twice
                    randomInt = random.randint(0,d.shape[0])
                retMatrix[i] = (d[randomInt])
        else:
            unique,labels=np.unique(categories.tolist(),return_inverse=True)
            means = np.zeros((K, d.shape[1]))
            retMatrix = np.matrix(np.zeros((K, d.shape[1])))
            for i in range(len(unique)):
            	means[i,:] = np.mean(d[labels==i,:],axis=0)
            retMatrix = means

        return retMatrix

    def kmeans_classify(self,data,means,manhattan=False):
        idVals=[]      #ID Vals
        meanId = {}  #Dictionary for mean values
        mindistances=[]   #Shortest distances

        for i in range (len(data)):
            distances =[]
            for mean in means:
                if (manhattan == False):
                    difference = data[i]-mean
                    square = np.square(difference)
                    sums = np.sum(square)
                    distance = np.sqrt(sums)
                else:
                    difference = data[i]-mean
                    difference = np.absolute(difference)
                    distance = np.sum(difference)
                distances.append(distance)

            lowestVal = distances[np.argmin(distances)]
            idVals.append( distances.index(lowestVal) )
            mindistances.append(lowestVal)
        return (idVals,mindistances)

    def kmeans_algorithm(self, A, means,manhattan):
        # set up some useful constants
        MIN_CHANGE = 1e-7
        MAX_ITERATIONS = 100
        D = means.shape[1]
        K = means.shape[0]
        N = A.shape[0]

        # iterate no more than MAX_ITERATIONS
        for i in range(MAX_ITERATIONS):
            # calculate the codes
            codes, errors = self.kmeans_classify( A, means, manhattan)

            # calculate the new means
            newmeans = np.zeros_like( means )
            counts = np.zeros( (K, 1) )
            for j in range(N):
                newmeans[codes[j],:] += A[j,:]
                counts[codes[j],0] += 1.0

            # finish calculating the means, taking into account possible zero counts
            for j in range(K):
                if counts[j,0] > 0.0:
                    newmeans[j,:] /= counts[j, 0]
                else:
                    newmeans[j,:] = A[random.randint(0,A.shape[0]),:]

            # test if the change is small enough
            diff = np.sum(np.square(means - newmeans))
            means = newmeans
            if diff < MIN_CHANGE:
                break

        # call classify with the final means
        codes, errors = self.kmeans_classify( A, means, manhattan)

        # return the means, codes, and errors
        return (means, codes, errors)

    def kmeans(self, d, headers, K, whiten=True,categories = None, manhattan=False):
        A= d
        if whiten==True:
            W=vq.whiten(A)
        else:
            W=A
        print K
        codebook= self.kmeans_init(W,K,categories)
        codebook, codes, errors = self.kmeans_algorithm(W,codebook, manhattan)
        return codebook, codes, errors
