import dialog
import Tkinter as tk
import math
import numpy as np
import tkFileDialog
import os.path
import os
import glob, os
import datetime

'''
    Dialogs is a file that contains all the dialog boxes I use within the application
'''

class AnalysisDialog(dialog.Dialog):
    #Dialog Box for showing the results of the data analysis
    def __init__(self,parent, axes, analysisVals):
        self.xVal = 0
        self.yVal = 0
        self.zVal = 0
        self.axes = axes
        self.cancelPress = False
        self.analysisVals = analysisVals
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        #Store all the data into local variables for easier accessing
        mean = [self.analysisVals[0]]
        stdDev = [self.analysisVals[1]]
        data_range = [self.analysisVals[2]]

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Basic Outline
        #Create Text with all the analysis data
        xText = (str(self.axes[0])+"\n Mean:"+str(mean[0][0])+"\n Std Dev:"+str(stdDev[0][0])+"\n Range:"+str(data_range[0][0]))
        #Create Label with text from above
        xlabel = tk.Label(coordsFrame, text=xText
        , width=40 )
        #Pack label into the dialog box
        xlabel.pack( side=tk.LEFT, pady=10,padx=5)

        yText = (str(self.axes[1])+"\n Mean:"+str(mean[0][1])+"\n Std Dev:"+str(stdDev[0][1])+"\n Range:"+str(data_range[0][1]))

        ylabel = tk.Label( coordsFrame, text=yText, width=40 )
        ylabel.pack( side=tk.LEFT, pady=10,padx=5)

        zText = (str(self.axes[2])+"\n Mean:"+str(mean[0][2])+"\n Std Dev:"+str(stdDev[0][2])+"\n Range:"+str(data_range[0][2]))

        zlabel = tk.Label( coordsFrame, text=zText, width=40 )
        zlabel.pack( side=tk.LEFT, pady=10,padx=5)


        if (len(self.axes) == 4):
            #handle cases where only 4 axes have been chosen
            cText = (str(self.axes[3])+"\n Mean:"+str(mean[0][3])+"\n Std Dev:"+str(stdDev[0][3])+"\n Range:"+str(data_range[0][3]))
            clabel = tk.Label( dialogFrame, text=cText, width=40 )
            clabel.pack( side=tk.LEFT, pady=10, padx =10)

        if (len(self.axes) == 5):
            #Handles cases where all 5 parameters have been chosen
            sText = (str(self.axes[4])+"\n Mean:"+str(mean[0][4])+"\n Std Dev:"+str(stdDev[0][4])+"\n Range:"+str(data_range[0][4]))
            slabel = tk.Label( dialogFrame, text=sText, width=40 )
            slabel.pack(side=tk.LEFT, pady=10, padx=10)

            cText = (str(self.axes[3])+"\n Mean:"+str(mean[0][3])+"\n Std Dev:"+str(stdDev[0][3])+"\n Range:"+str(data_range[0][3]))
            clabel = tk.Label( dialogFrame, text=cText, width=40 )
            clabel.pack( side=tk.LEFT, pady=10, padx =10)

    def apply(self):
        #function that is run when ok button is hit
        self.cancelButton()

    def cancelButton(self):
        #cancel button
        self.cancelPress = True

