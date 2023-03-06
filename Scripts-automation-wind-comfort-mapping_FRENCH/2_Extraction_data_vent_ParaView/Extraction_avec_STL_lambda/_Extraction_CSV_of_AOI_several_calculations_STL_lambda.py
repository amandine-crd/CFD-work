# trace generated using paraview version 5.9.1

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

##############################################################################################################################################
#============================================== DONNEES A MODIFIER (UNIQUEMENT CES DONNEES !) ==============================================##
##############################################################################################################################################

precision_nombres = 3

path_STL = 'D:/DATA/a.conrad/Documents/Professionnel/Wind_comfort/STL/Test_basique/AOI_sol_1_v4.stl'
general_file_name = 'Vent_batiments_test_basique_project_2_bis_'
general_path = 'D:/DATA/a.conrad/Documents/Professionnel/Wind_comfort/Simus_OF/Test_basique/3_Calculs'
path_CSV = 'D:/DATA/a.conrad/Documents/Professionnel/Wind_comfort/Simus_OF/Test_basique/4_Calcul_proba_2_bis/Sol_test_auto'
wind_dir = [45, 135, 225, 315]
nom_CSV_general = 'extrait_surface_test'
origin = [0.0, 0.0, 1.2]
normale = [0.0, 0.0, 1.0]

#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

        #--------------------------------------------------#
        #--------- OPENING OF THE STL FOR THE AOI ---------#
        #--------------------------------------------------#
        
STL_nomination = 'AOI'

AOI = STLReader (registrationName = STL_nomination, FileNames =[path_STL])
#get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# show data in a view
AOIDisplay = Show(AOI,renderView1, 'GeometryRepresentation')
# get color transfer function/color map for 'STLSolidLabeling'
sTLSolidLabelingLUT = GetColorTransferFunction ('STLSolidLabeling')

# show color bar/color legend
AOIDisplay.SetScalarBarVisibility(renderView1, True)
# update the view to ensure updated data information
renderView1.Update()
# get opacity transfer function/opacity map for 'STLSolidLabeling'
sTLSolidLabelingPWF = GetOpacityTransferFunction('STLSolidLabeling')


        #---------------------------------------------------------------------------------------------------#
        #--------- Here starts a loop where it opens the calculation, make an extraction of points ---------#
        #--------- and export these points data into a CSV. Eventually it closes the calculation. ----------#
        #---------------------------------------------------------------------------------------------------#

