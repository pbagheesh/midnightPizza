import numpy as np
import copy
import csv
import datetime
import os.path

class Data:
#Data Class --> reads and writes data to
    def __init__(self, filename=None):
	# create and initialize fields for the class
        self.raw_headers = [] #stores the headers of the data as strings in a list
        self.numeric_headers = [] #stores the numeric headers
        self.raw_types = [] #stores the type of each data
        self.raw_data = [[]] #lisTt of lists containg all the data
        self.header2raw = {} #dictionary to conver the header to a raw value

        self.matrix_data = np.matrix([]) # matrix of numeric data
        self.datesData = np.matrix([]) #Matrix of dates
        self.header2matrix = {} # dictionary mapping header string to index of column in matrix data

        if (filename is not None):
            self.read(filename)

#---------------o-------------------o-- CSV --> Internal Data functions --o----------------------o------------------------o

    def read(self,filename):
        #Reads in a file and stores the data in the files into a list of list
        #and populates the header and rawtypes fields
        file = open(filename,'rU')
        lineCount = 0
        for line in file:
            #simply adds data to the raw field (fields holding raw data)
            line = line.strip()

            if lineCount == 0:
                if line[0] == '#':  #Check to see if line is supposed to be a comment
                    continue
                self.raw_headers = (line.split(",")) #Assign to header the first line ie the headers
                for i in range (len(self.raw_headers)):
                    self.raw_headers[i] = self.raw_headers[i].strip()
            elif lineCount == 1:
                self.raw_types = (line.split(","))  #Assign to rawtypes the data type
            elif lineCount == 2:
                #This line is needed so that the first element of the data list is not append
                self.raw_data[0] = line.split(",")
            else:
                self.raw_data.append(line.split(","))
            lineCount +=1  #increment lineCount

        print "Read - Data: ", len(self.raw_data), len(self.raw_data[0])

        self.convertRawDataToNumeric()
        self.convertRawDataToDates()

    def convertRawDataToNumeric(self):
        #Converts the raw data from the fields into useable data for the numpy matrix

        #first create an appropriate sized list of lists
        convertedNumericData = []
        numericColsCount = 0 #Keeps track of how many cols you are adding to the numeric data

        count = 0
        for i in range (self.get_raw_num_rows()):
            tempList = []  #Temporary list storing the row values
            for j in range (self.get_raw_num_columns()):
                self.raw_types[j] = self.raw_types[j].strip()
                if self.raw_types[j] == 'numeric':  #only if this data type is supposed to be numeric
                    if "?"  in self.raw_data[i]:
                        #Checks to see if there is missing data within input file
                        count += 1
                        break

                    if (self.raw_headers[j] not in self.numeric_headers):  #Need to only add each header once
                        self.numeric_headers.append(self.raw_headers[j])

                    if (i == 0): #I only want it to update the dictionary when looping through the first line of the data
                        self.header2raw[self.raw_headers[j].strip()] = j
                        self.header2matrix[self.raw_headers[j].strip()] = numericColsCount

                    tempList.append(float(self.raw_data[i][j]))
                    numericColsCount += 1
            if len(tempList)>0:
                convertedNumericData.append(tempList)  #Assign each row which is supposed to contain numeric data to convertedNumericData
        self.matrix_data=np.matrix(convertedNumericData)

    def convertRawDataToDates(self):
        #Converts the raw data from the fields into useable data for the numpy matrix

        #first create an appropriate sized list of lists
        convertedNumericData = [[]]*self.get_raw_num_rows()

        for i in range (self.get_raw_num_rows()):
            tempList = []  #Temporary list storing the row values
            for j in range (self.get_raw_num_columns()):
                self.raw_types[j] = self.raw_types[j].strip() #strip values
                if self.raw_types[j] == 'date':  #only if this data type is supposed to be a date
                    dt = datetime.datetime.strptime(self.raw_data[i][j], '%x')
                    tempList.append(dt)
            convertedNumericData[i]=(tempList)  #Assign each row which is supposed to contain numeric data to convertedNumericData
        self.datesData=np.matrix(convertedNumericData)

    def write_headers(self, filename, headers=None):
        np.savetxt( filename, self.get_data(headers, self.get_num_rows()))

        with open(filename, 'r') as in_file:
            stripped = (line.strip() for line in in_file)
            lines = (line.split(",") for line in stripped if line)
            csvFileName = filename.replace(".txt",".csv")
            with open(csvFileName, 'w') as out_file:
                writer = csv.writer(out_file)
                # writer.writerow(('title', 'intro'))
                writer.writerows(lines)

    def add_column(self, column,headerName,rawType):
        self.matrix_data = np.hstack((self.matrix_data,column))
        self.raw_headers.append(headerName)

        if (rawType == 'numeric'):
            self.numeric_headers.append(column) #stores the numeric headers

        self.raw_types.append(rawType)


        for i in range(len(self.raw_data)):
            self.raw_data[i].append(column[i])

#---------------o-------------------o-- Accessor functions --o----------------------o------------------------o
#Name of function implies utility
    def get_code(self, rowVal):
        pos = int(len(self.raw_data[0]))-1
        return self.raw_data[rowVal][pos]

    def get_dates(self):
        return self.datesData

    def get_header2matrix(self):
        return self.header2matrix

    def get_raw_headers(self):
        return self.raw_headers[:]

    def get_raw_types(self):
        return self.raw_types[:]

    def get_raw_num_columns(self):
        return int(len(self.raw_data[0])) #Should always work since all rows should have equal num cols even if some are empty

    def get_raw_num_rows(self):
        return len(self.raw_data)

    def get_num_rows(self):
        return len(self.matrix_data)

    def get_raw_row(self, index):
        return self.raw_data[index]

    def get_raw_value(self, index,colName ):
        colInt = self.raw_headers.index(colName)
        return self.raw_data[index][colInt]

    def get_headers(self):
        return self.numeric_headers

    def get_num_columns(self):
        return len(self.header2raw.keys())

    def get_row(self, index):
        #Be careful index values are 0 indexed
        return self.matrix_data[index]

    def get_value(self, rowIndex, colHeader):
        colIndex=self.header2matrix[colHeader]
        return self.matrix_data[rowIndex,colIndex] #the -1 is there to avoid 0 indexing
        #because when you want to get a cell in a table you dont 0 index it

    def get_data(self,columns,rows):

        retListIdex = np.array([0]* len(columns))
        for i in range(len(columns)):
            retListIdex[i]=(self.header2matrix[columns[i]])

        return self.matrix_data[:, retListIdex]

    def get_columns(self, headerList):
        headIdex = []
        for i in range (len(headerList)):
            headIdex.append(self.header2matrix[headerList[i]])
        return self.matrix_data[ : ,headIdex]

    def get_mat_data(self):
        return self.matrix_data

    def containsType(self, type):
        if type in self.raw_types:
            return True
        else:
            return False

#---------------o-------------------o--  override functins --o----------------------o------------------------o

    def __str__(self):
        #Prints out nicely what the data looks like albeit in a rudimentary format
        retString = ""
        for i in range (len(self.raw_data)):
            for j in range (len(self.raw_data[0])):
                retString+=(str(self.raw_data[i][j]) + " ")
            retString+=("\n")
        return retString

if __name__ == '__main__':
    dataObject = Data('testdata2.csv')
    # print dataObject.get_value(3,'numberstuff')
    # print dataObject.get_data(['numberstuff'],2)
    dataObject.write_headers('test.txt',['numberstuff','numberstuff'])
    dataObject.add_column()
