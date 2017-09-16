# Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
# Additions by Prashant
#
# CS 251
# Spring 2015

import Tkinter as tk
import tkFileDialog
import tkFont as tkf
import numpy as np
import scipy.stats
import dialog
import data
import math
import random
import view
import analysis
import dialogs
import os.path
import datetime
import pcaData
import classify

# from enum import Enum
# create a class to build and manage the display
class DisplayApp:

    def __init__(self, width, height):

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("Midnight Pizza")

        # set the maximum size of the window for resizing
        self.root.maxsize(1600, 900 )

        self.zoomLevel = 1.0
        self.zoomLabel = None

        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()

        # build the Canvas
        self.buildCanvas()

        # bring the window to the front
        self.root.lift()

        # - do idle events here to get actual canvas size
        self.root.update_idletasks()

        # now we can ask the size of the canvas
        self.canvas.winfo_geometry()

        # set up the key bindings
        self.setBindings()

        # set up the application state
        self.objects = [] # list of data objects that will be drawn in the canvas
        self.data = None # will hold the raw data someday.
        self.baseClick = None # used to keep track of mouse movement
        self.baseExtent = None
        self.baseView = None

        self.dataObject = None #Stores the data Object
        self.preDataObject = None #Stores the data object with raw data
        self.spatial_matrix = None #the matrix containing the data points for x,y,z plotting
        self.color_points = None #Stores the axis points represented by color
        self.size_points = None #Stores the axis points represented by size

        # self.xaxes_points = None

        self.plotAxes = None  #Holds the axes labels for x,y and z
        self.colorAxes = None #Axes label for color
        self.sizeAxes = None #Axes label for size

        self.dataSize = 3  #Made data size a field so that if in future I want user to control base size it is easy
        self.analysisVals = None #Values that are generated from analysing the data in the app

        self.viewObject = view.View() #view object
        self.axes = np.matrix ( #axes , mainly stays fixed
                            [[0,0,0,1],
                             [1,0,0,1],
                             [0,0,0,1],
                             [0,1,0,1],
                             [0,0,0,1],
                             [0,0,1,1]]
        )
        self.lineObjects = [] #the actual lines representing the axes
        self.buildAxes()

        #Fields for Linear Regression:
        self.graphObjects = []
        self.graphEndPoints = None
        self.pNM = None   #preNormalized

        self.dataObjects = []
        self.pcaDataObjects = {}

        self.classifierObjects = {}

        self.saveBool = False #Decides if the PCA Analysis be saved
        self.kVal = 0

