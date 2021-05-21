# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# CATHENA-DONJON Coupling level 1
##
# @file PyProcs_lvl1mTh.py 
#
# @author U. Le Tennier (March 2020), (rev. 02/2021 for CNL)
# 
# @brief PyProcs_lvl1mTh.py contains all the function used by the main coupling function Coupling_lvl2().
#
# Various functions are provided. The description of how they are chained is provided in IGE-379.pdf. 
# Some functions write specific information such as power or different parameter distributions in 
# CATHENA or DONJON inputs. Others read the information in both HISTORY and FUELMAP (DONJON structures) or in CATHENA outputs. 
# There is a total of 11 parameters measured. 7 of them are useful for coupling calculation : Power, upward coolant density (DCu)
# and temperature (TCu), downward coolant density (DCd) and temperature (TCd), fuel temperature (TF) and finally mass flow. 
# The other parameters are the inner/outer rods cladding surface temperature and inner/outer rods centerline temperature.
# 
# Because CATHENA models a quarter core and DONJON a full core, different arrays with different formats are used. 
# Some functions enable to switch from one format to another. Most of the time, arrays of 3 dimensions are used to handle parameters. 
# The first dimension states which parameter is considered (10 possibilities).
# The two others are related to the position of the assembly in the core. Because DONJON files can only contain 
# characters before column 72, it was chosen to limit the number of values on a line to 5. To be consistent with this limitation,
# most of the array have the following format (10xAx5). Their second dimension can have 336 or 1344 possibilities,
# respectively for a quarter or a full core. Besides, in some functions, the digits are managed to avoid any crash due to the 
# 72 characters limitation. 
#
# Mass flow distribution is handled differently because each channel has only one mass flow (because of steady-state simulations). 
# 84x1 arrays are used. Besides, CATHENA requires power per channel in addition with relative power sharing between every node of the 
# channel, which involves 84x20 arrays. Finally, functions to store and get parameter distributions in DISTRIBUTION directory, to check 
# convergence of both CATHENA et coupled calculation and to help convergence are provided. 
#
# To help convergence, a new distribution is created from the two previous calculations. By design, each channel has 
# fixed inlet/outlet coolant temperatures and densities. The solution provided by CATHENA faces those important restrictions,
# no exotic situation can happen. From iteration to iteration, distributions frequently oscilliate around a mean value.
# Therefore, when convergence helped is triggered, the new distributions are the mean distributions from the two previous calculations.
#
# To easily recover information from DONJON structures, ASCII functions are used. They need to be imported from PATH_PROC_PY.
# If the global architecture suggested in PyMain_lvl2mTh.py is properly implemented, ASCII functions are located in the same 
# directory as the present file. The code automatically finds the required path to make the import. If not, the exact path
# to the ASCII functions must be provided to PATH_PROC_PY variable in the section IMPORTS of the present file.   
# 
# @remarks
# Overall, functions inputs are written in capital letters, output have no capital letters and local 
# variables have some capital letters but not only. Boolean are used from python to python, if a binary information 
# has to be retrieved or given to CATHENA or DONJON, it will be as an integer : 0 or 1
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# IMPORTS
import os
import numpy as np 
from math import *

# Import files managing functions 
PATH_PROC_PY = os.path.dirname(__file__)
os.chdir(PATH_PROC_PY+'\\')

import ASCIIOpnv4 as ASCIIOpnv4
from ASCIIOpnv4 import *
import ASCIILibv4 as ASCIILibv4
from ASCIILibv4 import *
import ASCIIGetv4 as ASCIIGetv4
from ASCIIGetv4 import *
import ASCIILenv4 as ASCIILenv4
from ASCIILenv4 import *
import ASCIISixv4 as ASCIISixv4
from ASCIISixv4 import *

