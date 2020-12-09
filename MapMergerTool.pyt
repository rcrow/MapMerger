import arcpy
import datetime
import pandas
import os, shutil
import xml.dom.minidom as DOM
#TODO produces errors - needs more work

#######################################################################################################################
#Some functions
def datetimePrint():
    time = datetime.datetime.now() #Get system time
    if len(str(time.month))==1:
        month="0"+str(time.month)
    else:
        month=str(time.month)
    if len(str(time.day)) == 1:
        day = "0" + str(time.day)
    else:
        day = str(time.day)
    if len(str(time.hour)) == 1:
        hour = "0" + str(time.hour)
    else:
        hour = str(time.hour)
    if len(str(time.minute)) == 1:
        minute = "0" + str(time.minute)
    else:
        minute = str(time.minute)
    if len(str(time.second)) == 1:
        second = "0" + str(time.second)
    else:
        second = str(time.second)
    timeDateString = str(time.year) + month + day + "_" + hour + minute + "_" + second
    date = month + "/" + day + "/" + str(time.year)
    timestr = hour + ":" + minute
    return [timeDateString,date,timestr,time]

def intersectFC(FCPath,quadPath,exportPath):
    arcpy.Intersect_analysis(in_features= [FCPath, quadPath],
                             out_feature_class=exportPath,
                             join_attributes="ALL", cluster_tolerance="-1 Unknown", output_type="INPUT")

def NCGMPname(str,num):
    return [str[num:],str[:num]]

def checkAndDeleteOS(path):
    arcpy.env.overwriteOutput = True
    if os.path.isdir(path):
        shutil.rmtree(path)
        arcpy.AddMessage("  " + path +": Exists, Deleted")
    else:
        arcpy.AddMessage("  " + path +": Does Not Exist")

def checkAndDelete(path):
    if arcpy.Exists(path):
        arcpy.AddMessage("  " + path +": Exists, Deleting")
        arcpy.Delete_management(path)
    else:
        arcpy.AddMessage("  " + path +": Does Not Exist")

def checkAndAppend(input,export):
    if arcpy.Exists(input):
        arcpy.AddMessage("Starting to append... ")
        arcpy.Append_management(input,export,"NO_TEST")
        arcpy.AddMessage(input +": Exists, Appended")
    else:
        arcpy.AddMessage(input +": Does Not Exist")