#---------------o-------------------o--  Axes/Points Building functions --o----------------------o------------------------o

    def buildAxes(self):
        #Builds the axes by creating a view transformation matrix
        #the view transformation matrix then gets multiplied with the self.axes to create the points for the axes

        vtm =  self.viewObject.build()
        pts = (vtm*self.axes.transpose()).transpose() #Creates the pts

        xaxis = self.canvas.create_line(pts[0,0],pts[0,1],pts[1,0],pts[1,1], tags="xaxis") #assigns appropriate points to x axis
        xaxisText = self.canvas.create_text(pts[1,0]+10,pts[1,1], text="x",tags="x")
        self.lineObjects.append(xaxis)

        yaxis = self.canvas.create_line(pts[2,0],pts[2,1],pts[3,0], pts[3,1], tags="yaxis") #assigns appropriate points to y axis
        yaxisText = self.canvas.create_text(pts[3,0],pts[3,1]-10, text="y",tags="y")
        self.lineObjects.append(yaxis)

        zaxis = self.canvas.create_line(pts[4,0],pts[4,1],pts[5,0], pts[5,1], tags="zaxis") #assigns appropriate points to z axis
        zaxisText = self.canvas.create_text(pts[5,0]-10,pts[5,1]+10, text="z",tags="z")
        self.lineObjects.append(zaxis)

    def buildPoints(self):
        #Build Points creates the data points on the canvas from the columns selected by the dialog box
        distinctColors = [(0,0,0),
        (211,211,211),(255,0,255),(153,50,204),(230,230,250),(0,0,255),
        (25,25,112),(64,224,208),(0,128,128),(0,255,0),(160,255,170),(50,205,50),
        (127,255,0),(245,245,20),(85,107,47),(255,127,80),(255,248,220),(255,0,0),(255,192,203)]



        if (self.spatial_matrix == None):
            #If buildPoints is being called when there are points already on the data then you first needed
            #to clear that data and then add the new points
            if (self.dataObject != None):
                #this checks to see if a data object exists or not.
                if(self.chooseAxes() == True):
                    analysisObject = analysis.Analysis()
                    normalizedData = analysisObject.normalize_columns_separately(self.plotAxes,self.dataObject) #Normalizes data
                    self.spatial_matrix = normalizedData
                    homogCoord = []
                    for i in range (len(self.spatial_matrix)): #Adds the homogenous coordinate to the spatial matrix the first time it is built
                        homogCoord.append([1])
                    self.spatial_matrix = np.hstack((self.spatial_matrix,homogCoord))

                    #Makes sure that colorAxes/sizeAxes gets normalized
                    if (self.colorAxes != None):
                        self.color_points = analysisObject.normalize_columns_separately(self.colorAxes,self.dataObject)
                    if (self.sizeAxes != None):
                        self.size_points = analysisObject.normalize_columns_separately(self.sizeAxes,self.dataObject)

                    vtm =  self.viewObject.build() # builds vtm
                    pts = (vtm*self.spatial_matrix.transpose()).transpose() #Generates a set of points through the transformation matrices

                    self.updateAxes()
                    dx = self.dataSize
                    for i in range (len(self.spatial_matrix)):
                        rgb = "#%02x%02x%02x" % (0, 0, 255) #Base Color is blue to differentiate from when color axes has been selected or not
                        if (self.color_points != None):
                         #Low RGB value is green and gradient slowly increases to more red color
                            rgb = "#%02x%02x%02x" % (39.2+(self.color_points[i]*215.8), 210-(self.color_points[i]*210), self.color_points[i]*7)

                        if (self.dataObject.containsType('code')):
                            if (self.kVal < len(distinctColors)):
                                code = int(self.dataObject.get_code(i))
                                rgb = "#%02x%02x%02x" % distinctColors[code]

                        if (self.size_points != None):
                            #changing size
                            dx = self.dataSize*self.size_points[i]

                        x = pts[i,0]
                        y = pts[i,1]
                        circle = self.canvas.create_oval( int(x-dx), int(y-dx), int(x+dx), int(y + dx), tags=(("dtp"+ str(i))), fill=rgb) # Assigns each data point a unique tag
                        self.objects.append(circle)
            else:
                #if data object doesnt exist then run handleOpen
                self.handleOpen(plot = True)
        else:
            self.clearScreenData()
            self.buildPoints()

    def buildPCA(self, PCAData):
        '''
            Builds the PCA Data points
            Exactly the same as Build Points but using PCAData
        '''
        self.clearScreenData()

        analysisObject = analysis.Analysis()
        eigenDbox = dialogs.eigenVectorSelector(self.root,PCAData.get_headers())
        self.saveBool = eigenDbox.getSaveVal()
        headerList = eigenDbox.getVal()

        spatialDataList = list(headerList)
        spatialDataList = spatialDataList[:3]

        normalizedData = analysisObject.normalize_columns_separately(spatialDataList,PCAData) #Normalizes data
        self.spatial_matrix = normalizedData

        if (headerList [3]!= None):
            self.color_points = analysisObject.normalize_columns_separately([headerList[3]],PCAData)
        if (headerList [4]!= None):
            print headerList[4], type(headerList[4])
            self.size_points = analysisObject.normalize_columns_separately([headerList[4]],PCAData)


        homogCoord = []
        for i in range (len(self.spatial_matrix)): #Adds the homogenous coordinate to the spatial matrix the first time it is built
            homogCoord.append([1])
        self.spatial_matrix = np.hstack((self.spatial_matrix,homogCoord))

        vtm =  self.viewObject.build() # builds vtm
        pts = (vtm*self.spatial_matrix.transpose()).transpose() #Generates a set of points through the transformation matrices

        self.updateAxes()
        dx = self.dataSize
        for i in range (len(self.spatial_matrix)):
            rgb = "#%02x%02x%02x" % (0, 0, 255) #Base Color is blue to differentiate from when color axes has been selected or not
            if (self.color_points != None):
             #Low RGB value is green and gradient slowly increases to more red color
                rgb = "#%02x%02x%02x" % (39.2+(self.color_points[i]*215.8), 210-(self.color_points[i]*210), self.color_points[i]*7)
            if (self.size_points != None):
                #changing size
                dx = self.dataSize*self.size_points[i]

            x = pts[i,0]
            y = pts[i,1]
            circle = self.canvas.create_oval( int(x-dx), int(y-dx), int(x+dx), int(y + dx), tags=(("dtp"+ str(i))), fill=rgb) # Assigns each data point a unique tag
            self.objects.append(circle)

    def buildLinearRegression(self, headers):
        analysisObject = analysis.Analysis()
        lrObject = analysisObject.normalize_columns_separately(headers[0:2],self.dataObject)
        # lrObject = self.dataObject.get_columns(lrBox.getVal())

        zeros = np.matrix(np.zeros(len(lrObject))).transpose()
        ones = np.matrix(np.ones(len(lrObject))).transpose()
        lrObject = np.hstack((lrObject,zeros))  #Add the third column as zeros
        self.spatial_matrix = np.hstack((lrObject,ones))  #Add the fourth column as ones

        vtm =  self.viewObject.build()
        pts = (vtm*self.spatial_matrix.transpose()).transpose()

        for i in range (len(self.spatial_matrix)):
            x = pts[i,0]
            y = pts[i,1]
            dx = self.dataSize
            circle = self.canvas.create_oval( int(x-dx), int(y-dx), int(x+dx), int(y + dx), tags=(("dtp"+ str(i)))) # Assigns each data point a unique tag
            self.objects.append(circle)

        slope, intercept, rvalue, pvalue, stdErr = scipy.stats.linregress(self.preDataObject.get_columns(headers[0:2]))
        dataRange = analysisObject.data_range(headers, self.preDataObject)
        self.linregressObj = [slope, intercept, rvalue, pvalue, stdErr]

        l1 = ((dataRange[0][0] * slope + intercept) - dataRange[1][0])/(dataRange[1][1] - dataRange[1][0])
        l2 = ((dataRange[0][1] * slope + intercept) - dataRange[1][0])/(dataRange[1][1] - dataRange[1][0])


        self.pNM = np.matrix ( #axes , mainly stays fixed
                                    [[0,1],
                                     [l1,l2],
                                      [0,0],
                                      [1,1]])
        pixelCoords = vtm * self.pNM

        x0 = pixelCoords[0,0]
        y0 = pixelCoords[1,0]
        x1 = pixelCoords[0,1]
        y1 = pixelCoords[1,1]
        lrLine = self.canvas.create_line(x0,y0,x1,y1, tags="lrLine", fill="red" )
        self.lineObjects.append(lrLine)

        lrValsBox = dialogs.LinearRegressionVals(self.root, slope, intercept, rvalue)