## Read the history to retrieve useful information \n \n
#   INPUTS \n
#       1) PATH_PROC_DJ ; str, absolute path to DJ directory \n
#       2) FILE_HISTORY ; str, name of the history file, should be "HISTORY.inp" \n \n
#   OUTPUTS \n
#       a) Reload     ; binary,  = 1 if reloading must be performed \n
#       b) CycleIndex ; int,     index of the current cycle or cycle to prepare \n
#       c) Step       ; int,     index of the calculation step \n
#       d) Out        ; binary,  = 1 all the calculation are done in DONJON \n
#       e) errors     ; boolean, = True if the wrong lines are considered  \n 
def readN1Flu(PATH_PROC_DJ,FILE_HISTORY):
    
    # inputs
    FileId = PATH_PROC_DJ+FILE_HISTORY
   
    # outputs 
    errors = False
    reload = 0    
    cycle  = 0
    step   = 0
    out    = 0
    
    (ilvl,RecordPos,RecordNumb,RecordName,CurRecInd) = ASCIIOpnv4(FileId) 
    
    leng1 = ASCIILenv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Step        ')
    Step  = ASCIIGetv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Step        ')
    step  = Step[leng1-1,0]
    
    leng2   = ASCIILenv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'CycleID     ')
    CycleID = ASCIIGetv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'CycleID     ')
    cycle   = CycleID[leng2-1,0]
    
    leng3  = ASCIILenv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Reload      ')
    Reload = ASCIIGetv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Reload      ')
    reload = Reload[leng3-1,0]
    
    leng4 = ASCIILenv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Out         ')
    Out   = ASCIIGetv4(FileId,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Out         ')
    out   = Out[leng4-1,0]
    
    
    return(reload,cycle,step,out,errors)

## Generate SCWR64N1Flu.x2m from its template to prepare the calculation at required Step \n  \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) FILE_FLU  ; str, name of the Flu.x2m file, should be 'SCWR64N1Flu.x2m' \n
#       3) Step      ; int, index of current calculation step \n
#       4) CycleRef  ; int, total number of cycles to simulate \n
#       5) TimeModel ; str, how to go through each cycle, available : "CANDU1" - "CANDU2" - "CANDU3" - "REP1" - "REP1b" - "REP2" \n
#       6) LoadModel ; str, which load model to be considered, 3 or 4 batches, available : "3c" - "4c" this information must match with the multicompos,
#                           available : "3c" - "4c" \n  \n
#   OUTPUTS \n
#       a) errors   ; boolean = True if the writing zone was not found \n
#       b) wentgood ; boolean = True if everything was written correctly \n
def writeN1Flu(PATH_EXEC,FILE_FLU,Step,CycleRef,TimeModel,LoadModel):
    
    # inputs
    FileId = PATH_EXEC+FILE_FLU
    Input1 = Step
    Input2 = CycleRef
    Input3 = TimeModel
    Input4 = LoadModel
    
    # outputs
    errors   = False
    wentgood = True
    
    # Find if the writing zone exists
    notfound     = True
    To_Found     = '* Interface write here please'
    Not_To_Found = '* Interface don t write anymore please'
    with open(FileId, 'r') as File:
        Lines = File.readlines()
        i = 1                                   
        
        while notfound :
            i+=1
            Not_To = Lines[i][0:38]
            To     = Lines[i][0:29]
            
            if To == To_Found :
                notfound = False
            if Not_To == Not_To_Found :
                errors = True 
                notfound = False 
            if i > 200 :
                errors = True
                notfound = False 
    
    if errors == False : # Writing zone exists, now prepare inputs  
        
        Input3 = '\"'+Input3+'\"'           # Add the quote marks 
        Input4 = '\"'+Input4+'\"'           # Add the quote marks 
    
        compl1 = 8
        compl2 = 8
        compl3 = 8
        compl4 = 5
        
        if Input1 > 1000  :
            compl1 = 5
        elif Input1 > 100 :
            compl1 = 6
        elif Input1 > 10  :
            compl1 = 7
        
        if Input2 > 1000  :
            compl2 = 5
        elif Input2 > 100 :
            compl2 = 6
        elif Input2 > 10  :
            compl2 = 7
        
        compl3 = 9 - len(Input3)
        
        Input1 = str(Input1)
        Input2 = str(Input2)
            
        Input1 += compl1 * ' ' +';'           
        Input2 += compl2 * ' ' +';'  
        Input3 += compl3 * ' ' +';'  
        Input4 += compl4 * ' ' +';'  
        
        # Inputs ready to be replaced 

        File2   = open(FileId, "rt")
        Changes = File2.read()
        Changes = Changes.replace('HERE1     ;', Input1)
        Changes = Changes.replace('HERE2     ;', Input2)
        Changes = Changes.replace('HERE3     ;', Input3)
        Changes = Changes.replace('HERE4     ;', Input4)
        File2.close()
        
        File2 = open(FileId, "wt")
        File2.write(Changes)
        File2.close()
                
        # Check if everything went good
    
        with open(FileId, 'r') as File3:
            Lines3 = File3.readlines()
            
            test = 'INTEGER Step      := '+Input1  
            if Lines3[i+1][0:len(test)] != test :
                wentgood = False 
                print('ok')
                
            test = 'INTEGER CycleRef  := '+Input2
            if Lines3[i+2][0:len(test)] != test :   
                wentgood = False  
                print('ok2')
                
            test = 'STRING TimeModel  := '+Input3
            if Lines3[i+4][0:len(test)] != test :   
                wentgood = False  
                print('ok3')
                
            test = 'STRING LoadModel  := '+Input4
            if Lines3[i+5][0:len(test)] != test :   
                wentgood = False  
                print('ok4')
                
    return(errors,wentgood)

## Generate SCWR64N1Relo.x2m from its template to prepare the new cycle, cycle index retrieved from HISTORY at Step \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) FILE_RELO ; str, name of the Relo.x2m file, should be 'SCWR64N1Relo.x2m' \n
#       3) Step      ; int, index of current calculation step \n
#       4) LoadModel ; str, which load model to be considered, 3 or 4 batches, available : "3c" - "4c" this information must match with the multicompos,
#                           available : "3c" - "4c" \n \n
#   OUTPUTS \n
#       a) errors   ; boolean = True if the writing zone was not found \n
def writeN1Relo(PATH_EXEC,FILE_RELO,Step,LoadModel):
    
    # inputs
    FileId = PATH_EXEC+FILE_RELO
    Input1 = Step
    Input2 = LoadModel
    
    # outputs
    errors   = False
    
    # Find if the writing zone exists
    notfound     = True
    To_Found     = '* Interface write here please'
    Not_To_Found = '* Interface don t write anymore please'
    with open(FileId, 'r') as File:
        Lines = File.readlines()
        i = 1                                   
        
        while notfound :
            i+=1
            Not_To = Lines[i][0:38]
            To     = Lines[i][0:29]
            
            if To == To_Found :
                notfound = False
            if Not_To == Not_To_Found :
                errors = True 
                notfound = False 
            if i > 200 :
                errors = True
                notfound = False 
    
    if errors == False : # Writing zone exists, now prepare inputs 
     
        Input2 = '\"'+Input2+'\"'           # Add the quote marks   
        
        compl1 = 8
        compl2 = 5    
        
        if Input1 > 1000  :
            compl1 = 5
        elif Input1 > 100 :
            compl1 = 6
        elif Input1 > 10  :
            compl1 = 7
            
        Input1 = str(Input1)
            
        Input1 += compl1 * ' ' +';'           
        Input2 += compl2 * ' ' +';'  
        
        # Inputs ready to be replaced 

        File2   = open(FileId, "rt")
        Changes = File2.read()
        Changes = Changes.replace('HERE1     ;', Input1)
        Changes = Changes.replace('HERE2     ;', Input2)
        File2.close()
        
        File2 = open(FileId, "wt")
        File2.write(Changes)
        File2.close()
                
        # Check if everything went good
    
        with open(FileId, 'r') as File3:
            Lines3 = File3.readlines()
            
            test = 'INTEGER Step      := '+Input1  
            if Lines3[i+1][0:len(test)] != test :
                errors = True 
                
            test = 'STRING LoadModel  := '+Input2
            if Lines3[i+3][0:len(test)] != test :   
                errors = True        
        
    
    return(errors)

## Generate SCWR64N1Upda.x2m from its template to update the local parameter INPUT1 retrieved from INPUT2 \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) FILE_UPDA ; str, name of the Upda.x2m file, should be 'SCWR64N1Upda.x2m' \n
#       3) ThermoP   ; str, which parameter to consider available : "CaloUp Dens" - "CaloUp Temp" - "CaloDw Dens" - "CaloDw Temp" - "Fuel Temp" \n
#       X) INPUTXX ; str (5), 5 distributions of the 5 ThermoP possibilities \n \n
#   OUTPUTS \n
#       a) errors   ; boolean = True if the writing zone was not found \n \n
#   IMPORTANT : THIS FUNCTION WILL COPY IN A DONJON INPUT FILE A SET OF LOCAL PARAMETERS, EACH DONJON LINE CAN CONTAIN A MAX OF 72 CHARACTERS. HERE, 960 LINES OF 7 VALUES ARE WRITTEN, IF EACH OF THE SEVEN VALUES HAS A LENGTH OF 9 CHARAC (ex: 1234567.9) THEN THE LINE WILL CONTAIN 70 CHARACTERS.
#   If CATHENA gives values with more than 8 digits, reshape internal variables Text and Li \n
def writeN1Upda(PATH_EXEC,FILE_UPDA,ThermoP,INPUTX1,INPUTX2,INPUTX3,INPUTX4,INPUTX5):
    
    # inputs
    #FileId  = PATH+'/'+FILE
    FileId  = PATH_EXEC+FILE_UPDA
    Input1  = ThermoP  
    InputX1 = INPUTX1 
    InputX2 = INPUTX2
    InputX3 = INPUTX3
    InputX4 = INPUTX4
    InputX5 = INPUTX5
    
    # outputs
    wentgood = True
    errors   = False
    
    # Find if the writing zone exists
    notfound     = True
    To_Found     = '* Interface write here please : '+Input1
    Not_To_Found = 'END: ;'
    
    with open(FileId, 'r') as File:
        Lines = File.readlines()
        i = 1                                   
        
        while notfound :
            i+=1
            To     = Lines[i][2:len(To_Found)+2]
            Not_To = Lines[i][0:len(Not_To_Found)]
            
            if To == To_Found :
                notfound = False
            if Not_To == Not_To_Found :
                errors = True 
                notfound = False 
        
    # Find which mark to replace 
    if   Input1 == 'CaloUp Dens':
        Mark = 'HERE1'
        Text = InputX1
    elif Input1 == 'CaloUp Temp':
        Mark = 'HERE2'
        Text = InputX2
    elif Input1 == 'CaloDw Dens':
        Mark = 'HERE3'
        Text = InputX3
    elif Input1 == 'CaloDw Temp':
        Mark = 'HERE4'
        Text = InputX4
    elif Input1 == 'Fuel Temp':
        Mark = 'HERE5'
        Text = InputX5
    
    if errors == False : # Writing zone exists, now prepare inputs         
        
        # put the lines where it is required
        File2   = open(FileId, "rt")
        Changes = File2.read()
        Changes = Changes.replace(Mark,Text)
        File2.close()
        
        File2 = open(FileId, "wt")
        File2.write(Changes)
        File2.close()
    
    return (errors)
 
## Retrieve power distribution from a FuelMap \n \n
#   INPUTS \n
#       1) PATH_EXEC    ; str, absolute path to execution directory \n
#       2) FILE_FMAP    ; str, name of the fuelmap file, should be "FMAP.out" \n
#       3) FILE_HISTORY ; str, name of the history file, should be "HISTORY.out" \n \n
#   OUTPUTS \n
#       a) param_dist   ; array (10*1344*5), power distribution, FuelMap format \n
#       b) errors       ; boolean = True if the writing zone was not found \n
def readN1Fmap(PATH_EXEC,FILE_FMAP,FILE_HISTORY):

    # inputs
    FileId1 = PATH_EXEC+FILE_FMAP
    FileId2 = PATH_EXEC+FILE_HISTORY
    
    # locals
    CorrCy = 0
    CorrSt = 0 
    
    # outputs
    param_dist      = np.zeros((10,1344,5))
    errors          = False
    
    # # Process history 
    (ilvl,RecordPos,RecordNumb,RecordName,CurRecInd) = ASCIIOpnv4(FileId2) 
    
    # Retrieve the CycleID and the step of the cycle to be considered
    leng3   = ASCIILenv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Reload      ')
    Reload  = ASCIIGetv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'Reload      ')
    reload  = int(Reload[leng3-1,0])
    
    if reload == 1 :
        CorrCy = 1
        CorrSt = 1
    
    # Retrieve the CycleID and the step of the cycle to be considered
    leng1   = ASCIILenv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'CycleID     ')
    CycleID = ASCIIGetv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'CycleID     ')
    cycle   = int(CycleID[leng1-1-CorrCy,0])
     
    leng2   = ASCIILenv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'StepCy      ')
    StepCy  = ASCIIGetv4(FileId2,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'StepCy      ')
    stepcy  = int(StepCy[leng2-1-CorrCy,0]) + CorrSt
    
    # Process FuelMap
    (ilvl,RecordPos,RecordNumb,RecordName,CurRecInd) = ASCIIOpnv4(FileId1) 
    
    SubDir      = 'Cycle'+str(cycle)+ (7-len(str(cycle)))*' '
    SubSubDir   = 'elt#' + '0'*(8 - len(str(stepcy)) ) + str(stepcy)
    
    #print(SubDir,SubSubDir)
 
    (ilvl,nbdata,CurRecInd) = ASCIISixv4(FileId1,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,SubDir,1)
    (ilvl,nbdata,CurRecInd) = ASCIISixv4(FileId1,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,SubSubDir,1)
    
    Power_Dist  = ASCIIGetv4(FileId1,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,'POWER-BUND  ')
        
    for i in range(1344):
        param_dist[0,i,0] = Power_Dist[(i)*5,0]
        param_dist[0,i,1] = Power_Dist[(i)*5+1,0]
        param_dist[0,i,2] = Power_Dist[(i)*5+2,0]
        param_dist[0,i,3] = Power_Dist[(i)*5+3,0]
        param_dist[0,i,4] = Power_Dist[(i)*5+4,0]
    
    return(param_dist,errors)

