import data
import numpy as np

class PCAData(data.Data):
    #Projected Data class
    def __init__(self, originalDataHeaders, projectedData, eigenValues,eigenVectors, origDataMean):
        #Fields not present in data class
        self.eigenValues = eigenValues
        self.eigenVectors = eigenVectors
        self.meanDataVals = origDataMean
        self.originalDataHeaders = originalDataHeaders
        self.name=None

        #Populating fields inherited from data class
        self.raw_headers = ["E"]*len(self.originalDataHeaders)
        self.raw_types = ["numeric"]* len(self.originalDataHeaders)
        self.numeric_headers = ["E"]*len(self.originalDataHeaders)
        self.header2matrix = {}
        self.header2raw = {} #dictionary to conver the header to a raw value

        self.raw_data = []


        self.matrix_data = projectedData
        self.datesData = np.matrix([]) #Matrix of dates

        for i in range (len(self.originalDataHeaders)):
            self.raw_headers[i] = ("E" + str(i))
            self.numeric_headers[i]= ("E" + str(i))
            self.header2matrix[("E" + str(i))] = i
            self.header2raw[("E" + str(i))] = i

        for i in range(len(projectedData)):
            col = []
            for j in range(len(self.originalDataHeaders)):
                col.append(str(projectedData[i,j]))
            self.raw_data.append(col)
        # print self.numeric_headers

    def get_eigenvalues(self):
        return self.eigenValues.copy()
    def get_eigenvectors(self):
        return self.eigenVectors.copy()
    def get_data_means(self):
        return self.meanDataVals.copy()
    def get_data_headers(self):
        return list(self.originalDataHeaders)

    def update_name(self, newName):
        self.name = newName

    def get_name(self):
        return self.name