#---------------o-------------------o--  Update functions --o----------------------o------------------------o

    def updateAxes(self):
        #updates the axes depending on how the view object has been changed
        vtm = self.viewObject.build()           # build the VTM
        pts = (vtm*self.axes.transpose()).transpose()

        self.canvas.coords(self.canvas.find_withtag("xaxis"),pts[0,0],pts[0,1],pts[1,0],pts[1,1])  #finds the objects with xaxis tag --> then updates the points appropriately
        self.canvas.coords(self.canvas.find_withtag("x"),pts[1,0]+10,pts[1,1])

        self.canvas.coords(self.canvas.find_withtag("yaxis"),pts[2,0],pts[2,1],pts[3,0], pts[3,1]) #same as xaxis update
        self.canvas.coords(self.canvas.find_withtag("y"),pts[3,0],pts[3,1]-10)

        self.canvas.coords(self.canvas.find_withtag("zaxis"),pts[4,0],pts[4,1],pts[5,0], pts[5,1]) #same as xaxis update
        self.canvas.coords(self.canvas.find_withtag("z"),pts[5,0],pts[5,1])

        if (self.plotAxes != None):
            #Loops through the x,y and z tags to see if the text needs to be changed to show which axes labels you are using
            self.canvas.itemconfig(self.canvas.find_withtag("x"), text=self.plotAxes[0])
            self.canvas.itemconfig(self.canvas.find_withtag("y"), text=self.plotAxes[1])
            self.canvas.itemconfig(self.canvas.find_withtag("z"), text=self.plotAxes[2])

        if (self.dataObject != None and self.spatial_matrix != None): #Makes sure updatePoints isnt called if data doesnt exist
            self.updatePoints()

        if (self.canvas.find_withtag("lrLine") != None and self.pNM != None):
            pixelCoords = vtm * self.pNM
            x0 = pixelCoords[0,0]
            y0 = pixelCoords[1,0]
            x1 = pixelCoords[0,1]
            y1 = pixelCoords[1,1]
            self.canvas.coords(self.canvas.find_withtag("lrLine"),x0,y0,x1,y1) #same as xaxis update
            self.canvas.itemconfig(self.canvas.find_withtag("lrLine"), fill="red")

        self.zoomLabel.config(text=("Scale Factor ",(round(self.zoomLevel,4)) ))


    def updatePoints(self):
        #updates the points not the axes
        if (self.spatial_matrix != None):
            vtm = self.viewObject.build()
            dataPTS = (vtm*self.spatial_matrix.transpose()).transpose() #same process as update Axes

            dx = self.dataSize
            for i in range (len(self.objects)):
                if (self.size_points != None):
                    dx = self.dataSize*self.size_points[i]
                # print dataPTS, type(dataPTS)
                x = dataPTS[i,0]
                y = dataPTS[i,1]
                self.canvas.coords(self.objects[i],int(x-dx), int(y-dx), int(x+dx), int(y + dx))

    def updatePCAlistBox(self):
        #Updates the display of the PCA List Box
        self.PCAlistbox.delete(0,tk.END)
        for key in self.pcaDataObjects.iterkeys():
            self.PCAlistbox.insert(tk.END, key)

    def updateClassifierListBox(self):
        self.classifierListBox.delete(0, tk.END)
        for key in self.classifierObjects.iterkeys():
            self.classifierListBox.insert(tk.END, key)

    def chooseAxes(self):
        #launches dialog box where user can check data from columns to display on the app
        dbox = dialogs.DialogBox(self.root, self.dataObject.get_headers())
        while (dbox.enoughParams == False and dbox.cancelPress == False):
            #Makes sure the user has checked atleast the x,y and z coordinates and the user has not
            #hit the cancel button
            dbox = dialogs.DialogBox(self.root, self.dataObject.get_headers())
            if (dbox.cancelPress == True):
                return False
        if (dbox.enoughParams == True):
            #makes sure that there are enough parameters for the code to continue executing
            self.plotAxes = dbox.getVal()[:3]
            if (dbox.getVal()[3] != -1):
                self.colorAxes = dbox.getVal()[3:4]
            if (dbox.getVal()[4] != -1):
                self.sizeAxes = dbox.getVal()[4:]
            return True

