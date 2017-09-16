import data
import analysis
import datetime


# dataObject = data.Data('data_noisy.csv')
# analysisObject = analysis.Analysis()
# print analysisObject.linear_regression(dataObject,["X0","X1"],["Y"])

dataFiles = ["lrTest2.csv","data_good.csv","data_noisy.csv"]
dataObject = data.Data("simplifiedData.csv")
analysisObject = analysis.Analysis()
analysisObject.linear_regression(dataObject,["Burglary","Arson"],["Population"],saveFile = True)

# print analysisObject.data_range(['thing1','thing3'], dataObject)
# print analysisObject.mean(['thing1','thing3'],dataObject)
# print analysisObject.stddev(['thing1','thing3'],dataObject)
# print analysisObject.normalize_columns_separately(['thing1','thing3'],dataObject)
# print "Different "
# print analysisObject.normalize_columns_together(['thing1','thing3'],dataObject)

# print dataObject.get_dates()
# print analysisObject.data_range(["numberstuff"],dataObject)
# print analysisObject.stddev(["numberstuff"],dataObject)
# print analysisObject.normalize_columns_together(["numberstuff"],dataObject)
# print " Different "
# print analysisObject.normalize_columns_separately(["numberstuff"],dataObject)

# print analysisObject.data_range(['bad','places'], dataObject)
# print analysisObject.mean(['bad','places'],dataObject)
# print analysisObject.stddev(['bad','places'],dataObject)
# print analysisObject.normalize_columns_separately(['bad','places'],dataObject)
# print "Different "
# print analysisObject.normalize_columns_together(['bad','places'],dataObject)


# print "Data Range = ", analysisObject.data_range(['Population','Robbery'], dataObject)
# print "Mean = ", analysisObject.mean(['Population','Robbery'],dataObject)
# print "Standard Deviation = ", analysisObject.stddev(['Population','Robbery'],dataObject)
# print "Variance = ", analysisObject.var(["Population", "Robbery"], dataObject)
# print "Median = ", analysisObject.median(["Population", "Robbery"], dataObject)

# print analysisObject.normalize_columns_separately(['Population','Robbery'],dataObject)
# print "Different "
# print analysisObject.normalize_columns_together(['Population','Robbery'],dataObject)
