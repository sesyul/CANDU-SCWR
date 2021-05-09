# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Mass Flow data treatment 
##
# @file TreatMaps.py 
# 
# @author U. Le Tennier (March 2021)
#
# @brief Contains the data treatment functions to handle parameter distributions retrieved from coupling (except mass flow).
#
# Three functions are available : CreateMatrix(), CreateMatrixPwr() and CreateHMap(). CreateMatrix() retrieves the distribution 
# from the coupling outputs (.txt) and returns the matrix object that can be directly used as an input for CreateHMap(). CreateMatrixPwr()
# works almost exactly the same but only retrieves power distribution in the fuelmap object. Therefore, it uses additional python 
# functions (ASCIIOpnv4, ASCIIGetv4 and ASCIISixv4) that enable to navigate effectively in donjon outputs.  
# CreateMatrix() and CreateMatrixPwr() use as input the absolute path where are located the coupling outputs or the fuelmap. 
# It also uses the cycle number CyNumb and the cycle step CyStep to pick up the required information from the coupling outputs. 
# The type of evolution EvTy (3-batches "3c" or 4-batches "4c") is finally asked. CreateHMap() requires the matrix and the height z required. 
# z belongs to [0;19] : 0 corresponds to the bottom of the core (where the flow reverses its path), 19 is at the top. \n \n
# From the matrix built, different charts can be created, 
# for instance the relative axial power distribution. Because it is relatively easy to create such a chart and impossible to cover all the 
# possibilities, no dedicated function is provided. It is up to the user to create his own additional functions. 
#
# @remarks
# Certain combinations of CyStep and EvTy are impossible. For example, a "4c" has only 18 steps per cycle. An error can occur if 
# an inconsistent call is made.
# 
# @remarks
# If the data required is not available but the combination (CyStep and EvTy) is possible, the codes does not return an error. It sends a cordial 
# invitation to check if the data required exists in the coupling output. Such an invitation cannot be sent by CreateMatrixPwr() because 
# no data can be lost in the fuelmap object. There is still a way to retrieve the data of the last cycle simulated which lies in the DISTRIBUTION folder. 
#
# @remarks
# Because of the different values that can be found, the colorscale must be adjusted at the beginning of CreateHMap(). Otherwise, the heatmap risk 
# to appear in only one color, without shades. 
#
# @remarks
# By default, at the end of CreateChartHmap(), the line that enables to save direclty the chart is wrote as a commentary. To use it, uncomment it
# and give the path where you want to save the chart.
#
# @remarks
# CreateHMap() uses seaborn module to produce the heatmap. By default, the colormap used is coolwarm. 
# Additionnal informations about seaborn and colormap options can be found on the following pages : \n
# seaborn     package      https://seaborn.pydata.org/generated/seaborn.heatmap.html \n
# additionnal colormaps    https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html \n
# create      colormaps    https://matplotlib.org/3.1.1/tutorials/colors/colormap-manipulation.html \n
# additionnal informations https://www.kdnuggets.com/2019/07/annotated-heatmaps-correlation-matrix.html 
# 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Imports
import os 
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt 
import seaborn as sns
import pandas  as pd
import matplotlib.pylab as plb
from matplotlib import rc 
from matplotlib import cm 

# Put the ASCII functions in the same dir than TreamMaps.py and uncomment #1 or give the absolute path to ASCII functions with #2
#1 PATH_PROC_PY = os.path.dirname(__file__)
#2 PATH_PROC_PY = '/Users/Ulysse/Documents/Poly/Maitrise/Documentation'
PATH_PROC_PY = os.path.dirname(__file__)
os.chdir(PATH_PROC_PY)

from ASCIIOpnv4 import *
from ASCIIGetv4 import *
from ASCIISixv4 import *