#---------------o-------------------o--  Menu Building functions --o----------------------o------------------------o

    def buildMenus(self):
        # create a new menu
        menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = menu)

        # create a variable to hold the individual menus
        menulist = []

        # create a file menu
        filemenu = tk.Menu( menu )
        menu.add_cascade( label = "File", menu = filemenu )
        menulist.append(filemenu)

        # create another menu for kicks
        cmdmenu = tk.Menu( menu )
        menu.add_cascade( label = "Command", menu = cmdmenu )
        menulist.append(cmdmenu)

        # menu text for the elements
        # the first sublist is the set of items for the file menu
        # the second sublist is the set of items for the option menu
        menutext = [ [ '-', '-', 'Quit  \xE2\x8C\x98-Q', 'Reset \xE2\x8C\x98-N' , 'Open \xE2\x8C\x98-O' , 'Save \xE2\x8C\x98-S'],  #'-' creates a separator line on the menu
                     [ 'Run Linear Regression', 'Run K-Means Clustering', 'Run K-Means: PCA', 'Train Classifier'],  ]

        # menu callback functions (note that some are left blank,
        # so that you can add functions there if you want).
        # the first sublist is the set of callback functions for the file menu
        # the second sublist is the set of callback functions for the option menu
        menucmd = [ [None, None, self.handleQuit, self.handleReset, self.handleOpen, self.handleSave],
                    [self.handleLinearRegression, self.handleClustering, self.handlePCAClustering, self.trainClassifier] ]

        # build the menu elements and callbacks
        for i in range( len( menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    menulist[i].add_separator()

    # create the canvas object
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy ) #width=self.initDx, height=self.initDy
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
        return

    # build a frame and put controls in it
    def buildControls(self):
        ### Control ###
        # make a control frame on the right
        rightcntlframe = tk.Frame(self.root)
        rightcntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

        # make a separator frame
        sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

        # use a label to set the size of the right panel
        label = tk.Label( rightcntlframe, text="Control Panel", width=20 )
        label.pack( side=tk.TOP, pady=10 )

        colorFrame = tk.Frame(rightcntlframe)
        colorFrame.pack(side=tk.TOP)

        # make a menubutton
        self.colorOption = tk.StringVar( self.root )
        self.colorOption.set("Black")
        colorMenu = tk.OptionMenu( colorFrame, self.colorOption,
                                        "Black", "Blue", "Red", "Green" ) # can add a command to the menu
        colorMenu.pack(side=tk.LEFT)

        # make a button in the frame
        # and tell it to call the handleButton method when it is pressed.
        button = tk.Button( colorFrame, text="Update Color",
                               command=self.handleButton1 )
        button.pack(side=tk.LEFT)  # default side is top   //Packing puts the button on the screen


        '''
            PCA items Below
        '''
        pcaFrame = tk.Frame(rightcntlframe)
        pcaFrame.pack(side=tk.TOP)

        label = tk.Label( pcaFrame, text="------PCA------", width=20 )
        label.pack( side=tk.TOP, pady=10 )

        self.PCAlistbox = tk.Listbox(pcaFrame,selectmode=tk.EXTENDED)
        self.PCAlistbox.pack(side=tk.TOP)

        executePCAButton = tk.Button(pcaFrame, text="Add", command=self.executePCA)
        executePCAButton.pack(side=tk.LEFT)

        deletePCAItem = tk.Button(pcaFrame, text="Delete", command=self.deletePCA)
        deletePCAItem.pack(side = tk.LEFT)

        plotPCAItem = tk.Button(pcaFrame, text="Graph", command=self.graphPCA)
        plotPCAItem.pack(side= tk.LEFT)

        viewPCAItem = tk.Button(rightcntlframe, text="PCA Details", command=self.viewPCA)
        viewPCAItem.pack(side= tk.TOP)

        #End PCA items

        '''
            Classifier Items Below
        '''
        classifierFrame = tk.Frame(rightcntlframe)
        classifierFrame.pack(side=tk.TOP)

        label = tk.Label( classifierFrame, text="------Classifier------", width=20 )
        label.pack( side=tk.TOP, pady=10 )

        self.classifierListBox = tk.Listbox(classifierFrame,selectmode=tk.EXTENDED)
        self.classifierListBox.pack(side=tk.TOP)

        trainClassiferButton = tk.Button(classifierFrame, text="Train", command=self.trainClassifier)
        trainClassiferButton.pack(side=tk.LEFT)

        deleteClassifierButton = tk.Button(classifierFrame, text="Delete", command=self.deleteClassifier)
        deleteClassifierButton.pack(side = tk.LEFT)

        plotClassifier = tk.Button(classifierFrame, text="Graph", command=self.graphClassifier)
        plotClassifier.pack(side= tk.LEFT)

        #End Classifier items

        label = tk.Label( rightcntlframe, text="------General------",width=20 )
        label.pack( side=tk.TOP, pady=10 )

        #Makes a button that calls the command to update the color of all the points on the screen
        updateColorButton = tk.Button(rightcntlframe, text="Build Points", command=self.buildPoints)
        updateColorButton.pack()

        analysisButton = tk.Button(rightcntlframe, text="Analyze", command=self.analyzeCols)
        analysisButton.pack()

        self.analyisLabel = tk.Label(rightcntlframe, fg="blue")
        self.analyisLabel.pack()

        #Makes a button to clear the screen of all its data
        resetButton = tk.Button(rightcntlframe, text = "Reset", command=self.handleReset)
        resetButton.pack(side=tk.BOTTOM)

        self.zoomLabel = tk.Label(rightcntlframe, fg="green")
        self.zoomLabel.pack()

    def setBindings(self):
        # bind mouse motions to the canvas
        self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
        self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
        self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
        self.canvas.bind( '<Shift-Button-1>', self.handleMouseButton3 )
        # self.canvas.bind( '<Shift-Button-1-Motion>', self.handleMouseButton3Motion )
        self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )
        self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<B3-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<Shift-B1-Motion>', self.handleMouseButton3Motion )
        self.canvas.bind( '<Configure>', self.resize)

        # bind command sequences to the root window
        self.root.bind( '<Command-q>', self.handleQuit )
        self.root.bind('<Command-n>', self.handleClear)
        self.root.bind('<Command-o>', self.handleOpen)
        self.root.bind('<Command-s>', self.handleSave)