## Produce CATHENA input file from its template \n \n
#   INPUTS \n
#       1) PATH_EXEC  ; str, absolute path to execution directory \n
#       2) FILE_CATH  ; str, name of the fuelmap file, should be "FMAP.out" \n
#       3) Pwr_Chn    ; array (84*1),  total channel power of 4 equivalent channels, created by treatN1paramDC() \n
#       4) Pwr_Coeff  ; array (84*20), channel axial power distribution, created by treatN1paramDC() \n
#       5) MFlow_Dist ; float array (84*1),  flow mass rate distribution \n
#       6) TimeCath   ; float, execution time for CATHENA, by default 1500 \n \n
#   OUTPUTS \n
#       a) errors ; boolean = True if the writing zone was not found \n
def writeN1CATH(PATH_EXEC,FILE_CATH,Pwr_Chn,Pwr_Coeff,MFlow_Dist,TimeCath):
    
    # inputs
    FileId = PATH_EXEC+FILE_CATH
    Input1 = Pwr_Chn  
    Input2 = Pwr_Coeff 
    Input3 = MFlow_Dist
    Input4 = TimeCath
    
    # outputs
    errors   = False
    
    # Find if the writing zone exists 
    notfound     = True
    To_Found     = '\'HEAT TRANSFER PACKAGE\'/'
    Not_To_Found = '\'* ALL THERMAL MODELS DEFINED\' /'
    
    with open(FileId, 'r') as File: 
        Lines = File.readlines()
        i = 1                                   
        
        while notfound :
            i+=1
            To     = Lines[i][0:len(To_Found)]
            Not_To = Lines[i][0:len(Not_To_Found)]
            
            if To == To_Found :
                notfound = False
            if Not_To == Not_To_Found :
                errors = True 
                notfound = False 
                
    if errors == False :
        Mark00 = 'HERE00'

        # put the lines where it is required
        File2   = open(FileId, "rt")
        Changes = File2.read()
        Changes = Changes.replace(Mark00,str(Input4))
        File2.close()
            
        File2 = open(FileId, "wt")
        File2.write(Changes)
        File2.close()
        
        for i in range(84):
            MarkIn  = 'HERE'+str(i+1)+'IN'
            MarkOut = 'HERE'+str(i+1)+'OUT'
            MarkFlw = 'HEREMFL'+str(i+1)
            
            # create the strs         
            StrCo  = str(Input2[i,19])+','+str(Input2[i,18])+','+str(Input2[i,17])+','+str(Input2[i,16])+','+str(Input2[i,15])+','
            StrCo += str(Input2[i,14])+','+str(Input2[i,13])+','+str(Input2[i,12])+','+str(Input2[i,11])+','+str(Input2[i,10])+', \n'
            StrCo += str(Input2[i,9])+','+str(Input2[i,8])+','+str(Input2[i,7])+','+str(Input2[i,6])+','+str(Input2[i,5])+','
            StrCo += str(Input2[i,4])+','+str(Input2[i,3])+','+str(Input2[i,2])+','+str(Input2[i,1])+','+str(Input2[i,0])+'/'
            
            
            StrIn   = '\'HQ-SPACE:('+str(((Input1[i,0]*4*0.481)*100//10)/10000)+'E06)\'/ \n'
            StrIn  += '\'R-USER:(0.1111 0.3333 0.5556)\', , \'A-USER\', , / \n'
            StrIn  += StrCo   
                
            StrOut  = '\'HQ-SPACE:('+str(((Input1[i,0]*4*0.519)*100//10)/10000)+'E06)\'/ \n'
            StrOut += '\'R-USER:(0.1111 0.3333 0.5556)\', , \'A-USER\', , / \n'
            StrOut += StrCo
            
            StrMfl  = str(Input3[i,0])

            # put the lines where it is required
            File2   = open(FileId, "rt")
            Changes = File2.read()
            Changes = Changes.replace(MarkIn,StrIn)
            Changes = Changes.replace(MarkOut,StrOut)
            Changes = Changes.replace(MarkFlw,StrMfl)
            File2.close()
            
            File2 = open(FileId, "wt")
            File2.write(Changes)
            File2.close()
    
    return (errors)
  
## Retrieve thermal hydraulic distributions, updates Param_DistCa \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) ThermoP   ; str, which parameter to consider available : "CaloUp Dens" - "CaloUp Temp" - "CaloDw Dens" - "CaloDw Temp" - "Fuel Temp" \n
#       3) Param_DistCa ; array (10*336*5), 10 distributions of thermohydraulic parameters \n \n
#   OUTPUTS \n
#       a) param_distca ; array (10*336*5), parameter distribution, CATHENA format \n
#       b) errors   ; boolean = True if the writing zone was not found \n
def readN1CATH(PATH_EXEC,ThermoP,Param_DistCa):
    
    # inputs
    Input1 = ThermoP  
    Input2 = Param_DistCa 
    
    # outputs
    param_distca    = np.zeros((10,336,5))
    errors          = False 
    
    # local 
    count = 1 ;
    indmv = 0 ;   
    lin   = 0 ;
    col   = 0 ;
    ind   = 0 ;
    hom   = 1 ;
    aff   = 0 ;
    temp_fuel      = np.zeros((2,336,5))
    temp_fuelC     = np.zeros((2,336,5))
    temp_sheath    = np.zeros((2,336,5))
    
    # Find which mark to replace 
    if   Input1 == 'CaloUp Dens':
        File1 = 'DENSFLC1.RES'
        File2 = 'DENSFLC2.RES'
        File3 = 'DENSFLC3.RES'
        File4 = 'DENSFLC4.RES'
        
        ind    =  1 
        hom    =  0.1
        aff    =  0
        inpmax =  6.1
        inpmin =  0.56
        
    elif Input1 == 'CaloUp Temp':
        File1 = 'TEMPFLC1.RES'
        File2 = 'TEMPFLC2.RES'
        File3 = 'TEMPFLC3.RES'
        File4 = 'TEMPFLC4.RES'
        
        ind   =  2 
        hom   =  1
        aff   =  273.15
        inpmax =  826.0
        inpmin =  353.0
        
    elif Input1 == 'CaloDw Dens':
        File1 = 'DENSFLW1.RES'
        File2 = 'DENSFLW2.RES'
        File3 = 'DENSFLW3.RES'
        File4 = 'DENSFLW4.RES'
        
        ind   =  3 
        hom   =  0.1
        aff   =  0
        inpmax =  6.2
        inpmin =  2.4
        
    elif Input1 == 'CaloDw Temp': 
        File1 = 'TEMPFLW1.RES'
        File2 = 'TEMPFLW2.RES'
        File3 = 'TEMPFLW3.RES'
        File4 = 'TEMPFLW4.RES'
        
        ind   =  4 
        hom   =  1
        aff   =  273.15
        inpmax =  396.0
        inpmin =  352.0
        
    elif Input1 == 'Fuel Temp':
        File11 = 'TWALLI1.RES' 
        File21 = 'TWALLI2.RES'
        File31 = 'TWALLI3.RES'
        File41 = 'TWALLI4.RES'
        
        File11b = 'TWALLCI1.RES' 
        File21b = 'TWALLCI2.RES'
        File31b = 'TWALLCI3.RES'
        File41b = 'TWALLCI4.RES'
        
        File11c = 'TWALLSI1.RES' 
        File21c = 'TWALLSI2.RES'
        File31c = 'TWALLSI3.RES'
        File41c = 'TWALLSI4.RES'
        
        File12 = 'TWALLO1.RES'
        File22 = 'TWALLO2.RES'
        File32 = 'TWALLO3.RES'
        File42 = 'TWALLO4.RES'
        
        File12b = 'TWALLCO1.RES'
        File22b = 'TWALLCO2.RES'
        File32b = 'TWALLCO3.RES'
        File42b = 'TWALLCO4.RES'
        
        File12c = 'TWALLSO1.RES'
        File22c = 'TWALLSO2.RES'
        File32c = 'TWALLSO3.RES'
        File42c = 'TWALLSO4.RES'
        
        ind   =  5
        hom   =  1
        aff   =  273.15
        inpmax =  2126.0
        inpmin =  528.0
        
    else :
        errors = True 
    
    if errors == False :
        if ind != 5 :
            for x in range(1,5):
                if x == 1 :
                    #FileId = PATH+'/'+FILE1
                    FileId = PATH_EXEC+File1
                    
                elif x == 2 :
                    #FileId = PATH+'/'+FILE2
                    FileId = PATH_EXEC+File2
                    
                elif x == 3 :
                    #FileId = PATH+'/'+FILE3
                    FileId = PATH_EXEC+File3
                    
                else :
                    #FileId = PATH+'/'+FILE4
                    FileId = PATH_EXEC+File4
                    
                with open(FileId, 'r') as File:
                    Lines = File.readlines()
                    i = -210                            
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Lines[i][12:20])
                            param2 = float(Lines[i][22:30]) 
                            
                        else :
                            param1 = float(Lines[i][2:10])
                            param2 = float(Lines[i][12:20])  
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                        
                        if param1 < inpmin :
                            param1 = inpmin
                        elif param1 > inpmax :
                            param1 = inpmax
                            
                        
                        Input2[ind,lin,col] = hom * param1 + aff  
                        
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                        
                        if param2 < inpmin :
                            param2 = inpmin
                        elif param2 > inpmax :
                            param2 = inpmax
                            
                        col = indmv 
                        Input2[ind,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1
                    
        else :       
            for x in range(1,5) :
                if x == 1 :
                    FileId = PATH_EXEC+File11
                    
                elif x == 2 :
                    FileId = PATH_EXEC+File21
                    
                elif x == 3 :
                    FileId = PATH_EXEC+File31
                    
                else :
                    FileId = PATH_EXEC+File41
                    
                with open(FileId, 'r') as File:
                    Lines = File.readlines()
                    i = -210                       
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Lines[i][12:20])
                            param2 = float(Lines[i][22:30])  
                            
                        else :
                            param1 = float(Lines[i][2:10])
                            param2 = float(Lines[i][12:20])  
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                        
                        if param1 < inpmin :
                            param1 = inpmin
                        elif param1 > inpmax :
                            param1 = inpmax
                            
                        temp_fuel[0,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                        
                        if param2 < inpmin :
                            param2 = inpmin
                        elif param2 > inpmax :
                            param2 = inpmax
                            
                        temp_fuel[0,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1  
                        
            count = 1 ;
            indmv = 0 ;   
            lin   = 0 ;
            col   = 0 ;
                    
            for x in range(1,5) :
                if x == 1 :
                    FileIdb = PATH_EXEC+File11b
                    
                elif x == 2 :
                    FileIdb = PATH_EXEC+File21b
                    
                elif x == 3 :
                    FileIdb = PATH_EXEC+File31b
                    
                else :
                    FileIdb = PATH_EXEC+File41b  
                    
                     
                        
                with open(FileIdb, 'r') as File:
                    Linesb = File.readlines()
                    i = -210                       
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Linesb[i][12:20])
                            param2 = float(Linesb[i][22:30])  
                            
                        else :
                            param1 = float(Linesb[i][2:10])
                            param2 = float(Linesb[i][12:20])  
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_fuelC[0,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_fuelC[0,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1                  
                        
            count = 1 ;
            indmv = 0 ;   
            lin   = 0 ;
            col   = 0 ;     
                
            for x in range(1,5) :
                if x == 1 :
                    FileIdc = PATH_EXEC+File11c
                    
                elif x == 2 :
                    FileIdc = PATH_EXEC+File21c
                    
                elif x == 3 :
                    FileIdc = PATH_EXEC+File31c
                    
                else :
                    FileIdc = PATH_EXEC+File41c
                      
                        
                with open(FileIdc, 'r') as File:
                    Linesc = File.readlines()
                    i = -210                       
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Linesc[i][12:20])
                            param2 = float(Linesc[i][22:30])  
                            
                        else :
                            param1 = float(Linesc[i][2:10])
                            param2 = float(Linesc[i][12:20])  
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_sheath[0,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_sheath[0,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1   
                    
            count = 1 ;
            indmv = 0 ;   
            lin   = 0 ;
            col   = 0 ;   
                     
            for x in range(1,5) :
                if x == 1 :
                    FileId = PATH_EXEC+File12
                    
                elif x == 2 :
                    FileId = PATH_EXEC+File22
                    
                elif x == 3 :
                    FileId = PATH_EXEC+File32
                    
                else :
                    FileId = PATH_EXEC+File42
                    
                with open(FileId, 'r') as File:
                    Lines = File.readlines()
                    i = -210                                   
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Lines[i][12:20])
                            param2 = float(Lines[i][22:30])
                            
                        else :
                            param1 = float(Lines[i][2:10])
                            param2 = float(Lines[i][12:20])
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                        
                        if param1 < inpmin :
                            param1 = inpmin
                        elif param1 > inpmax :
                            param1 = inpmax
                            
                        temp_fuel[1,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                        
                        if param2 < inpmin :
                            param2 = inpmin
                        elif param2 > inpmax :
                            param2 = inpmax
                            
                        temp_fuel[1,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1  
                    
            count = 1 ;
            indmv = 0 ;   
            lin   = 0 ;
            col   = 0 ;  
                
            for x in range(1,5) :
                if x == 1 :
                    FileIdb = PATH_EXEC+File12b
                    
                elif x == 2 :
                    FileIdb = PATH_EXEC+File22b
                    
                elif x == 3 :
                    FileIdb = PATH_EXEC+File32b
                    
                else :
                    FileIdb = PATH_EXEC+File42b                
                
                with open(FileIdb, 'r') as File:
                    Linesb = File.readlines()
                    i = -210                                   
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Linesb[i][12:20])
                            param2 = float(Linesb[i][22:30])
                            
                        else :
                            param1 = float(Linesb[i][2:10])
                            param2 = float(Linesb[i][12:20])
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_fuelC[1,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_fuelC[1,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1
                        
            count = 1 ;
            indmv = 0 ;   
            lin   = 0 ;
            col   = 0 ; 
                
            for x in range(1,5) :
                if x == 1 :
                    FileIdc = PATH_EXEC+File12c
                    
                elif x == 2 :
                    FileIdc = PATH_EXEC+File22c
                    
                elif x == 3 :
                    FileIdc = PATH_EXEC+File32c
                    
                else :
                    FileIdc = PATH_EXEC+File42c                  
                
                with open(FileIdc, 'r') as File:
                    Linesc = File.readlines()
                    i = -210                                   
                
                    while i < 0 :            
                        
                        if i == -210 :                        
                            param1 = float(Linesc[i][12:20])
                            param2 = float(Linesc[i][22:30])
                            
                        else :
                            param1 = float(Linesc[i][2:10])
                            param2 = float(Linesc[i][12:20])
                    
                        count += 2 
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_sheath[1,lin,col] = hom * param1 + aff
                        indmv += 1
                        
                        if indmv == 5 :
                            indmv  = 0
                            lin   += 1 
                            
                        col = indmv 
                            
                        temp_sheath[1,lin,col] = hom * param2 + aff
                        
                        indmv += 1
                        i     += 1
            
            for j in range(336) :
                for k in range(5) :
                    Input2[ind,j,k] = (temp_fuel[0,j,k] + temp_fuel[1,j,k])/2
                    Input2[ind+1,j,k] = temp_fuelC[0,j,k]
                    Input2[ind+2,j,k] = temp_fuelC[1,j,k]
                    Input2[ind+3,j,k] = temp_sheath[0,j,k]
                    Input2[ind+4,j,k] = temp_sheath[1,j,k]
    
    param_distca = Input2
    return(param_distca,errors)

## Treat power distribution to make it consistent with CATHENA input \n \n
#   INPUTS \n
#       1) Param_Dist ; array (10*1344*5), parameter distribution, FuelMap format, retrieved from readN1Fmap() \n \n
#   OUTPUTS \n
#       a) pwr_chn    ; array (84*1),  total channel power of 4 equivalent channels \n
#       b) pwr_coeff  ; array (84*20), channel axial power distribution \n
def treatN1paramDC(Param_Dist_new):
    
    # inputs
    Input1 = Param_Dist_new  
    
    # outputs
    pwr_chn        = np.zeros((84,1))
    pwr_coeff      = np.zeros((84,20))
    
    # local 
    count = 0 ;
    index = 1 ;
    indmv = 1 ;   
    lin   = 0 ;
    col   = 0 ;
    
    sum   = 0 ;
        
    while count < 84 : 
                
        for i in range(20) :
            indmv = index + (i*336) 
            lin   = indmv // 5 
            col   = indmv - (lin*5) - 1
            
            if col < 0 :
                lin -= 1 
                col  = 4
             
            pwr_coeff[count,i] = Input1[0,lin,col]
            sum               += pwr_coeff[count,i]
                        
        index += 1 
        
        if index == 5 :
            index += 4
        elif index == 15 :
            index += 6 
        elif index == 29 :
            index += 8 
        elif index == 45 :
            index += 8 
        elif index == 62 :
            index += 9 
        elif index == 80 :
            index += 9 
        elif index == 99 :
            index += 10 
        elif index == 119 :
            index += 10 
        elif index == 139 :
            index += 10 

        pwr_chn[count,0] = sum 
        
        count += 1 
        sum    = 0
        
    for i in range(84) :
        for j in range(20) :
            pwr_coeff[i,j] = ((pwr_coeff[i,j]*1000000) // pwr_chn[i,0])/1000000 # Restricts the number of digits
        
    
    return(pwr_chn,pwr_coeff)

## Treat thermal hydraulic distributions to make it consistent with DONJON input and create str for final coupling outputs \n \n
#   INPUTS \n
#       1) Param_Dist   ; array (10*1344*5), parameter distribution, FuelMap format, retrieved from readN1Fmap() \n
#       2) Param_DistCa ; array (10*336*5), parameter distribution, CATHENA format \n \n
#   OUTPUTS \n
#       a) param_dist ; array (10*1344*5), parameter distribution, FuelMap format \n
#       b) DCu_coeff  ; str, upward densities temperature values (5 values per line) \n
#       c) TCu_coeff  ; str, upward coolant temperature values (5 values per line) \n 
#       d) DCd_coeff  ; str, downward densities temperature values(5 values per line) \n 
#       e) TCd_coeff  ; str, downward coolant temperature values (5 values per line) \n 
#       f) TF_coeff   ; str, fuel temperature values (5 values per line) \n 
#       g) TCI_coeff  ; str, inner ring fuel centerline temperature values (5 values per line) \n 
#       h) TCO_coeff  ; str, outer ring fuel centerline temperature values (5 values per line) \n 
#       i) TSi_coeff  ; str, inner ring fuel cladding temperature values (5 values per line) \n 
#       j) TSO_coeff  ; str, outer ring fuel cladding temperature values (5 values per line) \n
def treatN1paramCD(Param_Dist,Param_DistCa):  
    
    # inputs
    Input1 = Param_Dist  
    Input2 = Param_DistCa   
    
    # outputs
    param_dist     = np.zeros((10,1344,5))
    DCu_coeff      = ''
    TCu_coeff      = ''
    DCd_coeff      = ''
    TCd_coeff      = ''
    TF_coeff       = ''
    TFCI_coeff     = ''
    TFCO_coeff     = ''
    TSI_coeff      = ''
    TSO_coeff      = ''
    
    # local 
    count  = 1 ; # Maint count 
    countb = 1 ; # Count of horizontal sym. 
    countc = 1 ; # Count of vertical sym.  
    countd = 1 ; # Count of both sym.       
    index  = 1 ; 
    lin    = 0 ;
    col    = 0 ;
        
    for i in range(20):
        while count < 168 :

            # Management of the initial coords. (CATH) 
            x = (84 * i + index) // 5
            y = (84 * i + index - x * 5) - 1  
            
            if y < 0 :
                x    =   x - 1
                y    =   4  
            
            # Management of the final coords. (DONJON)
            if count < 5 :
                countb =   9 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 15 :
                countb =  29 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 29 :
                countb =  57 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 45 :
                countb =  89 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 62 :
                countb = 123 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 80 :
                countb = 159 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count <  99 :
                countb = 197 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 119 :
                countb = 237 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 139 :
                countb = 277 - count
                countd = 337 - count
                countc = 337 - countb 
                
            elif count < 159 :
                countb = 317 - count
                countd = 337 - count
                countc = 337 - countb 
            
            lin = (336 * i + count) // 5
            col = (336 * i + count - lin * 5) - 1   
            
            if col < 0 :
                lin  = lin - 1
                col  = 4

           

            Input1[1,lin,col] = (Input2[1,x,y]  * 1000 // 1) / 1000
            Input1[2,lin,col] = (Input2[2,x,y]  * 1000 // 1) / 1000
            Input1[3,lin,col] = (Input2[3,x,y]  * 1000 // 1) / 1000
            Input1[4,lin,col] = (Input2[4,x,y]  * 1000 // 1) / 1000
            Input1[5,lin,col] = (Input2[5,x,y]  * 1000 // 1) / 1000
            Input1[6,lin,col] = (Input2[6,x,y]  * 1000 // 1) / 1000
            Input1[7,lin,col] = (Input2[7,x,y]  * 1000 // 1) / 1000
            Input1[8,lin,col] = (Input2[8,x,y]  * 1000 // 1) / 1000
            Input1[9,lin,col] = (Input2[9,x,y]  * 1000 // 1) / 1000
            
            
            # Management of the final coords. (DONJON)
            lin = (336 * i + countb) // 5
            col = (336 * i + countb - lin * 5) - 1    
            
            if col < 0 :
                lin  = lin - 1
                col  = 4
            
            Input1[1,lin,col] = (Input2[1,x,y] * 1000 // 1) / 1000
            Input1[2,lin,col] = (Input2[2,x,y] * 1000 // 1) / 1000 
            Input1[3,lin,col] = (Input2[3,x,y] * 1000 // 1) / 1000 
            Input1[4,lin,col] = (Input2[4,x,y] * 1000 // 1) / 1000 
            Input1[5,lin,col] = (Input2[5,x,y] * 1000 // 1) / 1000
            Input1[6,lin,col] = (Input2[6,x,y] * 1000 // 1) / 1000 
            Input1[7,lin,col] = (Input2[7,x,y] * 1000 // 1) / 1000  
            Input1[8,lin,col] = (Input2[8,x,y] * 1000 // 1) / 1000 
            Input1[9,lin,col] = (Input2[9,x,y] * 1000 // 1) / 1000  
                
            # Management of the final coords. (DONJON)
            lin = (336 * i + countc) // 5
            col = (336 * i + countc - lin * 5) - 1    
            
            if col < 0 :
                lin  = lin - 1
                col  = 4
            
            Input1[1,lin,col] = (Input2[1,x,y] * 1000 // 1) / 1000
            Input1[2,lin,col] = (Input2[2,x,y] * 1000 // 1) / 1000
            Input1[3,lin,col] = (Input2[3,x,y] * 1000 // 1) / 1000
            Input1[4,lin,col] = (Input2[4,x,y] * 1000 // 1) / 1000
            Input1[5,lin,col] = (Input2[5,x,y] * 1000 // 1) / 1000
            Input1[6,lin,col] = (Input2[6,x,y] * 1000 // 1) / 1000
            Input1[7,lin,col] = (Input2[7,x,y] * 1000 // 1) / 1000
            Input1[8,lin,col] = (Input2[8,x,y] * 1000 // 1) / 1000
            Input1[9,lin,col] = (Input2[9,x,y] * 1000 // 1) / 1000
                
            # Management of the final coords. (DONJON)
            lin = (336 * i + countd) // 5
            col = (336 * i + countd - lin * 5) - 1    
            
            if col < 0 :
                lin  = lin - 1
                col  = 4
            
            Input1[1,lin,col] = (Input2[1,x,y]  * 1000 // 1) / 1000
            Input1[2,lin,col] = (Input2[2,x,y]  * 1000 // 1) / 1000
            Input1[3,lin,col] = (Input2[3,x,y]  * 1000 // 1) / 1000
            Input1[4,lin,col] = (Input2[4,x,y]  * 1000 // 1) / 1000
            Input1[5,lin,col] = (Input2[5,x,y]  * 1000 // 1) / 1000
            Input1[6,lin,col] = (Input2[6,x,y]  * 1000 // 1) / 1000
            Input1[7,lin,col] = (Input2[7,x,y]  * 1000 // 1) / 1000
            Input1[8,lin,col] = (Input2[8,x,y]  * 1000 // 1) / 1000
            Input1[9,lin,col] = (Input2[9,x,y]  * 1000 // 1) / 1000
                
            if count == 4 :
                count += 4 
                
            elif count == 14 :
                count += 6 
                
            elif count == 28 :
                count += 8 
                
            elif count == 44 :
                count += 8 
                
            elif count == 61 :
                count += 9 
                
            elif count == 79 :
                count += 9
                
            elif count == 98 :
                count += 10
                
            elif count == 118 :
                count += 10
                
            elif count == 138 :
                count += 10
                
            elif count == 158 :
                count += 10
                
            index += 1    
            count += 1
        
        count = 1
        index = 1
            
    
    param_dist = Input1
    
    for s in range(1344):
        DCu_coeff  += str(param_dist[1,s,0])+' '+str(param_dist[1,s,1])+' '+str(param_dist[1,s,2])+' '+str(param_dist[1,s,3])+' '+str(param_dist[1,s,4])+' '+' \n'
        TCu_coeff  += str(param_dist[2,s,0])+' '+str(param_dist[2,s,1])+' '+str(param_dist[2,s,2])+' '+str(param_dist[2,s,3])+' '+str(param_dist[2,s,4])+' '+' \n'
        DCd_coeff  += str(param_dist[3,s,0])+' '+str(param_dist[3,s,1])+' '+str(param_dist[3,s,2])+' '+str(param_dist[3,s,3])+' '+str(param_dist[3,s,4])+' '+' \n'
        TCd_coeff  += str(param_dist[4,s,0])+' '+str(param_dist[4,s,1])+' '+str(param_dist[4,s,2])+' '+str(param_dist[4,s,3])+' '+str(param_dist[4,s,4])+' '+' \n'
        TF_coeff   += str(param_dist[5,s,0])+' '+str(param_dist[5,s,1])+' '+str(param_dist[5,s,2])+' '+str(param_dist[5,s,3])+' '+str(param_dist[5,s,4])+' '+' \n'
        TFCI_coeff += str(param_dist[6,s,0])+' '+str(param_dist[6,s,1])+' '+str(param_dist[6,s,2])+' '+str(param_dist[6,s,3])+' '+str(param_dist[6,s,4])+' '+' \n'
        TFCO_coeff += str(param_dist[7,s,0])+' '+str(param_dist[7,s,1])+' '+str(param_dist[7,s,2])+' '+str(param_dist[7,s,3])+' '+str(param_dist[7,s,4])+' '+' \n'
        TSI_coeff  += str(param_dist[8,s,0])+' '+str(param_dist[8,s,1])+' '+str(param_dist[8,s,2])+' '+str(param_dist[8,s,3])+' '+str(param_dist[8,s,4])+' '+' \n'
        TSO_coeff  += str(param_dist[9,s,0])+' '+str(param_dist[9,s,1])+' '+str(param_dist[9,s,2])+' '+str(param_dist[9,s,3])+' '+str(param_dist[9,s,4])+' '+' \n'
    
    return(param_dist,DCu_coeff,TCu_coeff,DCd_coeff,TCd_coeff,TF_coeff,TFCI_coeff,TFCO_coeff,TSI_coeff,TSO_coeff)
    
## Assess if the CATHENA simulation converged and create str for final coupling outputs (mass flow only) \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) FILE_CONV ; str, name of the fuelmap file, should be "CONV.RES" \n
#       3) FILE_MFLO ; str, name of the mass flow file, should be "MFLOW.RES" \n
#       4) IncConvC  ; float, convergence criteria (kg/s) for the CATHENA simulations \n \n
#   OUTPUTS \n
#       a) convc         ; boolean     , = True if the CATHENA calculation converged \n
#       b) MaxCat        ; float       , = Maximum (absolute) discrepancy in a channel \n
#       c) MassFLW_dist  ; array (84*1), mass flow distribution \n
#       d) MassFLW_coeff ; str         , mass flow values (5 values per line) \n
#       e) errors        ; boolean = True if the reading zones were not found \n
def checkN1convcath(PATH_EXEC,FILE_CONV,FILE_MFLO,IncConvC):
    
    # inputs
    Input1 = IncConvC  
    
    FileId = PATH_EXEC+FILE_CONV 
    FileIdb = PATH_EXEC+FILE_MFLO
    
    # outputs
    convc    = True 
    errors   = False
    MaxCat   = 0.
    MassFLW  = np.zeros((84,1))
    MassFLW_coeff = ''
    
    with open(FileId, 'r') as File:
        Lines = File.readlines()
        i = -249                                   
    
        while i < 0 and convc == True :            
            
            if i == -249 :                        
                flwrate1 = float(Lines[i][14:20])
                flwrate2 = float(Lines[i][24:30])
                
            else :
                flwrate1 = float(Lines[i][4:10])
                flwrate2 = float(Lines[i][14:20])

            flwrate3 = float(Lines[i+1][4:10])
            flwrate4 = float(Lines[i+1][14:20])
            flwrate5 = float(Lines[i+2][4:10])
            flwrate6 = float(Lines[i+2][14:20])
                
            if abs(flwrate1 - flwrate2) > Input1 :
                convc = False
                if abs(flwrate1 - flwrate2) > MaxCat :
                    MaxCat = abs(flwrate1 - flwrate2)
                
            elif abs(flwrate2 - flwrate3) > Input1 :
                convc = False
                if abs(flwrate2 - flwrate3) > MaxCat :
                    MaxCat = abs(flwrate2 - flwrate3)
                
            elif abs(flwrate3 - flwrate4) > Input1  :
                convc = False
                if abs(flwrate3 - flwrate4) > MaxCat :
                    MaxCat = abs(flwrate3 - flwrate4)
                
            elif abs(flwrate4 - flwrate5) > Input1 :
                convc = False
                if abs(flwrate4 - flwrate5) > MaxCat :
                    MaxCat = abs(flwrate4 - flwrate5)
                
            elif abs(flwrate5 - flwrate6) > Input1 :
                convc = False
                if abs(flwrate5 - flwrate6) > MaxCat :
                    MaxCat = abs(flwrate5 - flwrate6)
        
            i += 3 
    
    with open(FileIdb, 'r') as File:
        Linesb = File.readlines()
        i = -42       
        j =   0
    
        while i < 0 :            
            
            if i == -42 :                        
                flwrate1 = float(Linesb[i][14:20])
                flwrate2 = float(Linesb[i][24:30])
                
            else :
                flwrate1 = float(Linesb[i][4:10])
                flwrate2 = float(Linesb[i][14:20])
            
            MassFLW[j,0]   = flwrate1
            MassFLW[j+1,0] = flwrate2
                
            MassFLW_coeff = MassFLW_coeff +str(flwrate1)+'  \n'+str(flwrate2)+'  \n'
            
            i += 1
            j += 2
            
            
    return(convc,MaxCat,MassFLW,MassFLW_coeff,errors)
    
## Compare two consecutive distributions to assess if the simulation converged or not \n \n
#   INPUTS \n
#       1) Param_Dist     ; array (10*1344*5), old parameter distribution, FuelMap format \n
#       2) Param_Dist_new ; array (10*1344*5), new parameter distribution, FuelMap format, retrieved from readN1Fmap() \n \n
#       3) IncConvC       ; float, convergence criteria (kW) for simulation \n
#   OUTPUTS \n
#       a) convc    ; boolean, = True if the distributions converged \n
#       b) maxP     ; float  , Max mean squared difference between powers of 2 channels \n
#       c) maxTCu   ; float  , Max absolute difference between 2 TCu \n
#       d) maxTCd   ; float  , Max absolute difference between 2 TCd \n
#       e) maxTF    ; float  , Max absolute difference between 2 TF \n
def checkN1convdist(Param_Dist,Param_Dist_new,IncConvD) :
    
    # inputs
    Input1 = Param_Dist
    Input2 = Param_Dist_new
    Input3 = IncConvD
    
    # outputs
    convD    = False 
    maxP     = 0.
    maxTCu   = 0. 
    maxTCd   = 0.
    maxTF    = 0.
    
    # local
    Diff = np.zeros((4,1344,5))
    Chan = np.zeros((2,20,336))
    MSE1 = np.zeros((1,336))
    
    for i in range(1344):
        for j in range(5):
            Diff[0,i,j] = abs(Input1[0,i,j]-Input2[0,i,j]) 
            Diff[1,i,j] = abs(Input1[2,i,j]-Input2[2,i,j])
            Diff[2,i,j] = abs(Input1[4,i,j]-Input2[4,i,j])
            Diff[3,i,j] = abs(Input1[5,i,j]-Input2[5,i,j]) 
            
            if Diff[0,i,j] > maxP :
                maxP = Diff[0,i,j]
            
            if Diff[1,i,j] > maxTCu :
                maxTCu = Diff[1,i,j]
            
            if Diff[2,i,j] > maxTCd :
                maxTCd = Diff[2,i,j]
            
            if Diff[3,i,j] > maxTF :
                maxTF = Diff[3,i,j]
    
    # Calculation of the Mean Squared Error on power
    col = 0 
    lin = 0
    
    for z in range(20):
        for k in range(336):
            Chan[0,z,k] = Input1[0,lin,col]
            Chan[1,z,k] = Input2[0,lin,col]
            
            col += 1
            
            if col == 5 :
                lin += 1 
                col  = 0
                
    for g in range(336):
        sum1 = 0
        
        for z in range(20):
            sum1 += (Chan[0,z,g]-Chan[1,z,g])**2
        
        sum1 = sqrt(sum1/20)
        MSE1[0,g] = sum1 
        
    maxP = np.amax(MSE1)
    
    if maxP < Input3 :
        convD = True 
        
    return(convD,maxP,maxTCu,maxTCd,maxTF)

## Calculate the mean value of 2 sets of distributions \n \n
#   INPUTS \n
#       1) Param_Dist     ; array (10*1344*5), old parameter distribution, FuelMap format \n
#       2) Param_Dist_new ; array (10*1344*5), new parameter distribution, FuelMap format, retrieved from readN1Fmap() \n \n
#   OUTPUTS \n
#       a) param_dist ; array (10*1344*5), parameter distribution, FuelMap format \n
#       b) DCu_coeff  ; str, upward densities temperature values (5 values per line) \n
#       c) TCu_coeff  ; str, upward coolant temperature values (5 values per line) \n
#       d) DCd_coeff  ; str, downward densities temperature values(5 values per line) \n
#       e) TCd_coeff  ; str, downward coolant temperature values (5 values per line) \n
#       f) TF_coeff   ; str, fuel temperature values (5 values per line) \n
#       g) TCI_coeff  ; str, inner ring fuel centerline temperature values (5 values per line) \n
#       h) TCO_coeff  ; str, outer ring fuel centerline temperature values (5 values per line) \n
#       i) TSi_coeff  ; str, inner ring fuel cladding temperature values (5 values per line) \n
#       j) TSO_coeff  ; str, outer ring fuel cladding temperature values (5 values per line) \n
def helpconv(Param_Dist,Param_Dist_new) :
    
    # inputs
    Input1 = Param_Dist  
    Input2 = Param_Dist_new   
    
    # outputs
    param_dist     = np.zeros((10,1344,5))
    DCu_coeff      = ''
    TCu_coeff      = ''
    DCd_coeff      = ''
    TCd_coeff      = ''
    TF_coeff       = ''
    TFCI_coeff     = ''
    TFCO_coeff     = ''
    TSI_coeff      = ''
    TSO_coeff      = ''
    
    param_dist = ((Input1 + Input2)/2 * 1000 // 1) / 1000
    
    for s in range(1344):
        DCu_coeff  += str(param_dist[1,s,0])+' '+str(param_dist[1,s,1])+' '+str(param_dist[1,s,2])+' '+str(param_dist[1,s,3])+' '+str(param_dist[1,s,4])+' '+' \n'
        TCu_coeff  += str(param_dist[2,s,0])+' '+str(param_dist[2,s,1])+' '+str(param_dist[2,s,2])+' '+str(param_dist[2,s,3])+' '+str(param_dist[2,s,4])+' '+' \n'
        DCd_coeff  += str(param_dist[3,s,0])+' '+str(param_dist[3,s,1])+' '+str(param_dist[3,s,2])+' '+str(param_dist[3,s,3])+' '+str(param_dist[3,s,4])+' '+' \n'
        TCd_coeff  += str(param_dist[4,s,0])+' '+str(param_dist[4,s,1])+' '+str(param_dist[4,s,2])+' '+str(param_dist[4,s,3])+' '+str(param_dist[4,s,4])+' '+' \n'
        TF_coeff   += str(param_dist[5,s,0])+' '+str(param_dist[5,s,1])+' '+str(param_dist[5,s,2])+' '+str(param_dist[5,s,3])+' '+str(param_dist[5,s,4])+' '+' \n'
        TFCI_coeff += str(param_dist[6,s,0])+' '+str(param_dist[6,s,1])+' '+str(param_dist[6,s,2])+' '+str(param_dist[6,s,3])+' '+str(param_dist[6,s,4])+' '+' \n'
        TFCO_coeff += str(param_dist[7,s,0])+' '+str(param_dist[7,s,1])+' '+str(param_dist[7,s,2])+' '+str(param_dist[7,s,3])+' '+str(param_dist[7,s,4])+' '+' \n'
        TSI_coeff  += str(param_dist[8,s,0])+' '+str(param_dist[8,s,1])+' '+str(param_dist[8,s,2])+' '+str(param_dist[8,s,3])+' '+str(param_dist[8,s,4])+' '+' \n'
        TSO_coeff  += str(param_dist[9,s,0])+' '+str(param_dist[9,s,1])+' '+str(param_dist[9,s,2])+' '+str(param_dist[9,s,3])+' '+str(param_dist[9,s,4])+' '+' \n'
    
    return(param_dist,DCu_coeff,TCu_coeff,DCd_coeff,TCd_coeff,TF_coeff,TFCI_coeff,TFCO_coeff,TSI_coeff,TSO_coeff)
    
## Store the converged solution (thermal-hydraulics parameters distributions) into DISTRIBUTION directory,
#  each file in DISTRIBUTION contains one parameter distribution at only one step, file names as "Dist_PARAM_Step" \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) ThermoP   ; str, which parameter to consider available : "CaloUp Dens" - "CaloUp Temp" - "CaloDw Dens" - "CaloDw Temp" - "Fuel Temp" -"Fuel   Temp" - "Fuel CITemp" - "Fuel COTemp" - "ISheathTemp" - "OSheathTemp" - "MassFlow   "   \n
#       3) Step      ; int, index of current calculation step \n
#       4) LoadModel ; str, which load model to be considered, 3 or 4 batches, available : "3c" - "4c" this information must match with the multicompos,
#                           available : "3c" - "4c" \n
#       5) XXX_coeff  ; str, ThermoP parameter values (5 values per line), must match with ThermoP \n
def stockN1dist(PATH_EXEC,ThermoP,Step,LoadModel,XXX_coeff): 
    
    # inputs
    Input1 = ThermoP  
    Input2 = Step  
    Input3 = LoadModel  
    Input4 = XXX_coeff  
    
    # local 
    cstep  = 0  ;
    param  = '' ;
    cleng  = 0  ;
    
    # Find which file extension to replace 
    if   Input1 == 'CaloUp Dens':
        param  = 'Dist_DCu_'
        
    elif Input1 == 'CaloUp Temp':
        param = 'Dist_TCu_'
        
    elif Input1 == 'CaloDw Dens':
        param = 'Dist_DCd_'
        
    elif Input1 == 'CaloDw Temp': 
        param = 'Dist_TCd_'
        
    elif Input1 == 'Fuel   Temp': 
        param = 'Dist_TF_'
        
    elif Input1 == 'Fuel CITemp': 
        param = 'Dist_TCI_'
        
    elif Input1 == 'Fuel COTemp': 
        param = 'Dist_TCO_'
        
    elif Input1 == 'ISheathTemp': 
        param = 'Dist_TSI'
        
    elif Input1 == 'OSheathTemp': 
        param = 'Dist_TSO'
        
    elif Input1 == 'MassFlow   ': 
        param = 'Dist_MF_'
    
    if   Input3 == "3c":
        cleng = 22
    elif Input3 == "4c":
        cleng = 18
    
    cstep = Input2%cleng
    
    if cstep == 0 :
        cstep = cleng

    with open(PATH_EXEC+'DISTRIBUTION\\'+param+str(cstep)+'.inp', 'w') as File:
        File.write(Input4)     
    
    return()

## Retrieve the converged solution (thermal-hydraulics parameters distributions) from DISTRIBUTION directory \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) ThermoP   ; str, which parameter to consider available : "CaloUp Dens" - "CaloUp Temp" - "CaloDw Dens" - "CaloDw Temp" - "Fuel Temp" -"Fuel   Temp" - "Fuel CITemp" - "Fuel COTemp" - "ISheathTemp" - "OSheathTemp" - "MassFlow   "   \n
#       3) Step      ; int, index of current calculation step \n
#       4) LoadModel ; str, which load model to be considered, 3 or 4 batches, available : "3c" - "4c" this information must match with the multicompos,
#                           available : "3c" - "4c" \n \n
#   OUTPUTS \n
#       a) xxx_coeff  ; str, ThermoP parameter values (5 values per line), must match with ThermoP \n
def getN1dist(PATH_EXEC,ThermoP,Step,LoadModel):
    
    # inputs
    Input1 = ThermoP  
    Input2 = Step  
    Input3 = LoadModel  
    
    # outputs
    errors        = False 
    xxx_coeff     = ''
    
    # local 
    cstep  = 0  ;
    param  = '' ;
    cleng  = 0  ;
    
    # Find which file extension to replace 
    if   Input1 == 'CaloUp Dens':
        param  = 'Dist_DCu_'
        
    elif Input1 == 'CaloUp Temp':
        param = 'Dist_TCu_'
        
    elif Input1 == 'CaloDw Dens':
        param = 'Dist_DCd_'
        
    elif Input1 == 'CaloDw Temp': 
        param = 'Dist_TCd_'
        
    elif Input1 == 'Fuel   Temp': 
        param = 'Dist_TF_'
    
    if   Input3 == "3c":
        cleng = 22
    elif Input3 == "4c":
        cleng = 18
    
    cstep = Input2%cleng
    
    if cstep == 0 :
        cstep = cleng

    with open(PATH_EXEC+'DISTRIBUTION\\'+param+str(cstep)+'.inp', 'rb') as File:
        Lines    = File.read().splitlines()
        File.seek(0,0)
        
        for i in range(len(Lines)):
            xxx_coeff += Lines[i].decode("utf-8")+'\n'

    return(xxx_coeff,errors)

## Retrieve the converged solution (mass flow distribution) from DISTRIBUTION directory \n \n
#   INPUTS \n
#       1) PATH_EXEC ; str, absolute path to execution directory \n
#       2) Step      ; int, index of current calculation step \n
#       3) LoadModel ; str, which load model to be considered, 3 or 4 batches, available : "3c" - "4c" this information must match with the multicompos,
#                           available : "3c" - "4c" \n \n
#   OUTPUTS \n
#       a) MFlow_dist  ; array (84,1), mass flow distribution \n
def getN1mflw(PATH_EXEC,INPUT1,INPUT2):
    
    # inputs
    Input1 = INPUT1  
    Input2 = INPUT2  
    
    # outputs
    errors          = False 
    MFlow_dist      = np.zeros((84,1))
    
    # local 
    cstep  = 0  ;
    cleng  = 0  ;
    
    # Find which file extension to replace 
    
    param  = 'Dist_MF_' 
    if   Input2 == "3c":
        cleng = 22
    elif Input2 == "4c":
        cleng = 18
    
    cstep = Input1%cleng
    
    if cstep == 0 :
        cstep = cleng

    with open(PATH_EXEC+'DISTRIBUTION\\'+param+str(cstep)+'.inp', 'rb') as File:
        Lines    = File.read().splitlines()
        File.seek(0,0)
        
        for i in range(len(Lines)):
            MFlow_dist[i] += float(Lines[i].decode("utf-8"))

    return(MFlow_dist,errors)



# END