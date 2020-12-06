import arcpy
import datetime
import pandas
import os, shutil
import xml.dom.minidom as DOM

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
        print("  " + path +": Exists, Deleted")
    else:
        print("  " + path +": Does Not Exist")

def checkAndDelete(path):
    if arcpy.Exists(path):
        print("  " + path +": Exists, Deleting")
        arcpy.Delete_management(path)
    else:
        print("  " + path +": Does Not Exist")

def checkAndAppend(input,export):
    if arcpy.Exists(input):
        print("Starting to append... ")
        arcpy.Append_management(input,export,"NO_TEST")
        print(input +": Exists, Appended")
    else:
        print(input +": Does Not Exist")

project = "GRCA_River"

if project=="Blythe":
    mapAreasFCOrig = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\MergerExtents.gdb\Extents\ExtentPolys_PublishedMapping_20200507_1"
if project=="GRCA_All":
    mapAreasFCOrig = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps\MergedMaps.gdb\Extents100k\ExtentPolys"
if project == "GRCA_River":
    mapAreasFCOrig = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps\MergedMaps.gdb\Extents100k\ExtentPolys_5kmBuffer"
if project == "Piute":
    mapAreasFCOrig = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\MergerExtents.gdb\Extents\ExtentPolys_20200222_2"
if project == "DEMO":
    mapAreasFCOrig =r"\\igswzcwwgsrio\loco\Team\Crow\_Python\MapMerger\DemoMaps\Extents.gdb\ExtentPolys"

inputFieldNames=['OBJECTID','inputDBPath', 'inputFDSName','inputPrefixLength','listFCsToClip',
                 'exportFDSPrefix','inputPolygons','ConversionTables','LineConversionTables']
lengthInputFields=len(inputFieldNames)

if project=="Blythe":
    exportFolder = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\MergedMaps"
if project=="GRCA_River":
    exportFolder = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps"
if project == "GRCA_All":
    exportFolder = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps"
if project == "Piute":
    exportFolder = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\MergedMaps"
if project == "DEMO":
    exportFolder = r"\\igswzcwwgsrio\loco\Team\Crow\_Python\MapMerger\DemoOutput"

if project=="Blythe":
    exportGDBPrefix = "PARKER_ALL_"
if project == "GRCA_All":
    exportGDBPrefix = "GRANDCANYON_ALL_"
if project == "GRCA_River":
    exportGDBPrefix = "GRANDCANYON_"
if project == "Piute":
    exportGDBPrefix = "CR_PIUTE_"
if project == "DEMO":
    exportGDBPrefix = "DEMO_"

arcpy.ImportToolbox(r".\MergerTools.pyt")
arcpy.ImportToolbox(r"\\igswzcwwgsrio\loco\Team\Crow\_Python\GEMS_Tools\GeMS_ToolsArc105.tbx")

#######################################################################################################################
#Options
removeMultiParts = True
arcpy.env.overwriteOutput = True
buildOverlayMapping = True #True for PiuteValley #False for Parker right now
removeBlank = True
crosswalkNew = True #Testing this on 20200519
rebuildPolygons = True #True for PiuteValley
writeToMaster = True
removeInterior = True
renameAsMaster = False #Does not work all the time
exportToAGOL = False #Does not work within this script but works by itself
buildTopology = True

#######################################################################################################################
start = datetimePrint()[3]
timeDateString = datetimePrint()[0]  # Gets time and date to add to export
print("Current Run: " + timeDateString)

# Create a new GDB
# Export names and proj
if writeToMaster:
    exportGDBName = exportGDBPrefix + "MASTER"
else:
    exportGDBName = exportGDBPrefix + timeDateString

spatialRef = arcpy.Describe(mapAreasFCOrig).spatialReference #Assumes mapAreaFC and mapDBs have the same projection