#---------------o-------------------o-- Data Manipulation Methods Below --o----------------------o------------------------o

    def clearData(self):
        #Clears all the data including data object
        self.dataObject = None
        self.spatial_matrix = None
        self.color_points = None
        self.size_points = None
        self.objects = []
        self.canvas.delete("all")  # Not sure if this is necessarily the way to do it but it does clear the entire screen
        self.buildAxes()

    def clearScreenData(self):
        #clears all the points on the screen
        self.spatial_matrix = None
        self.color_points = None
        self.size_points = None
        self.objects = []
        self.canvas.delete("all")
        self.buildAxes()

#---------------o-------------------o-- PCA Data Methods Below --o----------------------o------------------------o

    def executePCA(self):
        #Execute the PCA Analys on the current Data Object
        if (self.dataObject != None):
            dboxPCA = dialogs.pcaDialogBox(self.root, self.dataObject.get_headers())
            headers = dboxPCA.getVal()  #Get the headers for the PCA Data Object

            if (len(headers)> 0):
                curTime = datetime.datetime.now()
                nameNum = curTime.strftime("%B %d, %Y")  #Creates number based on cur time
                analysisObj = analysis.Analysis()

                pcaName = "Analysis" + str(curTime.minute) + str(curTime.second) #Creates the time

                if len(dboxPCA.name) > 0:
                    pcaName = dboxPCA.name

                pcaDataObj = analysisObj.pca(self.dataObject, headers, normalize = dboxPCA.getNormalize())
                pcaDataObj.update_name(pcaName)
                self.pcaDataObjects[pcaName]= pcaDataObj
                self.updatePCAlistBox()

    def deletePCA(self):
        #Delete the PCA item as stored in the listbox
        curSelection = self.PCAlistbox.curselection()  #List of items to be deleted

        deleteList = []
        for i in range (len(curSelection)):
            deleteList.append(self.PCAlistbox.get(curSelection[i]))

        for i in range(len(deleteList)):
            self.pcaDataObjects.pop(deleteList[i])  #Pop them from the matrix

        self.updatePCAlistBox()

    def graphPCA(self):
        #Graph the PCA Object
        if (len(self.PCAlistbox.curselection()) != 0):
            selectVal = self.PCAlistbox.curselection()[0]  #index value of selected value
            selectedPCA = self.PCAlistbox.get(selectVal)
            self.buildPCA(self.pcaDataObjects.get(selectedPCA) )

    def viewPCA(self):
        #Display the values associated with the PCA object
        if (len(self.PCAlistbox.curselection()) != 0):
            selectVal = self.PCAlistbox.curselection()[0]  #index value of selected value
            selectedPCA = self.PCAlistbox.get(selectVal)

            if selectedPCA != None:
                dialogs.pcaViewDialogBox(self.root,self.pcaDataObjects.get(selectedPCA), self.saveBool)

