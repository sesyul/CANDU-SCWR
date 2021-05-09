# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Mass Flow data treatment 
##
# @file TreatMapMFlw.py 
# 
# @author U. Le Tennier (March 2021)
#
# @brief Contains the data treatment functions to handle mass flow distributions retrieved from coupling.
#
# Two functions are available : CreateMatrixMFlw() and CreateHMapMFlw(). CreateMatrixMFlw() retrieves the mass flow distribution 
# from the coupling output and returns the matrix object that can be directly used as an input for CreateHMapMFlw(). CreateMatrixMFlw()
# uses as input the absolute path where the coupling output is located. It also uses the cycle number CyNumb and the cycle step CyStep
# to pick up the required information from the coupling outputs. The type of evolution EvTy (3-batches "3c" or 4-batches "4c") is finally asked.
#
# @remarks
# Certain combinations of CyStep and EvTy are impossible. For example, a "4c" has only 18 steps per cycle. An error can occur if 
# an inconsistent call is made.
# 
# @remarks
# If the data required is not available but the combination (CyStep and EvTy) is possible, the codes does not return an error. It returns a 
# cordial invitation to check if the data required exists in the coupling output. A possible reason is that the coupling code was interrupted 
# while processing. There is still a way to retrieve the data of the last cycle simulated which lies in the DISTRIBUTION folder. 
#
# @remarks
# By default, at the end of CreateChart(), the line that enables to save directly the chart is written as a commentary. To use it, uncomment it
# and give the path where you want to save the chart.
#
# @remarks
# CreateHMapMFlw() uses seaborn module to produce the heatmap. By default, the colormap used is coolwarm. 
# Additionnal informations about seaborn and colormap options can be found on the following pages : \n
# seaborn     package      https://seaborn.pydata.org/generated/seaborn.heatmap.html \n
# additionnal colormaps    https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html \n
# create      colormaps    https://matplotlib.org/3.1.1/tutorials/colors/colormap-manipulation.html \n
# additionnal informations https://www.kdnuggets.com/2019/07/annotated-heatmaps-correlation-matrix.html 

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


## Creates a 10x10x1 matrix and fill it with data in FileId, unfolds the geometry \n \n
#   INPUTS \n
#   1) FileId        : string, absolute path to MassFlow_report  \n
#   2) CyNumb        :    int, number of targeted cycle  \n
#   3) CyStep        :    int, number of targeted step of cycle CyNumb \n
#   4) EvTy          : string, reloading model, available : "3c" and "4c" \n \n
#   OUTPUTS \n
#   a) matrix        :  array(10x10x1), mass flow distribution of a quarter core \n
def CreateMatrixMFlw(FileId,CyNumb,CyStep,EvTy):
    
    # Checks 
    assert EvTy == "3c" or EvTy == "4c"
    
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
        matrix  = np.zeros((10,10))
        
        j = 1
        LLine = Lines[line+j]
        
        # Elevation, lin and column 
        ele = 0
        col = 6
        lin = 0
        
        # Beginning and end of where to test the space ' '
        a = 0
        b = 1
        
        co = 0 
        
        while ele < 1 :
            
            while col != 10 and lin != 10 :
                if Lines[line+j][b] == ' ' :    
                    matrix[lin,col] = float(Lines[line+j][a:b])/4
                    a    = b+1 
                    b   += 1
                    col += 1
                    co  += 1
                    
                    if col == 10 :
                        lin += 1
                        
                        if lin == 1 :
                            col = 4 
                            
                        elif lin == 2 or lin == 3 :
                            col = 2    
                                                     
                        elif lin == 4 or lin == 5 :
                            col = 1
                            
                        else :
                            col = 0 
                
                if co == 1 :
                    j += 1 
                    co = 0
                    a    = 0
                    b    = 1
                            
                # 2 values per line in the coupling output 
                b += 1 
                
            ele += 1
   
    return(matrix)

## Creates a quarter core heatmap from a 10x10x1 matrix \n \n
#   INPUTS \n
#   1) matrix        :  array(10x10x1), mass flow distribution retrieved from CreateMatrixMFlw()  \n 
def CreateHMapMFlw(matrix) :
    
    # Manage the number of digits
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i,j] = ((matrix[i,j]*100)//1)/100
            
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
                        vmin = 1.5,
                        vmax = 5,
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
    
    ax.set_title(r'Mass Flow (kg.m.s$^{-1}$)', fontsize = 18,color='Black', y=1.06)  # Note title moves to make room for ticks   
    
    # heatmap.get_figure().savefig('PATH_SAVE')
    
    plt.show()
    
    # mpl.font_manager._rebuild()
    # print(matplotlib.matplotlib_fname())
    # print(matplotlib.get_cachedir())