## Creates a 20x20x20 matrix and fill it with data in FileId (coupling outputs), unfolds the geometry \n \n
#   INPUTS \n
#   1) FileId        : string, absolute path to the parameter_report.txt \n
#   2) CyNumb        :    int, number of targeted cycle \n
#   3) CyStep        :    int, number of targeted step of cycle CyNumb \n
#   4) EvTy          : string, reloading model, available : "3c" and "4c" \n \n
#   OUTPUTS \n
#   a) matrix        :  array(20x20x20), distribution of parameter for a full core \n
def CreateMatrix(FileId,CyNumb,CyStep,EvTy):
    
    # Checks 
    assert EvTy == "3c" or EvTy == "4c"
    assert CyStep > 0
    
    if EvTy == "3c" :
        assert CyStep < 23
        absStep = 22 * (CyNumb-1) + CyStep
        
    else :
        assert CyStep < 19 
        absStep = 18 * (CyNumb-1) + CyStep
    
    assert os.path.isfile(FileId)
    
    to_find = ">>Step "+str(absStep)+" "
    end     = len(to_find)
    
    # Look for the accurate step, begin at the bottom of the file
    with open(FileId, 'r') as File:
        Lines = File.readlines()
        ref = Lines[0]
        
        found = False 
        line  = -1
        LLine = Lines[line]
        
        # Find the data required 
        while LLine != ref and found == False :
            line -= 1
            LLine = Lines[line]
            
            if LLine[0:end] == to_find :
                found = True
        
            if LLine == ref :
                print("Unable to find "+(to_find)+", (Cycle :"+str(CyNumb)+", Step :"+str(CyStep)+", Evo Type :"+(EvTy)+")") 
                print("Check if the step number asked is in the targeted file")
                return
            
        # Create the matrix and fill it
        matrix  = np.zeros((20,20,20))
        
        j = 1
        LLine = Lines[line+j]
        
        # Elevation, lin and column 
        ele = 19
        col = 6
        lin = 0
        
        # Beginning and end of where to test the space ' '
        a = 0
        b = 1
        
        co = 0 
        
        while ele > -1 :
            
            while col != 14 or lin != 19 :
                if Lines[line+j][b] == ' ' :  
                    matrix[lin,col,ele] = float(Lines[line+j][a:b])
                    a    = b+1 
                    b   += 1
                    col += 1
                    co  += 1
                    
                    # If you have to give a look here, the python's god bless you, you have come a long way  
                    # Managing to unfold the data to have a clear view of the reactor 
                    if col == 14 and lin == 0 :
                        lin += 1
                        col  = 4
                        
                    elif col == 16 and lin == 1 :
                        lin += 1
                        col  = 2   
                        
                    elif col == 18 and lin == 2 :
                        lin += 1
                        col  = 2   
                        
                    elif col == 18 and lin == 3 :
                        lin += 1
                        col  = 1    
                        
                    elif col == 19 and lin == 4 :
                        lin += 1
                        col  = 1    
                        
                    elif col == 19 and lin == 5 :
                        lin += 1
                        col  = 0 
                        
                    elif col == 20 and lin > 5 and lin < 13 :
                        lin += 1
                        col  = 0
                        
                    elif col == 20 and lin == 13 :
                        lin += 1
                        col  = 1
                        
                    elif col == 19 and lin == 14 :
                        lin += 1
                        col  = 1
                        
                    elif col == 19 and lin == 15 :
                        lin += 1
                        col  = 2
                        
                    elif col == 18 and lin == 16 :
                        lin += 1
                        col  = 2
                        
                    elif col == 18 and lin == 17 :
                        lin += 1
                        col  = 4
                        
                    elif col == 16 and lin == 18 :
                        lin += 1
                        col  = 6
                
                if co == 5 :
                    j += 1 
                    co = 0
                    a  = 0
                    b  = 1
                            
                # 5 values per line in the coupling output 
                b += 1 
                
            ele -= 1
            
            col = 6
            lin = 0
            
    return(matrix)

## Creates a 20x20x20 matrix and fill it with data in FileId (donjon outputs), unfolds the geometry \n \n
#   INPUTS \n
#   1) FileId        : string, absolute path to FMAP.inp \n
#   2) CyNumb        :    int, number of targeted cycle \n
#   3) CyStep        :    int, number of targeted step of cycle CyNumb \n
#   4) EvTy          : string, reloading model, available : "3c" and "4c" \n \n
#   OUTPUTS \n
#   a) matrix        :  array(20x20x20), power distribution for a full core   \n 
def CreateMatrixPwr(FileId,CyNumb,CyStep,EvTy):
    
    # Checks 
    assert EvTy == "3c" or EvTy == "4c"
    assert CyStep > 0
    
    if EvTy == "3c" :
        assert CyStep < 23
        
    else :
        assert CyStep < 19
    
    assert os.path.isfile(FileId)
    
    # In FuelMap object, the rep. 1 is here to initiate the cycle, the first pwr dist. is in rep. 2
    CyStep += 1
    
    # Process FuelMap
    (ilvl,RecordPos,RecordNumb,RecordName,CurRecInd) = ASCIIOpnv4(FileId) 
    
    SubDir      = 'Cycle'+str(CyNumb)+ (7-len(str(CyNumb)))*' '
    SubSubDir   = 'elt#' + '0'*(8 - len(str(CyStep)) ) + str(CyStep)
 
    (ilvl,nbdata,CurRecInd) = ASCIISixv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,SubDir,1)
    (ilvl,nbdata,CurRecInd) = ASCIISixv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,SubSubDir,1)
    
    Power_Dist  = ASCIIGetv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'POWER-BUND  ')    
    
    # Create the matrix and fill it
    matrix  = np.zeros((20,20,20))
        
    # Elevation, lin and column 
    ele = 19
    col = 6
    lin = 0
        
    for i in range(6720) :
        
        matrix[lin,col,ele] = Power_Dist[i,0]
        col += 1
        
        # If you have to give a look here, the python's god bless you, you have come a long way  
        # Managing to unfold the data to have a clear view of the reactor 
        if col == 14 and lin == 0 :
            lin += 1
            col  = 4
            
        elif col == 16 and lin == 1 :
            lin += 1
            col  = 2   
            
        elif col == 18 and lin == 2 :
            lin += 1
            col  = 2   
            
        elif col == 18 and lin == 3 :
            lin += 1
            col  = 1    
            
        elif col == 19 and lin == 4 :
            lin += 1
            col  = 1    
            
        elif col == 19 and lin == 5 :
            lin += 1
            col  = 0 
            
        elif col == 20 and lin > 5 and lin < 13 :
            lin += 1
            col  = 0
            
        elif col == 20 and lin == 13 :
            lin += 1
            col  = 1
            
        elif col == 19 and lin == 14 :
            lin += 1
            col  = 1
            
        elif col == 19 and lin == 15 :
            lin += 1
            col  = 2
            
        elif col == 18 and lin == 16 :
            lin += 1
            col  = 2
            
        elif col == 18 and lin == 17 :
            lin += 1
            col  = 4
            
        elif col == 16 and lin == 18 :
            lin += 1
            col  = 6
        
        # If everything is good on an elevation 
        if col == 14 and lin == 19 :
            ele -= 1
            col = 6
            lin = 0
            
   
    return(matrix)