#---------------o-------------------o-- PCA Data Methods Below --o----------------------o------------------------o

    def trainClassifier(self):
        #Execute the PCA Analys on the current Data Object
        dboxC = dialogs.trainClassiferDialog(self.root)

        if (dboxC.enoughParams == True):
            curTime = datetime.datetime.now()
            nameNum = curTime.strftime("%B %d, %Y")  #Creates number based on cur time
            analysisObj = analysis.Analysis()

            className = "Classifier" + str(curTime.minute) + str(curTime.second) #Creates the time

            trainFile = dboxC.getVals()[0]
            testFile = dboxC.getVals()[1]
            classType = dboxC.getVals()[2]
            kVal = dboxC.getVals()[3]

            print trainFile, testFile, classType, kVal
            classifier = classify.buildClassifier(trainFile, testFile, classType = classType, K=kVal)
            classifier.updateName(className)
            self.classifierObjects[className] = classifier
            self.updateClassifierListBox()

    def deleteClassifier(self):
        #Delete the PCA item as stored in the listbox
        curSelection = self.classifierListBox.curselection()  #List of items to be deleted

        deleteList = []
        for i in range (len(curSelection)):
            deleteList.append(self.classifierListBox.get(curSelection[i]))

        for i in range(len(deleteList)):
            self.classifierObjects.pop(deleteList[i])  #Pop them from the matrix

        self.updateClassifierListBox()

    def graphClassifier(self):
        #Graphs the PCA Vals
        print "Sorry this functionality is currently unavailable"

    def viewCluster(self):
        print "Sorry this functionality is currently unavailable"

        # if (len(self.PCAlistbox.curselection()) != 0):
        #     selectVal = self.PCAlistbox.curselection()[0]  #index value of selected value
        #     selectedPCA = self.PCAlistbox.get(selectVal)
        #
        #     if selectedPCA != None:
        #         dialogs.pcaViewDialogBox(self.root,self.pcaDataObjects.get(selectedPCA), self.saveBool)