class LinearRegressionDialog(dialog.Dialog):
    def __init__(self,parent,columnsList):
        self.xVal = 0
        self.yVal = 0
        self.zVal = 0
        self.coords = [None,None,None,None,None]
        self.enoughParams = False
        self.cancelPress = False
        self.columnsList = columnsList
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text="Independent", width=20 )
        label.pack( side=tk.LEFT, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.SINGLE, exportselection=0)
        self.xWindow.pack(side=tk.LEFT,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        #Repeat
        label = tk.Label( coordsFrame, text="Dependent", width=20 )
        label.pack( side=tk.LEFT, pady=10 )

        self.yWindow = tk.Listbox(coordsFrame, selectmode=tk.SINGLE, exportselection=0)
        self.yWindow.pack(side=tk.LEFT, padx=5)

        for i in range (len(self.columnsList)):
            self.yWindow.insert(tk.END, self.columnsList[i])


    def apply(self):
        #function that is run when ok button is hit
        xVal = self.xWindow.curselection()
        yVal = self.yWindow.curselection()

        if (len(xVal) == 0 or len(yVal) == 0):
            #If user has not selected columns for x and y values
            top = tk.Toplevel()
            top.title("Select X Val")

            msg = tk.Message(top, text="Please ensure X and Y parameters are selected")
            msg.pack()

            button = tk.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            self.enoughParams = False
        else:
            #otherwise update fields so that main application can be updated
            if len(xVal) > 0:
                self.coords[0] = self.xWindow.curselection()[0] #assigns to selectVal the distribution selected

            if len(yVal) > 0:
                self.coords[1] = self.yWindow.curselection()[0] #assigns to shapeVal the distribution selected

            self.enoughParams = True

    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVal(self):
        #returns the values from the dialog box as a list
        retList =[0]*2
        for i in range(2):
            if (self.coords[i]== None):
                retList[i] = -1
            else:
                retList[i] = self.columnsList[self.coords[i]]
        return retList

    def getDataPointsVal(self):
        return self.numDataPoints


class DialogBox(dialog.Dialog):
    '''DialogBox class for the buildPoints ie asks users which columns they want to show in the
        application'''
    def __init__(self,parent,columnsList,headerList=["X-Axis","Y-Axis","Z-Axis","Color","Size"]):
        self.xVal = 0
        self.yVal = 0
        self.zVal = 0
        self.coords = [None,None,None,None,None]
        self.enoughParams = False
        self.cancelPress = False
        self.columnsList = columnsList
        self.headersList = headerList
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text=self.headersList[0], width=20 )
        label.pack( side=tk.LEFT, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.SINGLE, exportselection=0)
        self.xWindow.pack(side=tk.LEFT,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        #Repeat
        label = tk.Label( coordsFrame, text="Y Axis", width=20 )
        label.pack( side=tk.LEFT, pady=10 )

        self.yWindow = tk.Listbox(coordsFrame, selectmode=tk.SINGLE, exportselection=0)
        self.yWindow.pack(side=tk.LEFT, padx=5)

        for i in range (len(self.columnsList)):
            self.yWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label( coordsFrame, text="Z Axis", width=20 )
        label.pack( side=tk.LEFT, pady=10 )

        self.zWindow = tk.Listbox(coordsFrame, selectmode=tk.SINGLE, exportselection=0)
        self.zWindow.pack(side=tk.LEFT, padx=5)

        for i in range (len(self.columnsList)):
            self.zWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label( dialogFrame, text="Color(If you select \n it will override K- Clustering)", width=20 )
        label.pack( side=tk.LEFT, pady=10 )

        self.cWindow = tk.Listbox(dialogFrame, selectmode=tk.SINGLE, exportselection=0)
        self.cWindow.pack(side=tk.LEFT, padx=5)

        for i in range (len(self.columnsList)):
            self.cWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label( dialogFrame, text="Size", width=20 )
        label.pack(side=tk.LEFT, pady=10 )

        self.sWindow = tk.Listbox(dialogFrame, selectmode=tk.SINGLE, exportselection=0)
        self.sWindow.pack(side=tk.LEFT, padx=5)

        for i in range (len(self.columnsList)):
            self.sWindow.insert(tk.END, self.columnsList[i])

    def apply(self):
        #function that is run when ok button is hit
        xVal = self.xWindow.curselection()
        yVal = self.yWindow.curselection()
        zVal = self.zWindow.curselection()

        if (len(xVal) == 0 or len(yVal) == 0 or len(zVal) == 0):
            #If user has not selected columns for x y and z
            top = tk.Toplevel()
            top.title("Select X Val")

            msg = tk.Message(top, text="Please ensure X, Y and Z parameters are selected")
            msg.pack()

            button = tk.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            self.enoughParams = False
        else:
            #otherwise update fields so that main application can be updated
            if len(xVal) > 0:
                self.coords[0] = self.xWindow.curselection()[0] #assigns to selectVal the distribution selected

            if len(yVal) > 0:
                self.coords[1] = self.yWindow.curselection()[0] #assigns to shapeVal the distribution selected

            if len(zVal) > 0:
                self.coords[2] = self.zWindow.curselection()[0] #assigns to shapeVal the distribution selected

            cVal = self.cWindow.curselection()
            if len(cVal) > 0:
                self.coords[3] = self.cWindow.curselection()[0] #assigns to shapeVal the distribution selected

            sVal = self.sWindow.curselection()
            if len(sVal) > 0:
                self.coords[4] = self.sWindow.curselection()[0] #assigns to shapeVal the distribution selected

            self.enoughParams = True

    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVal(self):
        #returns the values from the dialog box as a list
        retList =[0]*5
        for i in range(5):
            if (self.coords[i]== None):
                retList[i] = -1
            else:
                retList[i] = self.columnsList[self.coords[i]]
        return retList

    def getDataPointsVal(self):
        return self.numDataPoints

class LinearRegressionVals(dialog.Dialog):
    #Dialog Box for showing the results of the linear Regression
    def __init__(self,parent, slope, intercept, rValue):
        self.slope = slope
        self.intercept = intercept
        self.rValue = rValue
        self.cancelPress = False
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        #Store all the data into local variables for easier accessing
        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        lrText = ("Slope: "+str(self.slope)+"\n Intercept: "+str(self.intercept)+"\n rValue: "+str(self.rValue))

        lrLabel = tk.Label( coordsFrame, text=lrText, width=40 )
        lrLabel.pack( side=tk.LEFT, pady=10,padx=5)

    def apply(self):
        #function that is run when ok button is hit
        self.cancelButton()

    def cancelButton(self):
        #cancel button
        self.cancelPress = True

class pcaDialogBox(dialog.Dialog):
    #Dialog box to allow users to select the headers PCA needs to be conducted on
    def __init__(self,parent,columnsList):
        self.returnVals = []
        self.coords = [None,None,None,None,None]
        self.columnsList = columnsList
        self.normalize = tk.IntVar()
        self.name = None
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text="Independent", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.xWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        self.normalizeCheck = tk.Checkbutton(coordsFrame, text="Normalize", variable=self.normalize, onvalue = 1, offvalue = 0)
        self.normalizeCheck.pack()

        nameLabel = tk.Label(coordsFrame, text="Analysis Name *(optional)", width=20 )
        nameLabel.pack( side=tk.TOP, pady=10)

        self.nameLabel = tk.Entry(coordsFrame)
        self.nameLabel.pack()


    def apply(self):
        #function that is run when ok button is hit
        xVal = self.xWindow.curselection()

        if len(xVal) > 0:
            self.coords[0] = self.xWindow.curselection() #assigns to selectVal the distribution selected

        retList = []
        if (self.coords[0] != None and self.columnsList != None):
            for i in range(len(self.coords[0])):
                retList.append(self.columnsList[ self.coords[0][i] ])
        self.returnVals = retList
        self.name = self.nameLabel.get().strip()

    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVal(self):
        #returns the values from the dialog box as a list
        return self.returnVals

    def getNormalize(self):
        if (self.normalize.get() == 1):
            return True
        else:
            return False

    def getDataPointsVal(self):
        return self.numDataPoints

class eigenVectorSelector(dialog.Dialog):
    #Dialog box to select the eigen values to be displayed
    def __init__(self,parent,columnsList):
        self.returnVals = []
        self.coords = [None,None,None,None,None]
        self.columnsList = columnsList
        self.save = tk.IntVar()
        self.returnVals = None
        self.name = None
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.LEFT)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.LEFT)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text="X", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.xWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label(coordsFrame, text="Y", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.yWindow = tk.Listbox(coordsFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.yWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.yWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label(coordsFrame, text="Z", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.zWindow = tk.Listbox(coordsFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.zWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.zWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label(dialogFrame, text="Color", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.cWindow = tk.Listbox(dialogFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.cWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.cWindow.insert(tk.END, self.columnsList[i])

        label = tk.Label(dialogFrame, text="Size", width=20 )
        label.pack( side=tk.TOP, pady=10 )

        #Create a Window
        self.sWindow = tk.Listbox(dialogFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.sWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.sWindow.insert(tk.END, self.columnsList[i])

        self.saveCheck = tk.Checkbutton(coordsFrame, text="Save *once you click PCA Details", variable=self.save, onvalue = 1, offvalue = 0)
        self.saveCheck.pack()

    def apply(self):
        #function that is run when ok button is hit
        retList = []
        if len(self.xWindow.curselection()) > 0:
            retList.append(self.columnsList[self.xWindow.curselection()[0]])
        else:
            retList.append(self.columnsList[0])

        if len(self.yWindow.curselection()) > 0:
            retList.append(self.columnsList[self.yWindow.curselection()[0]])
        else:
            retList.append(self.columnsList[0])

        if len(self.zWindow.curselection()) > 0:
            retList.append(self.columnsList[self.zWindow.curselection()[0]])
        else:
            retList.append(self.columnsList[0])

        if len(self.cWindow.curselection()) > 0:
            retList.append(self.columnsList[self.cWindow.curselection()[0]])
        else:
            retList.append(None)

        if len(self.sWindow.curselection()) > 0:
            retList.append(self.columnsList[self.sWindow.curselection()[0]])
        else:
            retList.append(None)
        self.returnVals = retList

    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVal(self):
        #returns the values from the dialog box as a list
        return self.returnVals

    def getSaveVal(self):
        if (self.save.get() == 1):
            return True
        else:
            return False

    def getDataPointsVal(self):
        return self.numDataPoints



class pcaViewDialogBox(dialog.Dialog):
    #Display the results of the PCA statistics
    def __init__(self,parent,pcaObj, save= False):
        self.pcaObj = pcaObj
        self.save = save
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()
        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        headers = self.pcaObj.get_data_headers()

        eigenVectors = self.pcaObj.get_eigenvectors()
        eigenValues = self.pcaObj.get_eigenvalues()

        eigenValuesLabel = tk.Label(coordsFrame, text="E-Val").grid(row=0, column=1)

        if (self.save == True) :
            now = datetime.datetime.now()
            curTime = str(now.day)+str(now.hour)+str(now.minute) + str(now.second)
            if (os.path.exists("PCAData") == True):
                pcaFile = open("PCAData/PCA:"+str(curTime)+".txt", 'wb')
            else:
                os.mkdir("PCAData",0755)
                pcaFile = open("PCAData/PCA:"+str(curTime)+".txt", 'wb')

        for i in range(len(headers)):
            headerLabel = tk.Label(coordsFrame, text= headers[i]).grid(row=0, column=2+i)
            pLabels = tk.Label(coordsFrame, text="P"+str(i)).grid(row=i+1, column=0)

            for i in range(len(headers)):
                eigenLabel = tk.Label(coordsFrame, text= str(round(eigenValues[i],4))).grid(row=i+1, column=1)

        if (self.save == True):
            for i in range(len(headers)):
                for j in range(self.pcaObj.get_num_columns()):
                    sampleLabel = tk.Label(coordsFrame, text=str(round(eigenVectors[i,j], 4))).grid(row=i+1, column=j+2)
                    pcaFile.write(str(round(eigenVectors[i,j], 4)) + " " )
        else:
            # I did this since if I put the if statement within the for loop it would have
            # to check if save is true each time it is looping through -- Good Code :)
            for i in range(len(headers)):
                for j in range(self.pcaObj.get_num_columns()):
                    sampleLabel = tk.Label(coordsFrame, text=str(round(eigenVectors[i,j], 4))).grid(row=i+1, column=j+2)

    def apply(self):
        return

    def cancelButton(self):
        return


class kmeansDialogBox(dialog.Dialog):
    #Code is same as PCA dialog box since they ask the same things
    def __init__(self,parent,columnsList):
        self.returnVals = []
        self.coords = [None,None,None,None,None]
        self.columnsList = columnsList
        self.normalize = tk.IntVar()
        self.manhattanify = tk.IntVar()
        self.name = None
        self.cancelPress = False
        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text="Independent", width=20 )
        label.pack( side=tk.TOP, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.EXTENDED, exportselection=0)
        self.xWindow.pack(side=tk.TOP,padx=5)
        #Populate Window with desired columns
        for i in range (len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        self.normalizeCheck = tk.Checkbutton(coordsFrame, text="Whitten", variable=self.normalize, onvalue = 1, offvalue = 0)
        self.normalizeCheck.pack()

        self.manhattanCheck = tk.Checkbutton(coordsFrame, text="Manhatten", variable=self.manhattanify, onvalue = 1, offvalue = 0)
        self.manhattanCheck.pack()

        nameLabel = tk.Label(coordsFrame, text="K-Value \n (Must be Less than 20)", width=20 )
        nameLabel.pack( side=tk.TOP, pady=10)

        self.nameLabel = tk.Entry(coordsFrame)
        self.nameLabel.pack()


    def apply(self):
        #function that is run when ok button is hit
        xVal = self.xWindow.curselection()

        if len(xVal) > 0:
            self.coords[0] = self.xWindow.curselection() #assigns to selectVal the distribution selected

        retList = []
        if (self.coords[0] != None and self.columnsList != None):
            for i in range(len(self.coords[0])):
                retList.append(self.columnsList[ self.coords[0][i] ])
        self.returnVals = retList
        try:
            self.name = int(self.nameLabel.get().strip())
        except:
            print "please enter an integer value"


    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVal(self):
        #returns the values from the dialog box as a list
        if (self.returnVals == None or self.name == None):
            return None
        else:
            return self.returnVals

    def getNormalize(self):
        if (self.normalize.get() == 1):
            return True
        else:
            return False

    def getManhattan(self):
        if (self.manhattanify.get() == 1):
            return True
        else:
            return False

    def getDataPointsVal(self):
        return self.numDataPoints


class trainClassiferDialog(dialog.Dialog):
    def __init__(self,parent):
        self.xVal = 0
        self.yVal = 0
        self.zVal = 0
        self.coords = [None,None,None,None,None]
        self.enoughParams = False
        self.cancelPress = False
        self.classOption = None
        self.columnsList = []

        os.chdir(os.getcwd())
        for file in glob.glob("*.csv"):
            self.columnsList.append(file)

        dialog.Dialog.__init__(self,parent)

    def body(self,parent):
        # tk.Label(top,text="Value").pack()

        coordsFrame = tk.Frame(self)
        coordsFrame.pack(side=tk.TOP)

        dialogFrame = tk.Frame(self)
        dialogFrame.pack(side=tk.TOP)

        #Base Logic (Applicable for all the rest of these)
        #Create a label
        label = tk.Label(coordsFrame, text="Training Set", width=20 )
        label.pack( side=tk.LEFT, pady=10 )
        #Create a Window
        self.xWindow = tk.Listbox(coordsFrame,selectmode=tk.SINGLE, exportselection=0)
        self.xWindow.pack(side=tk.LEFT,padx=5)

        for i in range( len(self.columnsList)):
            self.xWindow.insert(tk.END, self.columnsList[i])

        # os.chdir(os.getcwd())
        # for file in glob.glob("*.csv"):
        #     self.xWindow.insert(tk.END, file)

        #Repeat
        label = tk.Label( coordsFrame, text="Test Set", width=20 )
        label.pack( side=tk.LEFT, pady=10 )

        self.yWindow = tk.Listbox(coordsFrame, selectmode=tk.SINGLE, exportselection=0)
        self.yWindow.pack(side=tk.LEFT, padx=5)

        os.chdir(os.getcwd())
        for file in glob.glob("*.csv"):
            self.yWindow.insert(tk.END, file)

        kVal = tk.Label(dialogFrame, text="K Value * Only for KNN", width=20 )
        kVal.pack( side=tk.BOTTOM, pady=10)
        self.kVal = tk.Entry(dialogFrame)
        self.kVal.pack(side=tk.BOTTOM)

        self.classOption = tk.StringVar(dialogFrame)
        self.classOption.set("Naive Bayes")
        classOption = tk.OptionMenu( dialogFrame, self.classOption,
                                        "Naive Bayes", "KNN") # can add a command to the menu
        classOption.pack(side=tk.BOTTOM)

    def apply(self):
        #function that is run when ok button is hit
        xVal = self.xWindow.curselection()
        yVal = self.yWindow.curselection()

        classType = str(self.classOption)[-1]
        if not self.kVal.get():
            kValue = None
        else:
            kValue = int(self.kVal.get())

        print classType, type(classType), kValue

        if (len(xVal) == 0 or len(yVal) == 0):
            #If user has not selected columns to train on and to categorize
            top = tk.Toplevel()
            top.title("Select Categories to trainVal")

            msg = tk.Message(top, text="Please ensure to select one from each box")
            msg.pack()

            button = tk.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            self.enoughParams = False
        elif (len(xVal) > 0 and len(yVal) > 0 and classType=="2" and kValue == -1):
            top = tk.Toplevel()
            top.title("Select Categories to trainVal")

            msg = tk.Message(top, text="Please ensure to select one from each box")
            msg.pack()

            button = tk.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            self.enoughParams = False
        else:
            #otherwise update fields so that main application can be updated
            if len(xVal) > 0:
                self.coords[0] = self.xWindow.curselection() #assigns to selectVal the distribution selected
                retList = []
                if (self.coords[0] != None and self.columnsList != None):
                    for i in range(len(self.coords[0])):
                        retList.append(self.columnsList[ self.coords[0][i] ])
                self.returnVals = retList
            if len(yVal) > 0:
                self.coords[1] = self.yWindow.curselection()[0] #assigns to shapeVal the distribution selected

            self.kValue = kValue
            self.classType = classType

            self.enoughParams = True

    def cancelButton(self):
        #what needs to be pressed when cancel button is hit
        self.cancelPress = True

    def getVals(self):
        retList = [None]*4
        if (self.enoughParams == True):
            retList[0] = self.returnVals[0]
            retList[1] = self.columnsList[self.coords[1]]
            retList[2] = self.classType
            retList[3] = self.kValue
        return retList


    def getDataPointsVal(self):
        return self.numDataPoints