exportGDBFullPath = exportFolder + "\\" + exportGDBName + ".gdb"
if arcpy.Exists(exportGDBFullPath):
    print("GDB already exists")
    arcpy.env.workspace = exportGDBFullPath
    datasets = arcpy.ListDatasets()
    for dataset in datasets:
        checkAndDelete(dataset)
else:
    print("Creating a new GDB at: " + exportGDBFullPath)
    arcpy.CreateFileGDB_management(out_folder_path=exportFolder,
                               out_name=exportGDBName,
                               out_version="CURRENT")

if buildOverlayMapping:
    if project == "Blythe":
        inputOverlayLines = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\NewRSCMapping.gdb\RSCGeologicMap\RSCContactsAndFaults"
        inputOverLayPoints = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\NewRSCMapping.gdb\RSCGeologicMap\RSCMapUnitPoints"
        exportOverlayDB = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\NewRSCMapping.gdb"
        if writeToMaster:
            polyPath = exportOverlayDB + "\\" + "Polys_Master"
            dissPath = exportOverlayDB + "\\" + "Diss_Master"
            mapAreasFC = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\MergerExtents.gdb\Extents\ExtentPolys_Master"
        else:
            polyPath = exportOverlayDB + "\\"+"Polys_" + timeDateString
            dissPath = exportOverlayDB + "\\"+"Diss_" + timeDateString
            mapAreasFC = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\MergerExtents.gdb\Extents\ExtentPolys_" + timeDateString
        overlayInputDBPath = r"\\igswzcwwgsrio\loco\GeologicMaps_InProgress\ParkerIntermediateScale\NewRSCMapping.gdb"
        overlayInputFDSName = "RSCGeologicMap"
        overlayInputPrefixLength = 3
        overlayListFCsToClip = "ContactsAndFaults"
        overlayExportFDSPrefix = "NEW"
        overlayInputPolygons = polyPath
        overlayConversionTables = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\ConversionTables\TEST_conversions.xlsx"
        overlayILineConversionTables = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\ConversionTables\TEST_LineConversions.xlsx"
        overlayIDataSourceID = "this study"

    if project == "Piute":
        inputOverlayLines = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\NewRSCMapping.gdb\RSCGeologicMap\RSCContactsAndFaults"
        inputOverLayPoints = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\NewRSCMapping.gdb\RSCGeologicMap\RSCMapUnitPoints"
        exportOverlayDB = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\NewMappingPolys.gdb"
        if writeToMaster:
            polyPath = exportOverlayDB + "\\" + "Polys_Master"
            dissPath = exportOverlayDB + "\\" + "Diss_Master"
            mapAreasFC = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\MergerExtents.gdb\Extents\ExtentPolys_Master"
        else:
            polyPath = exportOverlayDB + "\\"+"Polys_" + timeDateString
            dissPath = exportOverlayDB + "\\"+"Diss_" + timeDateString
            mapAreasFC = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\MergerExtents.gdb\Extents\ExtentPolys_" + timeDateString
        overlayInputDBPath = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\NewRSCMapping.gdb"
        overlayInputFDSName = "RSCGeologicMap"
        overlayInputPrefixLength = 3
        overlayListFCsToClip = "ContactsAndFaults"
        overlayExportFDSPrefix = "NEW"
        overlayInputPolygons = polyPath
        overlayConversionTables = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\ConversionTables\MESQLAKE_conversions.xlsx"
        overlayILineConversionTables = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\ConversionTables\TEST_LineConversions.xlsx"
        overlayIDataSourceID = "this study"

    if project == "GRCA_River" or project == "GRCA_All":
        inputOverlayLines = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\NewGrandCanyonMapping.gdb\GeologicMap\ContactsAndFaults"
        inputOverLayPoints = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\NewGrandCanyonMapping.gdb\GeologicMap\MapUnitPoints"
        exportOverlayDB = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\NewGrandCanyonMapping.gdb" #FDS okay? (THIS IS EXPORTING THE POLYS TO THE SAME GDB)
        if writeToMaster:
            polyPath = exportOverlayDB + "\\" + "Polys_Master"
            dissPath = exportOverlayDB + "\\" + "Diss_Master"
            mapAreasFC = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps\MergedMaps.gdb\Extents100k\ExtentPolys_Master"
        else:
            polyPath = exportOverlayDB + "\\"+"Polys_" + timeDateString
            dissPath = exportOverlayDB + "\\"+"Diss_" + timeDateString
            mapAreasFC = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\MergedMaps\MergedMaps.gdb\Extents100k\ExtentPolys_" + timeDateString
        overlayInputDBPath = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\NewGrandCanyonMapping.gdb"
        overlayInputFDSName = "GeologicMap"
        overlayInputPrefixLength = 0
        overlayListFCsToClip = "ContactsAndFaults"
        overlayExportFDSPrefix = "NEW"
        overlayInputPolygons = polyPath
        overlayConversionTables = r"\\igswzcwwgsrio\loco\Team\Crow\GrandCanyon_RiverMap\ConversionTables\NO_conversions.xlsx" #CHANGE
        overlayILineConversionTables = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\ConversionTables\TEST_LineConversions.xlsx" #CHANGE
        overlayIDataSourceID = "this study"

    if crosswalkNew:
        txtFile = r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSConversionFiles\Master_Crosswalk.txt"
        print("Crosswalking the new mapping")
        arcpy.AttributeByKeyValues_GEMS(overlayInputDBPath, txtFile, True)



    arcpy.FeatureToPolygon_management(in_features=inputOverlayLines,
                                      out_feature_class=polyPath,
                                      cluster_tolerance="", attributes="ATTRIBUTES",
                                      label_features=inputOverLayPoints)

    if removeBlank:
        print("Removing blank polygons from new mapping")
        tempLayer="tempLayer"
        arcpy.MakeFeatureLayer_management(polyPath, tempLayer)
        arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION",
                                                "mapunit = ''")
        if int(arcpy.GetCount_management(tempLayer).getOutput(0)) > 0:
            arcpy.DeleteFeatures_management(tempLayer)

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
            print(row[0])
            if row[0] == None or row[0]=="":
                print("Updating feature with no attributes...")
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
                print("Nothing is blank")