#---------------o-------------------o-- Data Analysis Methods Below --o----------------------o------------------------o

    def analyzeCols(self):
        #uses the analyse class to analyse the data the user has selected and displays it
        #on a seperate dialog box
        if (self.plotAxes != None and self.dataObject != None):
            analysisObject = analysis.Analysis()
            axes = self.plotAxes

            #Appends color and size if user has selected that option
            if (self.colorAxes != None):
                axes.append(self.colorAxes[0])
            if (self.sizeAxes != None):
                axes.append(self.sizeAxes[0])

            retList = [analysisObject.mean(axes, self.dataObject),
                    analysisObject.stddev(axes, self.dataObject),
                    analysisObject.data_range(axes, self.dataObject)]
            self.analysisVals = retList #Creates compact list to pass on to analysis object

            aBox = dialogs.AnalysisDialog(self.root, axes,self.analysisVals) #creates an analysis Dialog Box
#---------------o-------------------o-- Handle Events Below --o----------------------o------------------------o
#Most functions are simply as the name suggests
#Some are also functions from the code Bruce handed over

    def handleOpen(self, event=None, plot=False):
        #Handles the open call which asks user which file they would like to load.
        self.clearData()
        fn = tkFileDialog.askopenfilename(parent=self.root,
        title='Choose a data file', initialdir='.' )

        if (fn != ""):
            charList = list(fn)
            count = 0
            for i in reversed(charList):  #This is required since fn returns a full address ie not local address
                if i == '/':  #this splits it up and will only accept data stored within the same directory
                    break
                count += 1
            name = ''.join(charList[len(charList)-count:])
            if (self.dataObject != None):
                self.clearData()
                self.dataObject = data.Data(name)
                self.preDataObject= data.Data(name)
            else:
                self.dataObject = data.Data(name)
                self.preDataObject= data.Data(name)

            if (plot == False):
                return
            else:
                self.buildPoints()

    def handleSave (self, event=None):
        '''
            Saves the canvas object as a post script and adds a number which is a makeup of the
            current time to each file as to avoid overwriting old files.
        '''
        now = datetime.datetime.now()
        curTime = str(now.day)+str(now.hour)+str(now.minute) + str(now.second)
        if (os.path.exists("images") == True):
            self.canvas.postscript(file="images/graphImage"+str(curTime)+".ps", colormode='color')
        else:
            os.mkdir("images",0755)
            self.canvas.postscript(file="images/graphImage"+str(curTime)+".ps", colormode='color')

    def handleQuit(self, event=None):
        print 'Terminating'
        self.root.destroy()

    def handleClear(self, event=None):
        self.clearData()

    def handleReset(self, event=None):
        self.viewObject.reset()
        self.updateAxes()

    def handleButton1(self):
        #Updates the color of the objects stored in the canvas.
      for obj in self.objects:
          self.canvas.itemconfig(obj, fill=self.colorOption.get())

    def handleMouseButton1(self, event):
        self.baseClick = (event.x, event.y)

    def handleMouseButton2(self, event):
        #Creates an oval object at the coordinate specified
        self.baseClick = [event.x,event.y]
        self.baseView = self.viewObject.clone()

    # This is called if the first mouse button is being moved
    def handleMouseButton1Motion(self, event):
        #Mouse button one moves all the data points on the Canvas

        #calculates the difference between last mouse click and current click
        diff = [float(event.x - self.baseClick[0])/float(self.viewObject.screen[0,0]),
         float(event.y - self.baseClick[1])/float(self.viewObject.screen[0,1])]
                # Divide the differential motion (dx, dy) by the screen size (view X, view Y)

        delta = [diff[0]*self.viewObject.extent[0,0], diff[1]*self.viewObject.extent[0,1]] # Multiply the horizontal and vertical motion by the horizontal and vertical extents.

        self.viewObject.vrp  = self.viewObject.vrp + (delta[0] * self.viewObject.u + delta[1]*self.viewObject.vup)
        self.updateAxes()
        self.baseClick = (event.x, event.y)

    def handleMouseButton2Motion(self, event):
        #This is called to rotate the data Points
        del0 = (float(event.x - self.baseClick[0])/(0.5*self.canvas.winfo_screenwidth())*math.pi) #Change to viewObject Screen
        del1 = (float(event.y - self.baseClick[1])/(0.5*self.canvas.winfo_screenheight())*math.pi)

        self.viewObject = self.baseView.clone()
        self.viewObject.rotateVRC(del0,del1)

        #Assign viewObject updates to current View Object fields
        self.updateAxes()

    def handleMouseButton3(self, event):
        #Mouse button three creates points around the point where the user clicked on the canvas
        self.baseClick = (event.x, event.y)
        self.baseExtent = self.viewObject.extent.copy()

    def handleMouseButton3Motion(self, event):
        #Handles the scaling of the screen
        screenHeight = float(self.canvas.winfo_screenheight())
        distanceToTop = (self.baseClick[1])
        scaleFactor = 1.0

        if (event.y > self.baseClick[1]): #zoom out
            percentDiff = float(event.y-self.baseClick[1])/distanceToTop #calculates scale factor as a function of how far away from top it is
            scaleFactor = scaleFactor + percentDiff*2.0
            if scaleFactor < 0.1:
                scaleFactor = 0.1
        else: #Zoom in
            distanceToBot = screenHeight-self.baseClick[1]
            percentDiff = (self.baseClick[1]-event.y)/distanceToBot #opposite of zoom out
            scaleFactor = scaleFactor-percentDiff
            if scaleFactor > 3.0:
                scaleFactor = 3.0
        self.zoomLevel = scaleFactor #updates field so that user can know whats happening
        self.viewObject.extent = self.baseExtent*scaleFactor
        self.updateAxes()

    def handleLinearRegression(self):
        '''
            Handles the Linear regression by first building a 4x4 matrix where the first two
            cols are the independent and dependent variables as selected by the user
        '''
        if (self.dataObject != None):
            lrBox = dialogs.LinearRegressionDialog(self.root,self.dataObject.get_headers())
            self.clearScreenData()#Clear stuff before
            self.buildLinearRegression(lrBox.getVal())
        else:
            print "Please Load a Data Set"

    def handleClustering(self):
        #Handles clustering for data application

        if (self.dataObject != None):
            cBox = dialogs.kmeansDialogBox(self.root, self.dataObject.get_headers())
            if (cBox.cancelPress == False):
                if (cBox.getVal != None):
                    if (cBox.getManhattan()==True):
                        analysisObj = analysis.Analysis()
                        self.kVal = cBox.name

                        headers = cBox.getVal()

                        d = self.dataObject.get_data(headers,self.dataObject.get_num_rows())
                        codebook, codes , error = analysisObj.kmeans(d, headers, self.kVal,manhattan=True)

                        self.dataObject.add_column(np.matrix(codes).T, 'codes', 'code')
                        self.buildPoints()
                    else:
                        analysisObj = analysis.Analysis()
                        self.kVal = cBox.name

                        headers = cBox.getVal()

                        d = self.dataObject.get_data(headers,self.dataObject.get_num_rows())
                        codebook, codes , error = analysisObj.kmeans_numpy(d, headers, self.kVal)

                        self.dataObject.add_column(np.matrix(codes).T, 'codes', 'code')
                        self.buildPoints()
        else:
            print "Please Load a Data Set"

    def handlePCAClustering(self):
        print self.pcaDataObjects
        print self.PCAlistbox.curselection()
        if (bool(self.pcaDataObjects) == True):
            curSelection = self.PCAlistbox.curselection()  #List of items to be deleted
            if (curSelection != None):
                cBox = dialogs.kmeansDialogBox(self.root, self.dataObject.get_headers())
                if (cBox.cancelPress == False):
                    if (cBox.getVal != None):
                        selectVal = self.PCAlistbox.curselection()[0]  #index value of selected value
                        selectedPCA = self.PCAlistbox.get(selectVal)
                        dataObject = self.pcaDataObjects.get(selectedPCA)

                        if (cBox.getManhattan()==True):
                            analysisObj = analysis.Analysis()
                            self.kVal = cBox.name

                            headers = cBox.getVal()

                            d = dataObject.get_data(headers,dataObject.get_num_rows())
                            codebook, codes , error = analysisObj.kmeans(d, headers, self.kVal,manhattan=True)

                            dataObject.add_column(np.matrix(codes).T, 'codes', 'code')
                            self.buildPCA(dataObject)
                        else:
                            analysisObj = analysis.Analysis()
                            self.kVal = cBox.name

                            headers = cBox.getVal()

                            d = dataObject.get_data(headers,dataObject.get_num_rows())
                            codebook, codes , error = analysisObj.kmeans_numpy(d, headers, self.kVal)

                            dataObject.add_column(np.matrix(codes).T, 'codes', 'code')
                            self.buildPCA(dataObject)
            else:
                print "Please select a PCA analysis to Run K mean on"
        else:
            print "Please perform PCA Analysis first"

    def resize(self, event=None):
        '''
            Resizes the screen coords
        '''
        self.viewObject.screen[0,0] = (self.canvas.winfo_width()/3)
        self.viewObject.screen[0,1] = (self.canvas.winfo_height()/2)
        self.updatePoints()
        self.updateAxes()


    def main(self):
        print 'Entering main loop'
        self.root.mainloop()

if __name__ == "__main__":
    dapp = DisplayApp(1200, 675)
    dapp.main()
