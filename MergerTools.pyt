import arcpy


def getGDB(fc):
    startIndex = fc.find(".gdb")
    if startIndex != -1:
        arcpy.AddMessage(fc[0:startIndex])
        return fc[0:startIndex] + ".gdb"
    else:
        return

class Toolbox (object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "MergerTools"
        self.alias = "MergerTools"

        # List of tool classes associated with this toolbox
        self.tools = [dissolveAndConcatenate,removeInteriorMapBoundaries,calcLabels,simpConcat]

class dissolveAndConcatenate(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "DissolveAndConcatenate"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="FC to dissolve:",
            name="polysToDissolve",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output Workspace:",
            name="gdb",
            datatype=["DEWorkspace"],
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Output Feature Class:",
            name="output",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        params = [param0,param1,param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        polysToDissolve = parameters[0].valueAsText
        gdb = parameters[1].valueAsText
        outputPath = parameters[2].valueAsText

        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("Starting the dissolve...")
        arcpy.Dissolve_management(in_features=polysToDissolve,
                                  out_feature_class=gdb+"\\"+"Polys_Dissolve",
                                  dissolve_field="MapUnit",
                                  statistics_fields="",
                                  multi_part="SINGLE_PART",
                                  unsplit_lines="DISSOLVE_LINES")
        # arcpy.AddField_management(gdb+"\\"+"Polys_Dissolve", "OrigMapUnits", "TEXT", field_length=10000)
        # arcpy.AddField_management(gdb+"\\"+"Polys_Dissolve", "OrigDataSourceIDs", "TEXT", field_length=10000)

        arcpy.Select_analysis(polysToDissolve, gdb+"\\"+"Polys_NotTiny",'"Shape_Area" > 10')
        arcpy.AddMessage("Creating centroid points...")
        arcpy.FeatureToPoint_management(in_features=gdb+"\\"+"Polys_NotTiny",
                                        out_feature_class=gdb+"\\"+"Poly_Points",
                                        point_location="INSIDE")

        fieldmappings = arcpy.FieldMappings()

        # Add all fields from inputs.
        fieldmappings.addTable(gdb+"\\"+"Polys_Dissolve")
        fieldmappings.addTable(gdb+"\\"+"Poly_Points")

        # Name fields you want. Could get these names programmatically too.
        keepers = ["OrigUnit", "DataSourceID", "IdentityConfidence"]

        # Remove all output fields you don't want.
        for field in fieldmappings.fields:
            if field.name not in keepers and not "MapUnit":
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
        for field2 in keepers:
            origFieldIndex = fieldmappings.findFieldMapIndex(field2)
            fieldmap = fieldmappings.getFieldMap(origFieldIndex)
            fieldmap.mergeRule = "Join"
            fieldmap.joinDelimiter = ","
            fieldName=fieldmap.outputField
            fieldName.length=1000000
            fieldmap.outputField = fieldName
            fieldmappings.replaceFieldMap(origFieldIndex,fieldmap)

        arcpy.AddMessage(str(fieldmappings))

        arcpy.AddMessage("Doing the spatial join")
        arcpy.SpatialJoin_analysis(target_features=gdb+"\\"+"Polys_Dissolve",
                                   join_features=gdb+"\\"+"Poly_Points",
                                   out_feature_class=outputPath,
                                   join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL",
                                   field_mapping= fieldmappings,
                                   match_option="INTERSECT", search_radius="", distance_field_name="")

        #TODO delete unneeded files
        return

class removeInteriorMapBoundaries(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "RemoveInteriorMapBoundaries"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="ContactsAndFaults:",
            name="lines",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")


        param1 = arcpy.Parameter(
            displayName="Output Workspace:",
            name="gdb",
            datatype=["DEWorkspace"],
            parameterType="Required",
            direction="Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        lines = parameters[0].valueAsText
        gdb = parameters[1].valueAsText

        arcpy.env.overwriteOutput = True

        arcpy.AddMessage("Finding indentical geometries")
        arcpy.FindIdentical_management(in_dataset=lines,
                                       out_dataset=gdb + "\\" + "IdenticalTable",
                                       fields="Shape", xy_tolerance="", z_tolerance="0",
                                       output_record_option="ONLY_DUPLICATES")

        arcpy.MakeFeatureLayer_management(lines, 'ContactAndFaults_lyr')

        arcpy.AddMessage("Joining the attributes")
        arcpy.AddJoin_management(in_layer_or_view="ContactAndFaults_lyr",in_field="OBJECTID",
                                 join_table=gdb + "\\" + "IdenticalTable",join_field="IN_FID")

        arcpy.AddMessage("Selecting the identical map boundaries")
        arcpy.SelectLayerByAttribute_management(in_layer_or_view='ContactAndFaults_lyr',
                                                selection_type='NEW_SELECTION',
                                                where_clause='IN_FID IS NOT NULL')

        arcpy.SelectLayerByAttribute_management(in_layer_or_view='ContactAndFaults_lyr',
                                                selection_type='SUBSET_SELECTION',
                                                where_clause='Symbol = \'31.08\'')  #


        arcpy.AddMessage("Removing the identical map boundaries")
        arcpy.DeleteFeatures_management('ContactAndFaults_lyr')
        return

class calcLabels(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "CalculateLabels"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="FC to calc:",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fc = parameters[0].valueAsText
        edit = arcpy.da.Editor(getGDB(fc))
        edit.startEditing(False, False)
        edit.startOperation()
        with arcpy.da.UpdateCursor(fc,['MapUnit', 'Label']) as cursor:
            for row in cursor:
                mapunit=row[0]
                #arcpy.AddMessage("Mapunit is: "+str(mapunit))
                if mapunit is not None:
                    if mapunit.startswith("IP"):
                        row[1]=mapunit.replace("IP","*",1)
                    elif mapunit.startswith("TR"):
                        row[1]=mapunit.replace("TR","^",1)
                    elif mapunit.startswith("C"):
                        row[1]=mapunit.replace("C","_",1)
                    else:
                        row[1]=mapunit
                else:
                    arcpy.AddMessage("No mapunit")
                cursor.updateRow(row)
        edit.stopOperation()
        edit.stopEditing(True)

        return

class simpConcat(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SimplifyConcatenations"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="FC to simplify:",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fc = parameters[0].valueAsText
        edit = arcpy.da.Editor(getGDB(fc))
        edit.startEditing(False, False)
        edit.startOperation()
        with arcpy.da.UpdateCursor(fc,['IdentityConfidence','DataSourceID','OrigUnit','OBJECTID']) as cursor:
            for row in cursor:
                arcpy.AddMessage("________")
                MapUnit = str(row[2]).split(",")
                arcpy.AddMessage("Object ID:"+str(row[3]))
                arcpy.AddMessage("Original Attributes:")
                arcpy.AddMessage(" Mapunits: "+str(MapUnit))
                IdentityConfidence = str(row[0]).split(",")
                arcpy.AddMessage(" IdentityConfidence: "+str(IdentityConfidence))
                DataSourceID = str(row[1]).split(",")
                arcpy.AddMessage(" DatSourceID: "+str(DataSourceID))

                length = len(MapUnit)
                lengthConf = len(IdentityConfidence)
                lengthData = len(DataSourceID)
                arcpy.AddMessage("Number of values: " +str(length)+", " +str(IdentityConfidence)+", "+str(DataSourceID))


                if length == lengthConf and length == lengthData and lengthConf == lengthData:
                    concatList = []
                    arcpy.AddMessage("Empty list of concatenated attributes: " + str(concatList)) #For testing
                    for n, value in enumerate(MapUnit):
                        concatList.append([MapUnit[n], IdentityConfidence[n], DataSourceID[n]])
                    arcpy.AddMessage("List of concatenated attributes: "+str(concatList))

                    uniqueConcat = []
                    for p in concatList:
                        if p not in uniqueConcat:
                            uniqueConcat.append(p)
                    arcpy.AddMessage("List of unique attribute: "+str(uniqueConcat))

                    newMapUnit = []
                    newIdentityConfidence = []
                    newDataSourceID = []

                    for s, value in enumerate(uniqueConcat):
                        newMapUnit.append(value[0])
                        newIdentityConfidence.append(value[1])
                        newDataSourceID.append(value[2])

                    arcpy.AddMessage("New Attributes:")
                    arcpy.AddMessage("  New Mapunits: "+str(newMapUnit))
                    arcpy.AddMessage("  New IdentityConfidence: "+str(newIdentityConfidence))
                    arcpy.AddMessage("  New DataSourceID "+str(newDataSourceID))

                    row[2] = ", ".join(newMapUnit)
                    row[0] = ", ".join(newIdentityConfidence)
                    row[1] = ", ".join(newDataSourceID)

                    cursor.updateRow(row)
                else:
                    arcpy.AddMessage("Warning: lists are different lengths")

                #Empything lists to try and get around an issue...
                concatList = []
                uniqueConcat= []
                newMapUnit= []
                newIdentityConfidence= []
                newDataSourceID= []

        edit.stopOperation()
        edit.stopEditing(True)

        return