else:
    print("Not Building Overlap Mapping")
    mapAreasFC = mapAreasFCOrig

listHeaderNames = ['NewMapUnit']
listFinalMapUnits = []
writer = pandas.ExcelWriter(exportFolder+r'\\'+exportGDBPrefix+timeDateString+'.xlsx')

listExportPrefixes = []
cursor = arcpy.da.SearchCursor(mapAreasFC, inputFieldNames)
count=1
for row in cursor:
    print("\n\r--------------------------------")
    print("Map area number: " + str(count))
    inputDBPath = row[1]
    inputFDSName = row[2]
    inputPrefixLength = row[3]
    listFCsToClip = row[4].split() #Turns a space deliminated list of string into a list data type
    print(listFCsToClip)
    exportFDSPrefix = row[5]
    listHeaderNames.append(exportFDSPrefix)
    listExportPrefixes.append(exportFDSPrefix)
    inputPolygons = row[6]
    conversionTable = row[7]
    print(conversionTable)
    lineConversionTable = row[8]
    print(lineConversionTable)
    print("  Export Map area / prefix: "+ exportFDSPrefix)
    inputFDSFullPath = inputDBPath + "\\" + inputFDSName
    print("  FDS to be copied: " + inputFDSFullPath)
    inputCoreFDSName = inputFDSName.split(".")[-1] # Cut off anything before the last period
    #print(inputCoreFDSName)
    prefixInitials = NCGMPname(inputCoreFDSName, inputPrefixLength)[1]
    print("  Input prefix name: " + prefixInitials)

    arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                          out_name=exportFDSPrefix + "_" + "GeologicMap",
                                          spatial_reference=spatialRef) # Create a FDS
    exportFDSFullPath = exportGDBFullPath + "\\" + exportFDSPrefix + "_" + "GeologicMap"

    print("  Created a new FDS at: " + exportFDSFullPath)
    #Copy Quad to new FDS
    Quad = exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "QuadBoundary"
    arcpy.env.workspace = exportFDSFullPath
    print("  Quad: " + Quad)
    #print("  ID: "+str(row[0]))
    tempLayer = arcpy.MakeFeatureLayer_management(mapAreasFC, "MapArea_lyr")
    arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION", "OBJECTID="+str(row[0]))
    arcpy.CopyFeatures_management(tempLayer,Quad)
    arcpy.Delete_management(tempLayer)
    arcpy.env.overwriteOutput = True

    print("\n\rvvvvvvvvvvvvvvvvvvv")
    print("Starting clipping stuff...")
    arcpy.env.workspace = inputFDSFullPath
    print("  Workspace is: " + arcpy.env.workspace)
    listFCsInInput = arcpy.ListFeatureClasses("*")
    print(listFCsInInput)
    arcpy.env.workspace = exportFDSFullPath
    print("  Workspace is: " + arcpy.env.workspace)
    for fcininput in listFCsInInput:
        genericFileName = NCGMPname(fcininput.split(".")[-1], inputPrefixLength)[0]
        print("     ####################")
        print("     Part: "+genericFileName)
        print("     Input feature class: " + fcininput)
        if genericFileName in listFCsToClip:
            importpath = inputFDSFullPath + "\\" + fcininput
            exportdestination = exportFDSFullPath + "\\" + exportFDSPrefix + "_" + genericFileName
            print("     Import Path: " + importpath)
            # ("     Check if input exists: " + str(arcpy.Exists(importpath)))
            print("     Export Destination: " + exportdestination)
            # print("     Check if export exists: " + str(arcpy.Exists(exportdestination)))

            print("     Using Clip")
            arcpy.Clip_analysis(
                in_features=importpath,
                clip_features=Quad,
                out_feature_class=exportdestination,
                # if you export this to the same FDS the feature links seem to be preserved
                cluster_tolerance="")
            print("     Finished clipping: " + genericFileName)
            if genericFileName == "ContactsAndFaults":
                # Add Quad and build polygons REQUIRES CONTACTS AND FAULTS
                quadLine = exportFDSFullPath + "\\" + "quadLines"
                quadLineParts = exportFDSFullPath + "\\" + "quadLinesParts"
                # Convert the polys to lines
                arcpy.FeatureToLine_management(Quad, quadLineParts)
                arcpy.MultipartToSinglepart_management(quadLineParts,quadLine) #This is needed for maps with non contiguous area
                arcpy.Delete_management(quadLineParts)
                arcpy.AddField_management(quadLine, "Symbol", "TEXT")
                arcpy.AddField_management(quadLine, "Type", "TEXT")
                arcpy.AddField_management(quadLine, "LocationConfidenceMeters", "FLOAT")
                arcpy.AddField_management(quadLine, "ExistenceConfidence", "TEXT")
                arcpy.AddField_management(quadLine, "IdentityConfidence", "TEXT")
                arcpy.AddField_management(quadLine, "IsConcealed", "TEXT")
                # This will change the Symbol of everything in the FC to 31.08
                with arcpy.da.UpdateCursor(quadLine, ["Symbol","Type","LocationConfidenceMeters","ExistenceConfidence",
                                                      "IdentityConfidence","IsConcealed"]) as cursor:
                    for row in cursor:
                        row[0] = '31.08'  # Map neatline
                        row[1] = 'map neatline'  # Map neatline
                        row[2] = 0.0  # Map neatline
                        row[3] = 'certain'  # Map neatline
                        row[4] = 'certain'  # Map neatline
                        row[5] = 'N'  # Map neatline
                        cursor.updateRow(row)
                print(exportdestination)
                print(quadLine)
                print(exportFDSFullPath + "\\" + "ContactsAndFaults_temp")
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
            print("     Ignoring: " + genericFileName)

    print("\n\rvvvvvvvvvvvvvvvvvvv")
    print("Clipping Polygons")
    arcpy.Clip_analysis(
        in_features=inputPolygons,
        clip_features=Quad,
        out_feature_class=exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys",
        cluster_tolerance="")

    print("\n\rvvvvvvvvvvvvvvvvvvv")
    print("Starting to rename stuff...")
    listfcsforrenaming = arcpy.ListFeatureClasses("*", "All")
    print(listfcsforrenaming)
    for fctorename in listfcsforrenaming:
        fcpath = exportFDSFullPath + "\\" + fctorename
        print("  Feature Class for field renaming: " + fctorename)
        fieldsToRename = arcpy.ListFields(fcpath)
        dfRename = pandas.read_excel(r"\\igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MrMerger\fieldsCapTable.xlsx") #TODO Move this pandas stuff out of the loop
        sdeFieldNames = dfRename['sdeField'].values.tolist()
        gemsFieldNames = dfRename['GEMSField'].values.tolist()
        for numb, field in enumerate(fieldsToRename): #TODO no nead to enumerate
            print(field.name)
            if field.name in sdeFieldNames:
                newfieldname = gemsFieldNames[sdeFieldNames.index(field.name)]
                arcpy.AlterField_management(fcpath, field.name, "zzzz") #Without this simple case changes are not recognized
                arcpy.AlterField_management(fcpath,"zzzz",newfieldname)
                print("   " + field.name + " renamed to: " + newfieldname)
            else:
                print("   Did not need to rename: "+ field.name)

    #Create Frequency Tables
    arcpy.Frequency_analysis(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "MapUnitPolys",exportGDBFullPath +"\\"+exportFDSPrefix +"_" + "MapUnits", "mapunit")

    print('Starting mapunit remapping')
    print('  Conversion table:' + conversionTable)
    df = pandas.read_excel(conversionTable)
    prevUnits = df['previous map unit'].values.tolist()
    newUnits = df['new map unit'].values.tolist()
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
                print("   Switching "+ str(unit) + " to: " +str(newUnits[index]))
            else:
                print('   No mapunit change needed for: '+ str(unit))
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

    print('Starting line remapping')
    print('  Conversion table:' + lineConversionTable)
    dfl = pandas.read_excel(lineConversionTable)
    prevLines = dfl['previous line symbol'].values.tolist()
    print(prevLines)
    newLines = dfl['new line symbol'].values.tolist()
    with arcpy.da.UpdateCursor(exportFDSFullPath + "\\" + exportFDSPrefix + "_" + "ContactsAndFaults",['Symbol']) as cursorl:
        for num, rowl in enumerate(cursorl):
            line = rowl[0]
            if line in prevLines:
                indexl = prevLines.index(line)
                rowl[0] = newLines[indexl]
                cursorl.updateRow(rowl)
                print("   Switching " + str(line) + " to: " + str(newLines[indexl]))