class Toolbox (object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "MapMergerTool"
        self.alias = "MapMergerTool"

        # List of tool classes associated with this toolbox
        self.tools = [mapMerger]

class mapMerger(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MapMerger"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="FC with map info:",
            name="inputAreas",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output Folder:",
            name="folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Output prefix:",
            name="prefix",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="GeMS Toolbox Path:",
            name="gemsToolbox",
            datatype="DEToolbox",
            parameterType="Required",
            direction="Input")

        param4= arcpy.Parameter(
            displayName="Merger Toolbox Path:",
            name="mergerToolbox",
            datatype="DEToolbox",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Build and Dissolve in Overlay Mapping:",
            name="buildOverlayMapping",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Overlay Mapping GDB:",
            name="overlayGDB",
            datatype="DEWorkspace",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Overlay prefix:",
            name="overlayPrefix",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="Overlay mapunit conversion file:",
            name="overlayMapUnitConv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input")

        param9 = arcpy.Parameter(
            displayName="Overlay line conversion file:",
            name="overlayLineConv",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input")

        param10 = arcpy.Parameter(
            displayName="Overlay datasource ID:",
            name="overlayDatasourceID",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param11 = arcpy.Parameter(
            displayName="Crosswalk Overlay Mapping (beta):",
            name="crosswalkNew",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param12 = arcpy.Parameter(
            displayName="Crosswalk file for new mapping:",
            name="crosswalkFile",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input")

        param13 = arcpy.Parameter(
            displayName="Remove Blank Poly from Overlay:",
            name="removeBlank",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param14 = arcpy.Parameter(
            displayName="Rebuild Polygons:",
            name="rebuildPolygons",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param15 = arcpy.Parameter(
            displayName="Remove Interior Line Segments:",
            name="removeInterior",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param16 = arcpy.Parameter(
            displayName="Build Topology:",
            name="buildTopology",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param17 = arcpy.Parameter(
            displayName="Write to a Master GDB:",
            name="writeToMaster",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param18 = arcpy.Parameter(
            displayName="Field name conversion file:",
            name="fieldName",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param19 = arcpy.Parameter(
            displayName="GEMS-style template GDB:",
            name="gemsGDB",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param20 = arcpy.Parameter(
            displayName="Use alternate mapunits:",
            name="altMapUnit",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        params = [param0,param1,param2,param3,param4,
                  param5,param6,param7,param8,param9,param10,
                  param11,param12,param13,
                  param14,param15,param16,param17,param18,param19,param20]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        if parameters[5].value == True:
            parameters[6].enabled = True
            parameters[7].enabled = True
            parameters[8].enabled = True
            parameters[9].enabled = True
            parameters[10].enabled = True
            parameters[11].enabled = True
            parameters[13].enabled = True
        else:
            parameters[6].enabled = False
            parameters[7].enabled = False
            parameters[8].enabled = False
            parameters[9].enabled = False
            parameters[10].enabled = False
            parameters[11].enabled = False
            parameters[13].enabled = False
        if parameters[11].value == True:
            parameters[12].enabled = True
        else:
            parameters[12].enabled = False
        return

    def Parameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        arcpy.AddMessage("Options and Parameters")

        mapAreasFCOrig = parameters[0].valueAsText
        arcpy.AddMessage(" Path to map areas FC: "+ str(mapAreasFCOrig))
        inputFieldNames=['OBJECTID','inputDBPath', 'inputFDSName','inputPrefixLength','listFCsToClip',
                         'exportFDSPrefix','inputPolygons','ConversionTables','LineConversionTables']
        lengthInputFields=len(inputFieldNames)
        exportFolder = parameters[1].valueAsText
        arcpy.AddMessage(" Export folder: " + str(exportFolder))
        exportGDBPrefix = parameters[2].valueAsText
        arcpy.AddMessage(" GBD name: " + str(exportGDBPrefix)+"GeologicMap")
        gemsToolbox = parameters[3].valueAsText
        arcpy.AddMessage(" Path to GEMS toolbox: " + str(gemsToolbox))
        arcpy.ImportToolbox(gemsToolbox)
        mergeToolbox = parameters[4].valueAsText
        arcpy.AddMessage(" Path to separate merger tools toolbox: " + str(mergeToolbox))
        arcpy.ImportToolbox(mergeToolbox)

        arcpy.env.overwriteOutput = True


        #######################################################################################################################
        #Options
        # removeMultiParts = parameters[10].valueAsText
        buildOverlayMapping = parameters[5].valueAsText
        arcpy.AddMessage(" Build Overlap Mapping: " + str(buildOverlayMapping))
        crosswalkNew = parameters[11].valueAsText
        arcpy.AddMessage(" Crosswalk New Mapping: " + str(crosswalkNew))
        removeBlank = parameters[13].valueAsText
        arcpy.AddMessage(" Remove Empty Polygons From New Mapping: " + str(removeBlank))

        rebuildPolygons = parameters[14].valueAsText
        arcpy.AddMessage(" Rebuild Polygons: " + str(rebuildPolygons))
        removeInterior = parameters[15].valueAsText
        arcpy.AddMessage(" Remove Interior Line Segments (e.g. part of original map boundaries): " + str(removeInterior))
        buildTopology = parameters[16].valueAsText
        arcpy.AddMessage(" Build Topology: " + str(buildTopology))
        writeToMaster = parameters[17].valueAsText
        arcpy.AddMessage(" Write to master: " + str(writeToMaster))
        altMapUnit = parameters[20].valueAsText
        arcpy.AddMessage(" Use alternate mapunits: " + str(altMapUnit))

        #######################################################################################################################
        start = datetimePrint()[3]
        timeDateString = datetimePrint()[0]  # Gets time and date to add to export

        arcpy.AddMessage("Current Run: " + timeDateString)

        # Create a new GDB
        # Export names and proj
        if writeToMaster == "true": #"if writeToMaster:" is always true #TODO this change probably has to be made throughout!!!
            exportGDBName = exportGDBPrefix + "MASTER"
            arcpy.AddMessage("Writing to master")
        else:
            exportGDBName = exportGDBPrefix + timeDateString
            arcpy.AddMessage("Appending the date to DB")

        spatialRef = arcpy.Describe(mapAreasFCOrig).spatialReference #Assumes mapAreaFC and mapDBs have the same projection

        exportGDBFullPath = exportFolder + "\\" + exportGDBName + ".gdb"
        if arcpy.Exists(exportGDBFullPath):
            arcpy.AddMessage("GDB already exists")
            arcpy.env.workspace = exportGDBFullPath
            datasets = arcpy.ListDatasets()
            for dataset in datasets:
                checkAndDelete(dataset)
        else:
            arcpy.AddMessage("Creating a new GDB at: " + exportGDBFullPath)
            arcpy.CreateFileGDB_management(out_folder_path=exportFolder,
                                       out_name=exportGDBName,
                                       out_version="CURRENT")

        if buildOverlayMapping == "true":
            print("Building overlays")
            overlayInputDBPath = parameters[6].valueAsText
            arcpy.AddMessage(" Path to overlays DB: "+str(overlayInputDBPath))
            exportOverlayDB = overlayInputDBPath
            overlayPrefix = parameters[7].valueAsText
            arcpy.AddMessage(" Overlay prefix: " + str(overlayPrefix))
            if writeToMaster == "true":
                polyPath = exportOverlayDB + "\\" + "Polys_Master"
                dissPath = exportOverlayDB + "\\" + "Diss_Master"
                #TODO this is probably not the best place for this file
                mapAreasFC = exportOverlayDB+r"\ExtentPolys_Master"
                arcpy.AddMessage("Using MASTER")
            else:
                polyPath = exportOverlayDB + "\\"+"Polys_" + timeDateString
                dissPath = exportOverlayDB + "\\"+"Diss_" + timeDateString
                #TODO this is probably not the best place for this file
                mapAreasFC = exportOverlayDB+ r"\ExtentPolys_" + timeDateString
                arcpy.AddMessage("Not using MASTER")
            if overlayPrefix == None:
                inputOverlayLines = overlayInputDBPath + "\\" + "GeologicMap" + "\\" + "ContactsAndFaults"
                inputOverlayPoints = overlayInputDBPath + "\\" + "GeologicMap" + "\\" + "MapUnitPoints"
                overlayInputFDSName = "GeologicMap"
                overlayInputPrefixLength = 0
            else:
                inputOverlayLines = overlayInputDBPath + "\\" + overlayPrefix + "GeologicMap" + "\\" + overlayPrefix + "ContactsAndFaults"
                inputOverlayPoints = overlayInputDBPath + "\\" + overlayPrefix + "GeologicMap" + "\\" + overlayPrefix + "MapUnitPoints"
                overlayInputFDSName = overlayPrefix + "GeologicMap"
                overlayInputPrefixLength = len(overlayPrefix)
            arcpy.AddMessage(" Path to overlay points: " + str(inputOverlayPoints))
            arcpy.AddMessage(" Path to overlay line: " + str(inputOverlayLines))

            overlayInputPolygons = polyPath
            # TODO the rest of this is hardcoded
            overlayListFCsToClip = "ContactsAndFaults"
            overlayExportFDSPrefix = "NEW"
            overlayConversionTables = parameters[8].valueAsText
            arcpy.AddMessage(" Path to overlays mapunit conversions file: " + str(overlayConversionTables))
            overlayILineConversionTables = parameters[9].valueAsText
            arcpy.AddMessage(" Path to overlays line conversions file: " + str(overlayILineConversionTables))
            overlayIDataSourceID = parameters[10].valueAsText
            arcpy.AddMessage(" Overlay datasource ID: " + str(overlayIDataSourceID))

            if crosswalkNew == "true":
                txtFile = parameters[12].valueAsText
                arcpy.AddMessage(" Path to crosswalk file: " + str(txtFile))
                arcpy.AddMessage("Crosswalking the new mapping")
                arcpy.AttributeByKeyValues_GEMS(overlayInputDBPath, txtFile, True)
            else:
                arcpy.AddMessage(" not crosswalking new")

            arcpy.FeatureToPolygon_management(in_features=inputOverlayLines,
                                              out_feature_class=polyPath,
                                              cluster_tolerance="", attributes="ATTRIBUTES",
                                              label_features=inputOverlayPoints)

            if removeBlank == "true":
                print("Removing blank polygons from new mapping")
                tempLayer = "tempLayer"
                arcpy.MakeFeatureLayer_management(polyPath, tempLayer)
                arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION",
                                                        "mapunit = ''")
                if int(arcpy.GetCount_management(tempLayer).getOutput(0)) > 0:
                    arcpy.DeleteFeatures_management(tempLayer)

            if altMapUnit == "true":
                arcpy.AddMessage("Switching Fields in the new polygons")
                arcpy.AddField_management(polyPath, "tempMapUnit", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED",
                                          "")
                arcpy.CalculateField_management(polyPath, "tempMapUnit", "!mapunit!", "PYTHON_9.3", "")
                arcpy.CalculateField_management(polyPath, "mapunit", "!mapunit2!", "PYTHON_9.3", "")
                arcpy.CalculateField_management(polyPath, "mapunit2", "!tempMapUnit!", "PYTHON_9.3", "")
                arcpy.DeleteField_management(polyPath, "tempMapUnit")
            else:
                arcpy.AddMessage("Not switching Fields in the new polygons")

            arcpy.Dissolve_management(in_features=polyPath,
                                      out_feature_class=dissPath,
                                      dissolve_field="", statistics_fields="", multi_part="MULTI_PART",
                                      unsplit_lines="DISSOLVE_LINES")

            arcpy.Update_analysis(in_features=mapAreasFCOrig, update_features=dissPath,
                                  out_feature_class=mapAreasFC,
                                  keep_borders="BORDERS", cluster_tolerance="")

            fields = ['inputDBPath', 'inputFDSName', 'inputPrefixLength','listFCsToClip','exportFDSPrefix','inputPolygons','ConversionTables','LineConversionTables','DataSourceID']
            with arcpy.da.UpdateCursor(mapAreasFC, fields) as cursor:
                for row in cursor:
                    arcpy.AddMessage(row[0])
                    if row[0] == None or row[0]=="":
                        arcpy.AddMessage("Updating feature with no attributes...")
                        row[0] = overlayInputDBPath
                        row[1] = overlayInputFDSName
                        row[2] = overlayInputPrefixLength
                        row[3] = overlayListFCsToClip
                        row[4] = overlayExportFDSPrefix
                        row[5] = overlayInputPolygons
                        row[6] = overlayConversionTables
                        row[7] = overlayILineConversionTables
                        row[8] = overlayIDataSourceID
                        cursor.updateRow(row)
                    else:
                        arcpy.AddMessage("Nothing is blank")
        else:
            arcpy.AddMessage("Not Building Overlap Mapping")
            mapAreasFC = mapAreasFCOrig

        listHeaderNames = ['NewMapUnit']
        listFinalMapUnits = []
        writer = pandas.ExcelWriter(exportFolder+r'\\'+exportGDBPrefix+timeDateString+'.xlsx')

        listExportPrefixes = []
        cursor = arcpy.da.SearchCursor(mapAreasFC, inputFieldNames)
        count=1
        for row in cursor:
            arcpy.AddMessage("\n\r--------------------------------")
            arcpy.AddMessage("Map area number: " + str(count))
            inputDBPath = row[1]
            inputFDSName = row[2]
            inputPrefixLength = row[3]
            listFCsToClip = row[4].split() #Turns a space deliminated list of string into a list data type
            arcpy.AddMessage(listFCsToClip)
            exportFDSPrefix = row[5]
            listHeaderNames.append(exportFDSPrefix)
            listExportPrefixes.append(exportFDSPrefix)
            inputPolygons = row[6]
            conversionTable = row[7]
            arcpy.AddMessage(conversionTable)
            lineConversionTable = row[8]
            arcpy.AddMessage(lineConversionTable)
            arcpy.AddMessage("  Export Map area / prefix: "+ exportFDSPrefix)
            inputFDSFullPath = inputDBPath + "\\" + inputFDSName
            arcpy.AddMessage("  FDS to be copied: " + inputFDSFullPath)
            inputCoreFDSName = inputFDSName.split(".")[-1] # Cut off anything before the last period
            #arcpy.AddMessage(inputCoreFDSName)
            prefixInitials = NCGMPname(inputCoreFDSName, inputPrefixLength)[1]
            arcpy.AddMessage("  Input prefix name: " + prefixInitials)

            arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                                  out_name=exportFDSPrefix + "_" + "GeologicMap",
                                                  spatial_reference=spatialRef) # Create a FDS
            exportFDSFullPath = exportGDBFullPath + "\\" + exportFDSPrefix + "_" + "GeologicMap"

            arcpy.AddMessage("  Created a new FDS at: " + exportFDSFullPath)
            #Copy Quad to new FDS
            #Copy Quad to new FDS
            Quad = exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "QuadBoundary"
            arcpy.env.workspace = exportFDSFullPath
            arcpy.AddMessage("  Quad: " + Quad)
            #arcpy.AddMessage("  ID: "+str(row[0]))
            tempLayer = arcpy.MakeFeatureLayer_management(mapAreasFC, "MapArea_lyr")
            arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION", "OBJECTID="+str(row[0]))
            arcpy.CopyFeatures_management(tempLayer,Quad)
            arcpy.Delete_management(tempLayer)
            arcpy.env.overwriteOutput = True

            arcpy.AddMessage("\n\rvvvvvvvvvvvvvvvvvvv")
            arcpy.AddMessage("Starting clipping stuff...")
            arcpy.env.workspace = inputFDSFullPath
            arcpy.AddMessage("  Workspace is: " + arcpy.env.workspace)
            listFCsInInput = arcpy.ListFeatureClasses("*")
            #arcpy.AddMessage(listFCsInInput)
            arcpy.env.workspace = exportFDSFullPath
            arcpy.AddMessage("  Workspace is: " + arcpy.env.workspace)
            for fcininput in listFCsInInput:
                genericFileName = NCGMPname(fcininput.split(".")[-1], inputPrefixLength)[0]
                arcpy.AddMessage("     ####################")
                arcpy.AddMessage("     Part: "+genericFileName)
                arcpy.AddMessage("     Input feature class: " + fcininput)
                if genericFileName in listFCsToClip:
                    importpath = inputFDSFullPath + "\\" + fcininput
                    exportdestination = exportFDSFullPath + "\\" + exportFDSPrefix + "_" + genericFileName
                    arcpy.AddMessage("     Import Path: " + importpath)
                    # ("     Check if input exists: " + str(arcpy.Exists(importpath)))
                    arcpy.AddMessage("     Export Destination: " + exportdestination)
                    # arcpy.AddMessage("     Check if export exists: " + str(arcpy.Exists(exportdestination)))

                    arcpy.AddMessage("     Using Clip")
                    arcpy.Clip_analysis(
                        in_features=importpath,
                        clip_features=Quad,
                        out_feature_class=exportdestination,
                        # if you export this to the same FDS the feature links seem to be preserved
                        cluster_tolerance="")
                    arcpy.AddMessage("     Finished clipping: " + genericFileName)
                    if genericFileName == "ContactsAndFaults":
                        # Add Quad and build polygons REQUIRES CONTACTS AND FAULTS
                        quadLine = exportFDSFullPath + "\\" + "quadLines"
                        quadLineParts = exportFDSFullPath + "\\" + "quadLinesParts"
                        # Convert the polys to lines
                        arcpy.FeatureToLine_management(Quad, quadLineParts)
                        arcpy.MultipartToSinglepart_management(quadLineParts,quadLine) #This is needed for maps with non contiguous area
                        arcpy.Delete_management(quadLineParts)
                        arcpy.AddField_management(quadLine, "Symbol", "TEXT")
                        # This will change the Symbol of everything in the FC to 31.08
                        with arcpy.da.UpdateCursor(quadLine, ["Symbol"]) as cursor:
                            for row in cursor:
                                row[0] = '31.08'  # Map neatline
                                cursor.updateRow(row)
                        arcpy.AddMessage(exportdestination)
                        arcpy.AddMessage(quadLine)
                        arcpy.AddMessage(exportFDSFullPath + "\\" + "ContactsAndFaults_temp")
                        arcpy.Merge_management([exportdestination, quadLine],
                                               exportFDSFullPath + "\\" + "ContactsAndFaults_temp")
                        arcpy.Delete_management(quadLine)
                        arcpy.MultipartToSinglepart_management(
                            in_features=exportFDSFullPath + "\\" + "ContactsAndFaults_temp",
                            out_feature_class=exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "ContactsAndFaultsClean")
                        arcpy.Delete_management(exportFDSFullPath + "\\" + "ContactsAndFaults_temp")
                        arcpy.Delete_management(exportdestination)
                        arcpy.Rename_management(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "ContactsAndFaultsClean",
                                                exportdestination)
                else:
                    arcpy.AddMessage("     Ignoring: " + genericFileName)

            arcpy.AddMessage("\n\rvvvvvvvvvvvvvvvvvvv")
            arcpy.AddMessage("Clipping Polygons")
            arcpy.Clip_analysis(
                in_features=inputPolygons,
                clip_features=Quad,
                out_feature_class=exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys",
                cluster_tolerance="")

            arcpy.AddMessage("\n\rvvvvvvvvvvvvvvvvvvv")
            arcpy.AddMessage("Starting to rename stuff...")
            listfcsforrenaming = arcpy.ListFeatureClasses("*", "All")
            arcpy.AddMessage(listfcsforrenaming)
            for fctorename in listfcsforrenaming:
                fcpath = exportFDSFullPath + "\\" + fctorename
                arcpy.AddMessage("  Feature Class for field renaming: " + fctorename)
                fieldsToRename = arcpy.ListFields(fcpath)
                fieldNamesFiles=parameters[18].valueAsText
                arcpy.AddMessage(" Path to fieldnames file: " + str(fieldNamesFiles))
                dfRename = pandas.read_excel(fieldNamesFiles) #TODO instead of requiring a separate file add these field names to the code
                gemsFieldNames = dfRename['GEMSField'].values.tolist()#TODO Move this pandas stuff out of the loop
                sdeFieldNames = dfRename['sdeField'].values.tolist()
                for numb, field in enumerate(fieldsToRename): #TODO no need to enumerate
                    arcpy.AddMessage(field.name)
                    if field.name in sdeFieldNames:
                        newfieldname = gemsFieldNames[sdeFieldNames.index(field.name)]
                        arcpy.AlterField_management(fcpath, field.name, "zzzz") #Without this simple case changes are not recognized
                        arcpy.AlterField_management(fcpath,"zzzz",newfieldname)
                        arcpy.AddMessage("   " + field.name + " renamed to: " + newfieldname)
                    else:
                        arcpy.AddMessage("   Did not need to rename: "+ field.name)

            #Create Frequency Tables
            arcpy.Frequency_analysis(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys",exportGDBFullPath +"\\"+exportFDSPrefix +"_" + "MapUnits", "mapunit")

            arcpy.AddMessage('Starting mapunit remapping')
            arcpy.AddMessage('  Conversion table:' + conversionTable)
            df = pandas.read_excel(conversionTable)
            prevUnits = df['previous map unit'].values.tolist()
            #TODO this is where you would add an alt mapunit option

            if altMapUnit == "true":
                newUnits = df['alt map unit'].values.tolist()
                arcpy.AddMessage("Using alternate mapunits")
            else:
                newUnits = df['new map unit'].values.tolist()
                arcpy.AddMessage("Not using alternate mapunits")

            if len(arcpy.ListFields(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys","OrigUnit"))==0:
                arcpy.AddField_management(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys","OrigUnit","TEXT")
            with arcpy.da.UpdateCursor(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys", ['MapUnit','OrigUnit']) as cursor:
                listPrevUnits=[]
                for num, row in enumerate(cursor):
                    unit = row[0]
                    if unit in prevUnits:
                        index = prevUnits.index(unit)
                        row[0] = newUnits[index]
                        if newUnits[index] not in listFinalMapUnits:
                            listFinalMapUnits.append(newUnits[index])
                        sumIndex = listFinalMapUnits.index(newUnits[index])
                        while sumIndex > len(listPrevUnits)-1:
                            listPrevUnits.append([])
                        else:
                            if len(listPrevUnits[sumIndex]) == 0:
                                listPrevUnits[sumIndex]=[unit]
                            elif unit not in listPrevUnits[sumIndex]:
                                listPrevUnits[sumIndex].append(unit)
                        row[1] = str(unit)
                        arcpy.AddMessage("   Switching "+ str(unit) + " to: " +str(newUnits[index]))
                    else:
                        arcpy.AddMessage('   No mapunit change needed for: '+ str(unit))
                        if unit not in listFinalMapUnits:
                            listFinalMapUnits.append(unit)
                        sumIndex = listFinalMapUnits.index(unit)
                        while sumIndex > len(listPrevUnits)-1:
                            listPrevUnits.append([])
                        else:
                            if len(listPrevUnits[sumIndex]) == 0:
                                listPrevUnits[sumIndex]=[unit]
                            elif unit not in listPrevUnits[sumIndex]:
                                listPrevUnits[sumIndex].append(unit)
                        #Need to add unit even to prev unit list even if not changed
                    cursor.updateRow(row)
                for idx, units in enumerate(listPrevUnits):
                    listPrevUnits[idx] = ', '.join(units)
                pandas.DataFrame([listPrevUnits]).T.to_excel(writer, 'Sheet1', header=False, index=False, startrow=1,
                                                                     startcol=count)
            count = count+1

            arcpy.AddMessage('Starting line remapping')
            arcpy.AddMessage('  Conversion table:' + lineConversionTable)
            dfl = pandas.read_excel(lineConversionTable)
            prevLines = dfl['previous line symbol'].values.tolist()
            arcpy.AddMessage(prevLines)
            newLines = dfl['new line symbol'].values.tolist()
            with arcpy.da.UpdateCursor(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "ContactsAndFaults",['Symbol']) as cursorl:
                for num, rowl in enumerate(cursorl):
                    line = rowl[0]
                    if line in prevLines:
                        indexl = prevLines.index(line)
                        rowl[0] = newLines[indexl]
                        cursorl.updateRow(rowl)
                        arcpy.AddMessage("   Switching " + str(line) + " to: " + str(newLines[indexl]))

        header = pandas.DataFrame(listHeaderNames)
        theader = header.T
        theader.to_excel(writer, 'Sheet1', header=False, index=False)
        pandas.DataFrame([listFinalMapUnits]).T.to_excel(writer, 'Sheet1', header=False, index=False, startrow=1,startcol=0)

        writer.save()
        arcpy.AddMessage("\n\rvvvvvvvvvvvvvvvvvvv")
        arcpy.AddMessage("Start merging the maps...")
        arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                              out_name="MergedGeologicMap",
                                              spatial_reference=spatialRef)  # Create a FDS
        exportMergedFDSFullPath = exportGDBFullPath + "\\" + "MergedGeologicMap"
        arcpy.AddMessage("  Created a new FDS at: " + exportMergedFDSFullPath)
        arcpy.AddMessage(listExportPrefixes)

        #TODO create this list based on what was already created earlier
        listFCsToMerge = ["MapUnitPolys","ContactsAndFaults","OrientationPoints"]
        gemsGDB = parameters[19].valueAsText
        arcpy.AddMessage(" Path to GEMS template GDB: " + str(gemsGDB))
        listFCTemplatesToMerge = [gemsGDB+"\GeologicMap\MapUnitPolys",
                                  gemsGDB+"\GeologicMap\ContactsAndFaults",
                                  gemsGDB+"\GeologicMap\OrientationPoints"]

        for cnt, fcToMerge in enumerate(listFCsToMerge):
            arcpy.CreateFeatureclass_management(out_path=exportMergedFDSFullPath,
                                                out_name=fcToMerge+"_temp",
                                                geometry_type=arcpy.Describe(listFCTemplatesToMerge[cnt]).shapeType,
                                                template=listFCTemplatesToMerge[cnt])
            mergedFCPath = exportMergedFDSFullPath + "\\" + fcToMerge + "_temp"
            for mapPrefix in listExportPrefixes:
                checkAndAppend(exportGDBFullPath + "\\" + mapPrefix + "_"+ "GeologicMap" + "\\" +mapPrefix+ "_" + fcToMerge,
                               mergedFCPath)
        arcpy.AddMessage("Finished with all the appending...")
        #Merge the adjacent polygons based on mapunit
        # arcpy.Dissolve_management(in_features=exportMergedFDSFullPath + "\\" + "MapUnitPolys_temp",
        #                           out_feature_class=exportMergedFDSFullPath + "\\" + "MapUnitPolys",
        #                           dissolve_field="MapUnit", statistics_fields="",
        #                           multi_part="SINGLE_PART",
        #                           unsplit_lines="DISSOLVE_LINES")

        arcpy.env.overwriteOutput = True
        arcpy.dissolveAndConcatenate_MergerTools(polysToDissolve=exportMergedFDSFullPath + "\\" + "MapUnitPolys_temp",
                                                 gdb=exportGDBFullPath,
                                                 output=exportMergedFDSFullPath + "\\" + "MapUnitPolys")

        arcpy.AddMessage("Finished the dissolving...")
        #arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "MapUnitPolys_temp")
        ##Delete the contacts and faults that are no longer needed
        #Can't remember exactly why I added the unsplit - no required but would fix pseudonodes
        arcpy.UnsplitLine_management(in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp",
                                     out_feature_class=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2",
                                     dissolve_field="Type;IsConcealed;LocationConfidenceMeters;ExistenceConfidence;IdentityConfidence;Symbol;Label;DataSourceID;Notes",
                                     statistics_fields="")
        arcpy.AddMessage("Finished the unsplitting the lines...")
        #This intersects all the feature with themselves
        arcpy.FeatureToLine_management(in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2",
                                       out_feature_class=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
                                       cluster_tolerance="", attributes="ATTRIBUTES")
        #arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp")
        #arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2")
        arcpy.AddMessage("Finished the feature to line...")
        arcpy.MakeFeatureLayer_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults", 'ContactAndFaults_lyr')
        arcpy.SelectLayerByLocation_management(in_layer='ContactAndFaults_lyr',
                                               select_features=exportMergedFDSFullPath + "\\" + "MapUnitPolys",
                                               overlap_type='SHARE_A_LINE_SEGMENT_WITH',
                                               invert_spatial_relationship='INVERT')
        arcpy.AddMessage("Finished the select by location...")
        arcpy.SelectLayerByAttribute_management(in_layer_or_view='ContactAndFaults_lyr',
                                                selection_type='SUBSET_SELECTION',
                                                where_clause='Symbol NOT LIKE \'02%\'') #

        arcpy.DeleteFeatures_management('ContactAndFaults_lyr')
        arcpy.DeleteIdentical_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults",["Shape","Symbol"])

        if removeInterior == "true":
            arcpy.removeInteriorMapBoundaries_MergerTools(lines=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
                                                          gdb=exportGDBFullPath)
        else:
            arcpy.AddMessage("Don't remove interiors")

        if rebuildPolygons == "true":
            arcpy.Select_analysis(exportMergedFDSFullPath + "\\" + "MapUnitPolys", exportMergedFDSFullPath + "\\" + "MapUnitPolys_NotTiny", '"Shape_Area" > 10')
            arcpy.AddMessage("Creating centroid points...")
            arcpy.FeatureToPoint_management(in_features=exportMergedFDSFullPath + "\\" + "MapUnitPolys_NotTiny",
                                            out_feature_class=exportMergedFDSFullPath + "\\" + "MapUnitPoints",
                                            point_location="INSIDE")
            arcpy.AddMessage("Rebuidling Polygons")
            arcpy.FeatureToPolygon_management(
                in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
                out_feature_class=exportMergedFDSFullPath + "\\" + "MapUnitPolys_rebuilt",
                cluster_tolerance="", attributes="ATTRIBUTES",
                label_features=exportMergedFDSFullPath + "\\" + "MapUnitPoints")
        else:
            arcpy.AddMessage("Not rebuilding polygons")

        if buildTopology == "true":
            arcpy.AddMessage("Building Topology")
            topology = arcpy.CreateTopology_management(exportMergedFDSFullPath, "Topology", in_cluster_tolerance="")
            arcpy.AddFeatureClassToTopology_management(topology, exportMergedFDSFullPath + "\\" + "MapUnitPolys", xy_rank="1", z_rank="1")
            arcpy.AddFeatureClassToTopology_management(topology, exportMergedFDSFullPath + "\\" + "ContactsAndFaults", xy_rank="1", z_rank="1")
            arcpy.AddRuleToTopology_management(topology, rule_type="Must Not Have Gaps (Area)",
                                               in_featureclass=exportMergedFDSFullPath + "\\" + "MapUnitPolys",
                                               subtype="", in_featureclass2="#", subtype2="")
            arcpy.AddRuleToTopology_management(topology, rule_type="Must Be Covered By Boundary Of (Line-Area)",
                                               in_featureclass=exportMergedFDSFullPath + "\\" + "ContactsAndFaults", subtype="",
                                               in_featureclass2=exportMergedFDSFullPath + "\\" + "MapUnitPolys", subtype2="")
            arcpy.ValidateTopology_management(topology)
            arcpy.ExportTopologyErrors_management(
                in_topology=topology,
                out_path=exportMergedFDSFullPath,
                out_basename="TopologyErrors")
        else:
            arcpy.AddMessage("Not building topology")

        #TODO add these as options?
        arcpy.AddMessage("Calculating Labels")
        arcpy.calcLabels_MergerTools(fc=exportMergedFDSFullPath + "\\" + "MapUnitPolys")
        arcpy.AddMessage("Simplifing Concenations")
        arcpy.simpConcat_MergerTools(fc=exportMergedFDSFullPath + "\\" + "MapUnitPolys")
        arcpy.AddMessage("Copying MapUnit to Symbol")
        arcpy.CalculateField_management(in_table=exportMergedFDSFullPath + "\\" + "MapUnitPolys",
                                        field="Symbol", expression="!MapUnit!",
                                        expression_type="PYTHON_9.3", code_block="")


        end = datetimePrint()[3]
        elapsed = end-start
        arcpy.AddMessage("Elapsed time: "+str(elapsed))

        arcpy.env.overwriteOutput = False