for i in wind_dir :
    
    file_nomination = 'calcul'+str(i)
    file_name = general_file_name + str(i) +'deg'
    foam_name = general_file_name + str(i) +'deg.foam'
    path_file = general_path + '/' + file_name +'/'  + foam_name
    CSV_nomination = nom_CSV_general + str(i) + 'deg.csv'
    
    # create a new 'OpenFOAMReader' and give the properties
    calcul = OpenFOAMReader(registrationName = file_nomination, FileName = path_file)
    calcul.MeshRegions = ['internalMesh']
    calcul.CaseType = 'Decomposed Case'
    
    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
        # get animation scene
    animationScene1 = GetAnimationScene()
    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()
    
    # show data in view
    calculDisplay = Show(calcul, renderView1, 'UnstructuredGridRepresentation')
    
    # get color transfer function/color map for 'p'
    pLUT = GetColorTransferFunction('p')
    # get opacity transfer function/opacity map for 'p'
    pPWF = GetOpacityTransferFunction('p')
    
    # trace defaults for the display properties.
    calculDisplay.Representation = 'Surface'
    calculDisplay.ColorArrayName = ['POINTS', 'p']
    calculDisplay.LookupTable = pLUT
    calculDisplay.SelectTCoordArray = 'None'
    calculDisplay.SelectNormalArray = 'None'
    calculDisplay.SelectTangentArray = 'None'
    calculDisplay.OSPRayScaleArray = 'p'
    calculDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    calculDisplay.SelectOrientationVectors = 'U'
    calculDisplay.ScaleFactor = 210.0
    calculDisplay.SelectScaleArray = 'p'
    calculDisplay.GlyphType = 'Arrow'
    calculDisplay.GlyphTableIndexArray = 'p'
    calculDisplay.GaussianRadius = 10.5
    calculDisplay.SetScaleArray = ['POINTS', 'p']
    calculDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    calculDisplay.OpacityArray = ['POINTS', 'p']
    calculDisplay.OpacityTransferFunction = 'PiecewiseFunction'
    calculDisplay.DataAxesGrid = 'GridAxesRepresentation'
    calculDisplay.PolarAxes = 'PolarAxesRepresentation'
    calculDisplay.ScalarOpacityFunction = pPWF
    calculDisplay.ScalarOpacityUnitDistance = 11.569309286764984
    calculDisplay.OpacityArrayName = ['POINTS', 'p']
    calculDisplay.ExtractedBlockIndex = 1
    
    # reset view to fit data
    renderView1.ResetCamera()
    # get the material library
    materialLibrary1 = GetMaterialLibrary()  
    # show color bar/color legend
    calculDisplay.SetScalarBarVisibility(renderView1, True)
    
        #-------------------------------------------------------------#
        # CREATION OF A SLICE TO TAKE FOR THE EXTRACT ENCLOSED POINTS #
        #-------------------------------------------------------------#
        
    slice1 = Slice(registrationName='Slice1', Input = calcul)
    slice1.SliceType = 'Plane'
    slice1.HyperTreeGridSlicer = 'Plane'
    slice1.SliceOffsetValues = [0.0]
    
    # Properties modified on slice1.SliceType
    slice1.SliceType.Origin = origin
    slice1.SliceType.Normal = normale
    
    slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')
    
    Hide(calcul, renderView1)
    slice1Display.SetScalarBarVisibility(renderView1, True)
    renderView1.Update()
    
        #---------------------------------------------------------------#
        #--------- CREATION OF A NEW 'EXTRACT ENCLOSED POINTS' ---------#
        #---------------------------------------------------------------#
    
    # create a new 'Extract Enclosed Points'
    extraction1 = ExtractEnclosedPoints(registrationName = 'extraction_1', Input = slice1, Surface = AOI)
    extraction1Display = Show (extraction1, renderView1, 'GeometryRepresentation')
    
    # hide data in view
    Hide(slice1, renderView1)
    Hide(AOI, renderView1)
    renderView1.Update()
    # show color bar/color legend
    extraction1Display.SetScalarBarVisibility(renderView1, True)
    extraction1Display_1 = Show(OutputPort(extraction1, 1), renderView1, 'GeometryRepresentation')
    
    # set scalar coloring
    ColorBy(extraction1Display, ('POINTS', 'U', 'Magnitude'))
    # Hide the scalar bar for this color map if no visible data is colored by it.
    HideScalarBarIfNotNeeded(pLUT, renderView1)
    
    # rescale color and/or opacity maps used to include current data range
    extraction1Display.RescaleTransferFunctionToDataRange(True, False)
    # show color bar/color legend
    extraction1Display.SetScalarBarVisibility(renderView1, True)
    # get color transfer function/color map for 'U'
    uLUT = GetColorTransferFunction('U')
    # get opacity transfer function/opacity map for 'U'
    uPWF = GetOpacityTransferFunction('U')
    
        #---------------------------------------------------------------#
        #--------- EXPORT IN SPREADSHEETVIEW AND EXPORT IN CSV ---------#
        #---------------------------------------------------------------#
    
    #get layout
    layout1 = GetLayout()
    #split cell
    layout1.SplitHorizontal (0, 0.5)
    
    SetActiveView(None)
    
    #Create a new spreadsheet view
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.ColumnToSort = ''
    spreadSheetView1.BlockSize = 1024
        	
    extraction_1 = GetActiveSource()
        	
    extraction_1Display = Show(extraction_1, spreadSheetView1, 'SpreadSheetRepresentation')
    
    # assign view to a particular cell in the layout
    AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=2)
    
    ExportView (path_CSV + '/' + CSV_nomination, view = spreadSheetView1, RealNumberPrecision = precision_nombres)
    
        #--------------------------------------------------------------------#
        #--------- DELETING SPREADSHEET, EXTRACTION AND CALCULATION ---------#
        #--------------------------------------------------------------------#
        
    spreadSheetView1 = GetActiveViewOrCreate ('SpreadSheetView')
    Delete (spreadSheetView1)
    del spreadSheetView1
    layout1 = GetLayoutByName ("Layout #1")
    layout1.Collapse(2) 
    renderView = FindViewOrCreate ('RenderView1', viewtype = 'RenderView')
    SetActiveView(renderView)
    
    uLUT = GetColorTransferFunction('U')
    uPWF = GetOpacityTransferFunction('U')
    
    calcul_suppr = FindSource(file_nomination)
    extraction_1 = FindSource('extraction_1')
    slice_suppr = FindSource('Slice1')
    
    Delete (extraction_1)
    del extraction_1
    
    Delete (slice_suppr)
    del slice_suppr
    
    Delete(calcul_suppr)
    del calcul_suppr
    
    sTLSolidLabelingLUT = GetColorTransferFunction('STLSolidLabeling')
    sTLSolidLabelingPWF = GetOpacityTransferFunction('STLSolidLabeling')
    
    animationScene1 = GetAnimationScene()
    animationScene1.UpdateAnimationUsingDataTimeSteps()