## Creates a quarter core heatmap from a 20x20x20 matrix  \n \n
#   INPUTS \n
#   1) matrix  :  array(20x20x20), distribution retrieved from CreateMatrix() or CreateMatrixPwr()   \n
#   2) z       :              int, elevation to display : 0 bottom of the core, 19 top   \n
def CreateHmap(matrix,z):
    
    matrix = matrix[0:10,0:10,z]
    
    # Managing the color scale, should be changed depending on which data is displayed
    if matrix[9,9] < 1 :
        norm = 1000
        vmm  = 0.70
        vmx  = 0.06
        
    elif matrix[9,9] < 1100 :
        norm =   10
        vmm  =  100
        vmx  = 1000
        
    elif matrix[9,9] < 2000 :
        norm =   10
        vmm  = 1000
        vmx  = 2000
        
    elif matrix[9,9] < 3000 :
        norm =   10
        vmm  = 2000
        vmx  = 3000
    
    # Manage the number of digits
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i,j] = ((matrix[i,j]*norm)//1)/norm
            
    # Mask that enables to remove the zeros
    mask = np.zeros_like(matrix, dtype=np.bool)
    mask[0,0]= True
    mask[0,1]= True
    mask[0,2]= True
    mask[0,3]= True
    mask[0,4]= True
    mask[0,5]= True
    mask[1,0]= True
    mask[1,1]= True
    mask[1,2]= True
    mask[1,3]= True
    mask[2,0]= True
    mask[2,1]= True
    mask[3,0]= True
    mask[3,1]= True
    mask[4,0]= True
    mask[5,0]= True
    
    f, ax = plt.subplots(figsize=(11, 15))
    heatmap = sns.heatmap(matrix,
                        mask = mask,
                        square = True,
                        linewidths = .5,
                        cmap = 'coolwarm',
                        vmin = vmm,
                        vmax = vmx,
                        annot = True,
                        fmt='.2f',
                        annot_kws = {"size": 12})
                        
    heatmap.set_xticklabels(heatmap.get_xmajorticklabels(), fontsize = 12)
    heatmap.set_yticklabels(heatmap.get_ymajorticklabels(), fontsize = 12)
    plt.yticks(rotation=0)
    plt.xticks(rotation=0)
    ax.xaxis.tick_top()
    
    plt.yticks(np.arange(0.5,10.5), ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
    plt.xticks(np.arange(0.5,10.5), ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'))
    plt.rcParams['font.family'] = "CMU Serif"
    
    heatmap.tick_params(left=False, top=False)
    heatmap.set_xticklabels(heatmap.get_xmajorticklabels(), fontsize = 14)
    heatmap.set_yticklabels(heatmap.get_ymajorticklabels(), fontsize = 14)
    
    ax.set_title(r'Value (unit)', fontsize = 18,color='Black', y=1.06)  # Note title moves to make room for ticks   
    
    # heatmap.get_figure().savefig('PATH_SAVE')
    
    plt.show()
    
    # mpl.font_manager._rebuild()
    # print(matplotlib.matplotlib_fname())
    # print(matplotlib.get_cachedir())