header = pandas.DataFrame(listHeaderNames)
theader = header.T
theader.to_excel(writer, 'Sheet1', header=False, index=False)
pandas.DataFrame([listFinalMapUnits]).T.to_excel(writer, 'Sheet1', header=False, index=False, startrow=1,startcol=0)

writer.save()
print("\n\rvvvvvvvvvvvvvvvvvvv")
print("Start merging the maps...")
arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                      out_name="MergedGeologicMap",
                                      spatial_reference=spatialRef)  # Create a FDS
exportMergedFDSFullPath = exportGDBFullPath + "\\" + "MergedGeologicMap"
print("  Created a new FDS at: " + exportMergedFDSFullPath)
print(listExportPrefixes)

#TODO create this list based on what was already created earlier
listFCsToMerge = ["MapUnitPolys","ContactsAndFaults","OrientationPoints"]
listFCTemplatesToMerge = [r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\ComplexGDB_ForMerger.gdb\GeologicMap\MapUnitPolys",
                          r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\ComplexGDB.gdb\GeologicMap\ContactsAndFaults",
                          r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\ComplexGDB.gdb\GeologicMap\OrientationPoints"]
for cnt, fcToMerge in enumerate(listFCsToMerge):
    arcpy.CreateFeatureclass_management(out_path=exportMergedFDSFullPath,
                                        out_name=fcToMerge+"_temp",
                                        geometry_type=arcpy.Describe(listFCTemplatesToMerge[cnt]).shapeType,
                                        template=listFCTemplatesToMerge[cnt])
    mergedFCPath = exportMergedFDSFullPath + "\\" + fcToMerge + "_temp"
    for mapPrefix in listExportPrefixes:
        checkAndAppend(exportGDBFullPath + "\\" + mapPrefix + "_"+ "GeologicMap" + "\\" +mapPrefix+ "_" + fcToMerge,
                       mergedFCPath)
print("Finished with all the appending...")
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

print("Finished the dissolving...")
#arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "MapUnitPolys_temp")
##Delete the contacts and faults that are no longer needed
#Can't remember exactly why I added the unsplit - no required but would fix pseudonodes
arcpy.UnsplitLine_management(in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp",
                             out_feature_class=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2",
                             dissolve_field="Type;IsConcealed;LocationConfidenceMeters;ExistenceConfidence;IdentityConfidence;Symbol;Label;DataSourceID;Notes",
                             statistics_fields="")
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "Merged\ContactsAndFaults_temp"
print("Finished the unsplitting the lines...")
#This intersects all the feature with themselves
arcpy.FeatureToLine_management(in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2",
                               out_feature_class=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
                               cluster_tolerance="", attributes="ATTRIBUTES")
#arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp")
#arcpy.Delete_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults_temp2")
print("Finished the feature to line...")
arcpy.MakeFeatureLayer_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults", 'ContactAndFaults_lyr')
arcpy.SelectLayerByLocation_management(in_layer='ContactAndFaults_lyr',
                                       select_features=exportMergedFDSFullPath + "\\" + "MapUnitPolys",
                                       overlap_type='SHARE_A_LINE_SEGMENT_WITH',
                                       invert_spatial_relationship='INVERT')
print("Finished the select by location...")
arcpy.SelectLayerByAttribute_management(in_layer_or_view='ContactAndFaults_lyr',
                                        selection_type='SUBSET_SELECTION',
                                        where_clause='Symbol NOT LIKE \'02%\'') #

arcpy.DeleteFeatures_management('ContactAndFaults_lyr')
arcpy.DeleteIdentical_management(exportMergedFDSFullPath + "\\" + "ContactsAndFaults",["Shape","Symbol"])

if removeInterior:
    arcpy.removeInteriorMapBoundaries_MergerTools(lines=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
                                                  gdb=exportGDBFullPath)

if rebuildPolygons:
    arcpy.Select_analysis(exportMergedFDSFullPath + "\\" + "MapUnitPolys", exportMergedFDSFullPath + "\\" + "MapUnitPolys_NotTiny", '"Shape_Area" > 10')
    arcpy.AddMessage("Creating centroid points...")
    arcpy.FeatureToPoint_management(in_features=exportMergedFDSFullPath + "\\" + "MapUnitPolys_NotTiny",
                                    out_feature_class=exportMergedFDSFullPath + "\\" + "MapUnitPoints",
                                    point_location="INSIDE")

    arcpy.FeatureToPolygon_management(
        in_features=exportMergedFDSFullPath + "\\" + "ContactsAndFaults",
        out_feature_class=exportMergedFDSFullPath + "\\" + "MapUnitPolys_rebuilt",
        cluster_tolerance="", attributes="ATTRIBUTES",
        label_features=exportMergedFDSFullPath + "\\" + "MapUnitPoints")

if renameAsMaster:
    arcpy.AddMessage("Overwriting the Master GDB")
    masterGDB = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeologicMaps\MergedMaps\CR_PIUTE_MASTER.gdb"
    checkAndDeleteOS(masterGDB)
    print(exportGDBFullPath)
    shutil.copytree(exportGDBFullPath, masterGDB)
    #arcpy.Copy_management(exportGDBFullPath,masterGDB)

if buildTopology:
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


if exportToAGOL:
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage("Updating Feature Service on AGOL")
    # Update these variables
    # The tempPath variable is a relative path which is the same directory
    # this script is saved to. You can modify this value to a path on your
    # system to hold the temporary files.
    serviceName = "Piute"
    tempPath = r"\\igswzcwwgsrio\mojo\Team\Crow\TEMP\agol"
    path2MXD = r"\\igswzcwwgsrio\mojo\Team\Crow\PiuteValleyGeoMaps_AGOL.mxd"

    # All paths are built by joining names to the tempPath
    SDdraft = os.path.join(tempPath, "tempdraft.sddraft")
    newSDdraft = os.path.join(tempPath, "updatedDraft.sddraft")
    SD = os.path.join(tempPath, serviceName + ".sd")

    mxd = arcpy.mapping.MapDocument(path2MXD)
    arcpy.mapping.CreateMapSDDraft(mxd, SDdraft, serviceName, "MY_HOSTED_SERVICES")

    # Read the contents of the original SDDraft into an xml parser
    doc = DOM.parse(SDdraft)

    # The follow 5 code pieces modify the SDDraft from a new MapService
    # with caching capabilities to a FeatureService with Query,Create,
    # Update,Delete,Uploads,Editing capabilities. The first two code
    # pieces handle overwriting an existing service. The last three pieces
    # change Map to Feature Service, disable caching and set appropriate
    # capabilities. You can customize the capabilities by removing items.
    # Note you cannot disable Query from a Feature Service.
    tagsType = doc.getElementsByTagName('Type')
    for tagType in tagsType:
        if tagType.parentNode.tagName == 'SVCManifest':
            if tagType.hasChildNodes():
                tagType.firstChild.data = "esriServiceDefinitionType_Replacement"

    tagsState = doc.getElementsByTagName('State')
    for tagState in tagsState:
        if tagState.parentNode.tagName == 'SVCManifest':
            if tagState.hasChildNodes():
                tagState.firstChild.data = "esriSDState_Published"

    # Change service type from map service to feature service
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        if typeName.firstChild.data == "MapServer":
            typeName.firstChild.data = "FeatureServer"

    # Turn off caching
    configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "isCached":
                    keyValue.nextSibling.firstChild.data = "false"

    # Turn on feature access capabilities
    configProps = doc.getElementsByTagName('Info')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    keyValue.nextSibling.firstChild.data = "Query,Create,Update,Delete,Uploads,Editing"

    # Write the new draft to disk
    f = open(newSDdraft, 'w')
    doc.writexml(f)
    f.close()

    # Analyze the service
    analysis = arcpy.mapping.AnalyzeForSD(newSDdraft)

    if analysis['errors'] == {}:
        # Stage the service
        arcpy.StageService_server(newSDdraft, SD)

        # Upload the service. The OVERRIDE_DEFINITION parameter allows you to override the
        # sharing properties set in the service definition with new values. In this case,
        # the feature service will be shared to everyone on ArcGIS.com by specifying the
        # SHARE_ONLINE and PUBLIC parameters. Optionally you can share to specific groups
        # using the last parameter, in_groups.
        arcpy.UploadServiceDefinition_server(SD, "My Hosted Services", serviceName,
                                             "", "", "", "", "OVERRIDE_DEFINITION", "SHARE_ONLINE",
                                             "PUBLIC", "SHARE_ORGANIZATION", "")

        print "Uploaded and overwrote service"

    else:
        # If the sddraft analysis contained errors, display them and quit.
        print analysis['errors']

end = datetimePrint()[3]
elapsed = end-start
print("Elapsed time: "+str(elapsed))

arcpy.env.overwriteOutput = False