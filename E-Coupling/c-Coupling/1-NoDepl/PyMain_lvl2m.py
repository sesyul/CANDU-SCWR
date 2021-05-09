# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# CATHENA-DONJON Coupling level 2
#
# Python main function 
#
# Author : U. Le Tennier (March 2020), revised in February 2021 for CNL
#
# General informations :
#
# PyMain_lvl2m.py contains the code that performs coupling level 2. It uses file managing functions 
#                 available in PyProcs_lvl1m. The algorithm is presented in CouplingAlgo.pdf. This file
#                 provides the function Coupling_lvl2 which performs the coupling. The global 
#                 architecture of the environment required is specified hereafter. This function
#                 does not take into account the impact of reloading on Th233, Pa233 and U233, contrarily 
#                 to PyMain_lvl2mTh.py.
#
# To set up the environment :
#
# Before executing Coupling_lvl2, execution directory path "# Import files managing functions" 
# (after the basic imports such as "os" or "shutil") and "# Execution" (at the end of the file) 
# must be changed to agree with the environment. The user must choose or create a directory where 
# the execution will take place (so called EXEC_DIRECTORY). In this directory, several elements 
# will be placed, they are described hereafter in the section "Global architecture of directories". 
# Besides, PyProcs_lvl1m must also be provided a path (just after the initial comments) to retrieve 
# Fortran files managing functions (called "Function of Donjon output management"). The last line of this
# file is a call to Coupling_lvl2 which is a comment line. To execute the function, remove the comment mark
# and execute the file, the coupling will begin
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Global architecture of directories :
#
# Hereafter, a description of the directories and how they must be filled by the user,
#   are referred as "frozen file" the files that will not be updated by the coupling
#
# A) EXEC_DIRECTORY                    # Where the magic happens, REFERRED AS PATH_EXEC
#
#   a) Store_CATHENA                   # REFERRED AS PATH_PROC_CA (here is PATH_EXEC\\CA)
#       1) TEMPLATE_CATH               # Pre-filled CATHENA Input file
#
#   b) Store_DONJON                    # REFERRED AS PATH_PROC_DJ (here is PATH_EXEC\\DJ)
#       1) TEMPLATE_SCWR64N1Flu        # Pre-filled DONJON Input file, flux calculation
#       2) TEMPLATE_SCWR64N1Relo       # Pre-filled DONJON Input file, reloading
#       3) TEMPLATE_SCWR64N1Upda       # Pre-filled DONJON Input file, update fuelmap
#       4) SCWR64N1Crit.c2m            # Procedure called by SCWR64N1Flu     
#       5) SCWR64N1MacU.c2m            # Procedure called by SCWR64N1Crit.c2m       
#       6) FMAP      (*)               # FuelMap  to be replaced when updated
#       7) HISTORY   (*)               # History to be replaced when updated
#       8) GEOCORE   (*)               # Geometry of the core   , frozen file
#       9) MATEX     (*)               # Matex                  , frozen file 
#      10) TRACK     (*)               # Tracking of the core   , frozen file
#      11) MACRORFL  (*)               # Macrolib of reflector  , frozen file
#      12) FMAP0     (*)               # Initial FuelMap (copy) , frozen file 
#      13) HISTORY0  (*)               # Initial History (copy) , frozen file 
#      14) DBREFXXxX (*)               # Databases              , frozen file
#
#   c) Store_PY
#       1) PyMain_lvl2m.py (the present file you are reading)
#       2) PyProcs_lvl1m.py            # Different functions called by PyMain_lvl2m.py
#       3) ASCIIGetv4.py               # Function of Donjon output management
#       4) ASCIILenv4.py               # Function of Donjon output management
#       5) ASCIILibv4.py               # Function of Donjon output management
#       6) ASCIIOpnv4.py               # Function of Donjon output management
#       7) ASCIISixv4.py               # Function of Donjon output management
#
#   c) DISTRIBUTION (some results will be stockpiled there to ensure the calculation could be
#                    restarted anytime from its stopping point)
#
#   e) donjon.exe                      # DONJON  executable 
#   f) cat3_6_1_1-b01.exe              # CATHENA executable
#   g) rdonjon5.bat                    # DONJON  execution tool
#
#   Notes : - If a different name is used for one of the e) f) or g) item, Coupling_lvl2 must
#                       must be updated (look and find for the items in the code and replace their 
#                       name by the accurate one)  
#           - Files with (*) are inherited of stability calculation, the initial HISTORY 
#                       is empty and the initial FMAP contains the simulated cycles used to 
#                       reach stability
#           - DBREFXXxX are the cross sections databases, there are at least 3 but could be 9 depending on 
#                       the calculation intended (DD or not DD)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#          
# X) Coupling_lvl2(PATH_EXEC,PATH_PROC_DJ,PATH_PROC_CA,INPUT1,INPUT2,INPUT3,INPUT4,INPUT5,INPUT6) = (a,b...)         
#       Write at the top of SCWR64N1Flu.x2m to prepare the calculation at Step X 
#
#       -> PATH_EXEC     : absolute path where to execute all the operations (#magic)
#       -> PATH_PROC_DJ  : absolute path where DONJON  files are stored
#       -> PATH_PROC_CA  : absolute path where CATHENA files are stored
#       -> INPUT1 : Step      (X)         ; int, 
#       -> INPUT2 : CycleRef  (Y)         ; int, number of cycles to simulate
#       -> INPUT3 : TimeModel (REP/CAN)   ; str, how to go through each cycle 
#                                           available : "CANDU1" - "CANDU2" - "CANDU3" - "REP1" - "REP1b" - "REP2"
#       -> INPUT4 : LoadModel ("3c"/"4c") ; str, which load model to be considered, 3 or 4 cycles,
#                                           available : "3c" - "4c" 
#                                           this information must match with the multicompo in input
#       -> INPUT5 : IncConvC  (x.x) (kg/s); float, convergence criteria for the CATHENA simulations
#       -> INPUT6 : IncConvD  (y.y) (kW)  ; float, convergence criteria for the coupled simulations 
#                                                  (by default applied to power but a quick change 
#                                                   in checkN1convdist() in PyProcs_lvl1m.py can be
#                                                   done to enable convergence to rely on a different 
#                                                   parameter)
#
#           a) Exec_report  ; text file, copied in the execution directory when simulation is over
#                             contains notes on calculations made by the main during its execution.
#                             It is where to look when an error is triggered.
#                             Gives total time of execution (evaluated with START and END (both equal to time.time()))  
#                             Gives times of execution of each call to CATHENA and DONJON (with start and end, from time.time())     
#           b) Param_DistX  ; text file, contains distribution of thermalhydraulic parameters and power distribution over time.
#                             Only written when normal end of execution happens 
#                             X = A ; CaloUp Dens
#                             X = B ; CaloUp Temp
#                             X = C ; CaloDw Dens
#                             X = D ; CaloDw Temp
#                             X = E ; Fuel   Temp
#                             X = F ; Fuel Centerline (Inner Fuel Ring) Temp
#                             X = G ; Fuel Centerline (Outer Fuel Ring) Temp
#                             X = H ; Fuel Cladding Surface (Inner Fuel Ring) Temp
#                             X = I ; Fuel Cladding Surface (Outer Fuel Ring) Temp
#                             X = M ; Mass Flow
#
#      Note1 : 4 booleans are used : DON1_exec, DON2_exec, DON3_exec and CATH_exec
#              if the execution of one of the code goes wrong, the correspondig boolean equals False (it can not come back to True).
#              Then, the main ends and the error is notified in the Exec_report
#                   DON1_EXEC : SCWR64N1Flu
#                   DON2_EXEC : SCWR64N1Upda
#                   DON3_EXEC : SCWR64N1Relo
#                   CATH_EXEC : Cathena 
#
#      Note2 : errors is a boolean which is updated after each call to a PyProcs procedure. 
#              If an error happened in the proc, errors no longer equals to True
#              Then execution of the main stops after writing the Exec_report (to implement) 
#              
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# TO RESTART A CALCULATION FROM ITS STOPPING POINT 
# a) Clear the execution directory (remove what appears in but not in the "Global architecture of directories")
# b) Open the Store_DONJON and open the History.inp file
# c) Look in the "Step" repertory what is the last number written
# d) Use the number retrieved at c) to call Coupling_lvl2, the number is the new INPUT3
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Imports
import os         # Basic operations (management of files)
import shutil     # Sophisticated operations (management of files)
import time       # Time
import subprocess # Run CATHENA and DONJON 

from time import gmtime, strftime

# Import files managing functions 
PATH_PROC_PY = os.path.dirname(__file__)
PATH_EXEC    = PATH_PROC_PY[0:len(PATH_PROC_PY)-2]
PATH_PROC_DJ = PATH_EXEC+'DJ\\'
PATH_PROC_CA = PATH_EXEC+'CA\\'
os.chdir(PATH_PROC_PY+'\\')

import PyProcs_lvl1mTh as PyPro
from PyProcs_lvl1 import *

os.chdir(PATH_EXEC) 

## Main Coupling_lvl1
def Coupling_lvl2(PATH_EXEC,PATH_PROC_DJ,PATH_PROC_CA,INPUT1,INPUT2,INPUT3,INPUT4):
        
    # Inputs for SCWR64N1Flu
    Step      = INPUT1    
    CycleRef  = INPUT2
    TimeModel = INPUT3
    LoadModel = INPUT4
    
    # Outputs of SCWR64N1Flu.x2m+, initialization 
    Reload     = 0
    Out        = 0
    CycleIndex = 1
    
    # Errors and wentgood (complementary to errors for SCWR64N1Flu)
    errors     = False
    wentgood   = True 
    
    # Good execution booleans 
    ConvC     = False
    ConvD     = False
    
    # Output 
    RoadMap = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + ' \n \n'
    RoadMap = RoadMap + str(Step)+' Initialization done \n \n'
    
    CompCath  = 1
    CompCathS = 1
    
    START = time.time()

    Param_Dist     = zeros((10,1344,5))
    Param_Dist_new = zeros((10,1344,5))
    Param_DistCa   = zeros((10,336,5)) 
    MFlow_Dist     = ones((84,1))
    
    MFlow_Dist     = MFlow_Dist * 5.1   

    Param_DistA = ''
    Param_DistB = ''
    Param_DistC = ''
    Param_DistD = ''
    Param_DistE = ''
    Param_DistF = ''
    Param_DistG = ''
    Param_DistH = ''
    Param_DistI = ''
    Param_DistM = ''
    
    Param_AStore = 'CaloUp Dens distribution \n'
    Param_BStore = 'CaloUp Temp distribution \n'
    Param_CStore = 'CaloDw Dens distribution \n'
    Param_DStore = 'CaloDw Temp distribution \n'
    Param_EStore = 'Fuel   Temp distribution \n'
    Param_FStore = 'Fuel CITemp distribution \n'
    Param_GStore = 'Fuel COTemp distribution \n'
    Param_HStore = 'ISheathTemp distribution \n'
    Param_IStore = 'OSheathTemp distribution \n'
    Param_MStore = 'MassFlow    distribution \n'
    
    TimeCath = 1500.
    ConvArg  = []
    
    # # TO REMOVE 
    # TimeCath = 1.
    
    IncConvC = 0.3 
    IncConvD = 5.0 
    
    MaxCat = 0.
    MaxP   = 0.
    MaxTCu = 0.
    MaxTCd = 0.
    MaxTF  = 0.

    # While loop, tests Out condition, in normal execution, Out = 1 is triggered in history (SCWR64N1Flu.x2m+)
    # XXX
    while Out < 1 : 
        while ConvD == False :
            # - # - # - # - # - # - # - # - # DONJON1 # - # - # - # - # - # - # - # - #  
            
            # Import SCWR64N1Flu from Store  
            shutil.copyfile(PATH_PROC_DJ+'TEMPLATE_SCWR64N1Flu.x2m',PATH_EXEC+'SCWR64N1Flu.x2m')
            RoadMap = RoadMap + str(Step)+' SCWR64N1Flu.x2m was imported \n'
            
            # Prepare SCWR64N1Flu file
            #vvv
            (errors,wentgood) = writeN1Flu('SCWR64N1Flu.x2m',PATH_EXEC,Step,CycleRef,TimeModel,LoadModel)
            
            if wentgood == False or errors == True :
                RoadMap = RoadMap + str(Step)+' ERROR IN writeN1Flu \n'
                RoadMap = RoadMap + str(Step)+' wentgood = '+str(wentgood)+'\n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()
                
            else :
                RoadMap = RoadMap + str(Step)+' SCWR64N1Flu.x2m was properly prepared \n'
                
            
            #-------> Execution of SCWR64N1Flu.x2m
            start = time.time()
            
            subprocess.run([PATH_EXEC+"rdonjon5.bat", PATH_EXEC+"SCWR64N1Flu", PATH_EXEC+"DJ"])
            RoadMap = RoadMap + str(Step)+' SCWR64N1Flu.x2m execution \n'
        
            #xxxxx> Observer
            while os.path.isfile(PATH_EXEC+'SCWR64N1Flu.result') == False :
                time.sleep(1)
            
            end = time.time()    
            time.sleep(5)
            
            RoadMap = RoadMap + str(Step)+' SCWR64N1Flu.x2m end of execution \n'
            RoadMap = RoadMap +'!>> ' + str(end-start)[0:8]+' seconds spent in SCWR64N1Flu execution \n \n'  
                
            # Out of execution, retrieve power map                
            if os.path.isfile(PATH_EXEC+'FMAP.out') == True :
                
            # Read FuelMap file 
            #vvv  
                (Param_Dist_new,errors) = readN1Fmap('FMAP.out',PATH_EXEC,'HISTORY.out',PATH_EXEC) 
            
                if errors == True :
                    RoadMap = RoadMap + str(Step)+' readN1Fmap exec, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                    
                RoadMap = RoadMap + str(Step)+' new FMAP found and power retrieved \n'
                
            else :
                RoadMap = RoadMap + str(Step)+' new FMAP not found, error triggered \n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()
                                    
            # Remove SCWR64N1Flu.x2m+ and SCWR64N1Flu.x2m from execution dir
            os.remove(PATH_EXEC+'SCWR64N1Flu.result')
            os.remove(PATH_EXEC+'SCWR64N1Flu.x2m')
            RoadMap = RoadMap + str(Step)+' SCWR64N1Flu.x2m(+) read and cleaned, Step ='+str(Step)+' \n'
            
            # - # - # - # - # - # - # - # - # CATHENA # - # - # - # - # - # - # - # - #        
                    
            # Treat Power_Dist to prepare CATH file
            # vvv
            (Pwr_Chn,Pwr_Coeff) = treatN1paramDC(Param_Dist_new) 
                        
            RoadMap = RoadMap + str(Step)+' Power_Dist treated \n'
            
            while ConvC == False : 
            
                # Import CATH from Store
                shutil.copyfile(PATH_PROC_CA+'TEMPLATE_CATH.INP',PATH_EXEC+'CATH.INP')
                RoadMap = RoadMap + str(Step)+' CATH.INP was imported \n'
                
                # Prepare CATH file 
                # vvv
                (errors) = writeN1CATH('CATH.INP',PATH_EXEC,Pwr_Chn,Pwr_Coeff,MFlow_Dist,TimeCath) 
                
                if errors == True :
                    RoadMap = RoadMap + str(Step)+' writeN1CATH exec, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                
                RoadMap = RoadMap + str(Step)+' CATH was properly prepared \n'
                
                #-------> Execution of CATH
                start = time.time() 
                subprocess.run([PATH_EXEC+"cat3_6_1_1-b01", PATH_EXEC+"CATH.INP"])  
                RoadMap = RoadMap + str(Step)+' CATH execution \n'
                
                #xxxxx> Observer
                while os.path.isfile(PATH_EXEC+'CATH.buf') == True :
                    time.sleep(1)
                
                end = time.time()
                time.sleep(5)
                
                RoadMap = RoadMap + str(Step)+' CATH end of execution \n'
                RoadMap = RoadMap +'!>> ' + str(end-start)[0:8]+' seconds spent in CATH execution \n \n' 
                
                # Out of execution, retrieve thermodynamic parameters map 
                if os.path.isfile(PATH_EXEC+'CATH.lis') == True : 
                
                    # Read CONV.RES
                    # vvv
                    (ConvC,MaxCat,MFlow_Dist,Param_DistM,errors) = checkN1convcath('CONV.RES','MFLOW.RES',PATH_EXEC,IncConvC)
                    
                    RoadMap = RoadMap + str(Step)+'  => Conv Cath Param = '+str(MaxCat)+' \n'
                    print(str(Step)+'  => Conv Cath Param = '+str(MaxCat))     
                     
                    if ConvC == True :
                        # Read CATH+ file
                        # vvv
                        (Param_DistCa,errors) = readN1CATH(PATH_EXEC,'CaloUp Dens',Param_DistCa)  
                        # vvv
                        (Param_DistCa,errors) = readN1CATH(PATH_EXEC,'CaloUp Temp',Param_DistCa)  
                        # vvv
                        (Param_DistCa,errors) = readN1CATH(PATH_EXEC,'CaloDw Dens',Param_DistCa)  
                        # vvv
                        (Param_DistCa,errors) = readN1CATH(PATH_EXEC,'CaloDw Temp',Param_DistCa)  
                        # vvv
                        (Param_DistCa,errors) = readN1CATH(PATH_EXEC,'Fuel Temp',Param_DistCa)  
                    
                        (Param_Dist_new,Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE,Param_DistF,Param_DistG,Param_DistH,Param_DistI)  = treatN1paramCD(Param_Dist_new,Param_DistCa) 
                        
                        if errors == True :
                            RoadMap = RoadMap + str(Step)+' readN1CATH exec, error triggered \n'
                            END = time.time()
                            RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                            with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                                File.write(RoadMap)
                            return()
                        
                        else : 
                            RoadMap = RoadMap + str(Step)+' CATH+  converged  \n'
                        
                    else :
                        TimeCath += 500. 
                        RoadMap = RoadMap + str(Step)+' CATH+ did not converged, TimeCath inc of +500 :'+str(TimeCath)+'  \n'
                        RoadMap = RoadMap + str(Step)+'  => Abs Mass Flow  Diff = '+str(MaxCat)+' \n'   
                                            
                    # Clean exec directory
                    os.remove(PATH_EXEC+'CATH.lis')
                    os.remove(PATH_EXEC+'CATH.INP')
                    os.remove(PATH_EXEC+'SCWR64.rst')
                    
                    
                    newname = 'CONV'+str(Step)+str(CompCathS)+str(CompCath)+'.RES'
                    
                    #shutil.copyfile(PATH_EXEC+'CONV.RES',PATH_EXEC+newname)
                    os.remove(PATH_EXEC+'CONV.RES')
                    os.remove(PATH_EXEC+'MFLOW.RES')
                    
                    CompCath += 1
                        
                    for zz in range(1,5):
                        
                        Fid1  = 'DENSFLC'+str(zz)+'.RES'                         
                        Fid2  = 'DENSFLW'+str(zz)+'.RES' 
                        Fid3  = 'TEMPFLC'+str(zz)+'.RES'                         
                        Fid4  = 'TEMPFLW'+str(zz)+'.RES'                        
                        Fid5  = 'TWALLI'+str(zz)+'.RES'                        
                        Fid6  = 'TWALLO'+str(zz)+'.RES'                       
                        Fid7  = 'TWALLCI'+str(zz)+'.RES'                        
                        Fid8  = 'TWALLCO'+str(zz)+'.RES'                      
                        Fid9  = 'TWALLSI'+str(zz)+'.RES'                        
                        Fid10 = 'TWALLSO'+str(zz)+'.RES' 
                            
                        os.remove(PATH_EXEC+Fid1)                        
                        os.remove(PATH_EXEC+Fid2)                        
                        os.remove(PATH_EXEC+Fid3)
                        os.remove(PATH_EXEC+Fid4)
                        os.remove(PATH_EXEC+Fid5)
                        os.remove(PATH_EXEC+Fid6)
                        os.remove(PATH_EXEC+Fid7)
                        os.remove(PATH_EXEC+Fid8)
                        os.remove(PATH_EXEC+Fid9)
                        os.remove(PATH_EXEC+Fid10)
    
                    RoadMap = RoadMap + str(Step)+' CATH(+) read and cleaned \n'
                        
                else :
                    RoadMap = RoadMap + str(Step)+' CATH+ not found , error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                        
                RoadMap = RoadMap + str(Step)+' Thermodynamic parameters treated \n'
        
            (ConvD,MaxP,MaxTCu,MaxTCd,MaxTF) = checkN1convdist(Param_Dist,Param_Dist_new,IncConvD)
            
            ConvArg.append(MaxP)
            print(ConvArg)
            
            # Help convergence
            if ConvD == False :
                if CompCathS > 1 :
                    if ConvArg[CompCathS-1] > ConvArg[CompCathS-2] :
                        (Param_Dist_new,Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE,Param_DistF,Param_DistG,Param_DistH,Param_DistI)  = helpconv(Param_Dist_new,Param_Dist)
            
            ConvC = False
            
            # CHEAT 
            CompCathS += 1
            
            # TO REMOVE
            if CycleIndex < 5 :
                if CompCathS == 8 :
                    ConvD = True
                    
            Param_Dist = Param_Dist_new
                
            RoadMap = RoadMap + str(Step)+'  => Abs Power  Diff = '+str(MaxP)+' \n'
            RoadMap = RoadMap + str(Step)+'  => Abs TempCu Diff = '+str(MaxTCu)+' \n'
            RoadMap = RoadMap + str(Step)+'  => Abs TempCd Diff = '+str(MaxTCd)+' \n'
            RoadMap = RoadMap + str(Step)+'  => Abs TempFu Diff = '+str(MaxTF)+' \n'
            
            print(str(Step)+'  => Abs Power  Diff = '+str(MaxP))            
            print(str(Step)+'  => Abs TempCu Diff = '+str(MaxTCu))            
            print(str(Step)+'  => Abs TempCd Diff = '+str(MaxTCd))            
            print(str(Step)+'  => Abs TempFu Diff = '+str(MaxTF))            
            print('---------------------------------------')       
                                    
            if ConvD == True :
                
                RoadMap = RoadMap + str(Step)+' distribution did converge, old FMAP need to be removed, new need to take place \n'
                
                # Remove obsolete fuelmap and history 
                if os.path.isfile(PATH_PROC_DJ+'FMAP.inp') == True : 
                    os.remove(PATH_PROC_DJ+'FMAP.inp')
                    RoadMap = RoadMap + str(Step)+' old FMAP removed \n'
                else :
                    RoadMap = RoadMap + str(Step)+' old FMAP not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                    
                if os.path.isfile(PATH_PROC_DJ+'HISTORY.inp') == True :
                    os.remove(PATH_PROC_DJ+'HISTORY.inp')
                    RoadMap = RoadMap + str(Step)+' old HISTORY removed \n'
                else :
                    RoadMap = RoadMap + str(Step)+' old HISTORY not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()  
                
                # Copy new fuelmap and history 
                if os.path.isfile(PATH_EXEC+'FMAP.out') == True : 
                    shutil.copyfile(PATH_EXEC+'FMAP.out',PATH_PROC_DJ+'FMAP.inp')
                    RoadMap = RoadMap + str(Step)+' new FMAP copied in store \n'
                else :
                    RoadMap = RoadMap + str(Step)+' new FMAP not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                    
                if os.path.isfile(PATH_EXEC+'HISTORY.out') == True :
                    shutil.copyfile(PATH_EXEC+'HISTORY.out',PATH_PROC_DJ+'HISTORY.inp')
                    RoadMap = RoadMap + str(Step)+' new HISTORY copied in store \n'
                else :
                    RoadMap = RoadMap + str(Step)+' new HISTORY not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()
                
                # Stockpile the solution in a lasting file
                (errors) = stockN1dist(PATH_EXEC,'CaloUp Dens',Step,LoadModel,Param_DistA)
                (errors) = stockN1dist(PATH_EXEC,'CaloUp Temp',Step,LoadModel,Param_DistB)
                (errors) = stockN1dist(PATH_EXEC,'CaloDw Dens',Step,LoadModel,Param_DistC)
                (errors) = stockN1dist(PATH_EXEC,'CaloDw Temp',Step,LoadModel,Param_DistD)
                (errors) = stockN1dist(PATH_EXEC,'Fuel   Temp',Step,LoadModel,Param_DistE)
                (errors) = stockN1dist(PATH_EXEC,'Fuel CITemp',Step,LoadModel,Param_DistF)
                (errors) = stockN1dist(PATH_EXEC,'Fuel COTemp',Step,LoadModel,Param_DistG)
                (errors) = stockN1dist(PATH_EXEC,'ISheathTemp',Step,LoadModel,Param_DistH)
                (errors) = stockN1dist(PATH_EXEC,'OSheathTemp',Step,LoadModel,Param_DistI)
                (errors) = stockN1dist(PATH_EXEC,'MassFlow   ',Step,LoadModel,Param_DistM)
                
                
                RoadMap = RoadMap + str(Step)+' solutions stockpiled \n'
                
            else : 
                RoadMap = RoadMap + str(Step)+' distribution did not converge, new FMAP need to me removed \n'
            
            # Remove new fuelmap and history from execution dir 
            os.remove(PATH_EXEC+'FMAP.out')
            RoadMap = RoadMap + str(Step)+' new FMAP deleted from execution dir \n'
                
            os.remove(PATH_EXEC+'HISTORY.out')
            RoadMap = RoadMap + str(Step)+' new HISTORY deleted from execution dir \n'

            # Read history file 
            #vvv 
            if Step != 1 :
                (Reload,CycleIndex,Step,Out,errors) = readN1Flu('HISTORY.inp',PATH_PROC_DJ)   
                
            else : 
                if ConvD == True :
                    Reload     = 0
                    CycleIndex = 1
                    Step       = 2
                    Out        = 0
                    
            Reload     = int(Reload)             
            CycleIndex = int(CycleIndex)             
            Step       = int(Step)
            Out        = int(Out)
            
            
            CompCath   = 1
            
            # - # - # - # - # - # - # - # - # DONJON3 # - # - # - # - # - # - # - # - #
            RoadMap = RoadMap + str(Step)+' Updating triggered \n'
            
            # Import SCWR64N1Upda from Store
            shutil.copyfile(PATH_PROC_DJ+'TEMPLATE_SCWR64N1Upda.x2m',PATH_EXEC+'SCWR64N1Upda.x2m')
            
            if   LoadModel == "3c":
                cleng = 22
            elif LoadModel == "4c":
                cleng = 18
    
            cstep = Step%cleng
    
            if cstep == 0 :
                cstep = cleng
            
            poss_acc = 'Dist_DCu_'+str(cstep)+'.inp'
            
            if os.path.isfile(PATH_EXEC+'DISTRIBUTION\\'+poss_acc) and ConvD == True :  
                
                # Retrieve the solution of a precedent cycle
                
                (Param_DistA,errors) = getN1dist(PATH_EXEC,'CaloUp Dens',Step,LoadModel)
                (Param_DistB,errors) = getN1dist(PATH_EXEC,'CaloUp Temp',Step,LoadModel)
                (Param_DistC,errors) = getN1dist(PATH_EXEC,'CaloDw Dens',Step,LoadModel)
                (Param_DistD,errors) = getN1dist(PATH_EXEC,'CaloDw Temp',Step,LoadModel)
                (Param_DistE,errors) = getN1dist(PATH_EXEC,'Fuel   Temp',Step,LoadModel)
                (MFlow_Dist,errors)  = getN1mflw(PATH_EXEC,Step,LoadModel)
                
                RoadMap = RoadMap + str(Step)+' 5 useful solutions retrieved to begin the new step \n'
            
            # vvv
            writeN1Upda('SCWR64N1Upda.x2m',PATH_EXEC,'CaloUp Dens',Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE)                
            # vvv
            writeN1Upda('SCWR64N1Upda.x2m',PATH_EXEC,'CaloUp Temp',Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE)                
            # vvv
            writeN1Upda('SCWR64N1Upda.x2m',PATH_EXEC,'CaloDw Dens',Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE)                
            # vvv
            writeN1Upda('SCWR64N1Upda.x2m',PATH_EXEC,'CaloDw Temp',Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE)                
            # vvv
            writeN1Upda('SCWR64N1Upda.x2m',PATH_EXEC,'Fuel Temp',Param_DistA,Param_DistB,Param_DistC,Param_DistD,Param_DistE)
            
            if errors == True :
                RoadMap = RoadMap + str(Step)+' writeN1Upda exec, error triggered \n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()
                
            RoadMap = RoadMap + str(Step)+' SCWR64N1Upda was properly prepared \n'
            
            #-------> Execution of SCWR64N1Upda.x2m
            start = time.time()            
            subprocess.run([PATH_EXEC+"rdonjon5.bat", PATH_EXEC+"SCWR64N1Upda", PATH_EXEC+"DJ"])
            RoadMap = RoadMap + str(Step)+' SCWR64N1Upda execution \n'
            
            #xxxxx> Observer 
            while os.path.isfile(PATH_EXEC+'SCWR64N1Upda.result') == False  :
                time.sleep(1)
                
            end = time.time()
            time.sleep(5)   
            
            RoadMap = RoadMap + str(Step)+' SCWR64N1Upda end of execution \n'
            RoadMap = RoadMap +'!>> ' + str(end-start)[0:8]+' seconds spent in SCWR64N1Upda execution \n \n' 
                            
            # Remove obsolete fuelmap, then clean 
            if os.path.isfile(PATH_EXEC+'FMAPUP.out') == True : 
                
                if os.path.isfile(PATH_PROC_DJ+'FMAP.inp') == True : 
                    os.remove(PATH_PROC_DJ+'FMAP.inp')
                    RoadMap = RoadMap + str(Step)+' old FMAP removed \n'
                else :
                    RoadMap = RoadMap + str(Step)+' old FMAP not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()

                # Copy new Fuelmap 
                shutil.copyfile(PATH_EXEC+'FMAPUP.out',PATH_PROC_DJ+'FMAP.inp')
                RoadMap = RoadMap + str(Step)+' new FMAP copied in store \n'
                
                # Remove new fuelmap from execution dir 
                os.remove(PATH_EXEC+'FMAPUP.out')
                os.remove(PATH_EXEC+'SCWR64N1Upda.result')
                os.remove(PATH_EXEC+'SCWR64N1Upda.x2m')
                
                
                RoadMap = RoadMap + str(Step)+' SCWR64N1Upda.x2m(+)(FMAPUPDA) cleaned \n'
                RoadMap = RoadMap + str(Step)  +' STEP '+str(Step) +' TO BEGIN \n'
                
            else :                
                RoadMap = RoadMap + str(Step)+' new FMAP (updating) not found, error triggered \n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()
                                                  
        # Write thermodynamics distributions in output file 
        Param_AStore = Param_AStore + '>>Step '+str(Step-1)+' \n'
        Param_AStore = Param_AStore + Param_DistA ;
        Param_BStore = Param_BStore + '>>Step '+str(Step-1)+' \n'
        Param_BStore = Param_BStore + Param_DistB ;
        Param_CStore = Param_CStore + '>>Step '+str(Step-1)+' \n'
        Param_CStore = Param_CStore + Param_DistC ;
        Param_DStore = Param_DStore + '>>Step '+str(Step-1)+' \n'
        Param_DStore = Param_DStore + Param_DistD ;
        Param_EStore = Param_EStore + '>>Step '+str(Step-1)+' \n'
        Param_EStore = Param_EStore + Param_DistE ;
        Param_FStore = Param_FStore + '>>Step '+str(Step-1)+' \n'
        Param_FStore = Param_FStore + Param_DistF ;
        Param_GStore = Param_GStore + '>>Step '+str(Step-1)+' \n'
        Param_GStore = Param_GStore + Param_DistG ;
        Param_HStore = Param_HStore + '>>Step '+str(Step-1)+' \n'
        Param_HStore = Param_HStore + Param_DistH ;
        Param_IStore = Param_IStore + '>>Step '+str(Step-1)+' \n'
        Param_IStore = Param_IStore + Param_DistI ;
        Param_MStore = Param_MStore + '>>Step '+str(Step-1)+' \n'
        Param_MStore = Param_MStore + Param_DistM ;          
           
        print('<.>!<.>!<.>!<.>!<.>!<.>')
        print(str(Step)+'  to begin '+strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
          
        
        # Reset what need to be reset
        Param_Dist = zeros((10,1344,5))
        ConvD  = False 
        ConvArg  = []
            
        CompCath   = 1
        CompCathS  = 1
        TimeCath   = 1500.
        
        # - # - # - # - # - # - # - # - # DONJON2 # - # - # - # - # - # - # - # - #
        
        # If Reloading only is triggered, Reload                         
        if Reload == 1 :

            RoadMap = RoadMap + str(Step)+' Reloading triggered \n'
            
            # Import SCWR64N1Relo from Store
            shutil.copyfile(PATH_PROC_DJ+'TEMPLATE_SCWR64N1Relo.x2m',PATH_EXEC+'SCWR64N1Relo.x2m')

            # vvv
            errors = writeN1Relo('SCWR64N1Relo.x2m',PATH_EXEC,Step,LoadModel)
            
            if errors == True :
                RoadMap = RoadMap + str(Step)+' writeN1Relo exec, error triggered \n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()
            
            RoadMap = RoadMap + str(Step)+' SCWR64N1Relo was properly prepared \n'
            
            #-------> Execution of SCWR64N1Relo.x2m
            start = time.time()
            subprocess.run([PATH_EXEC+"rdonjon5.bat", PATH_EXEC+"SCWR64N1Relo", PATH_EXEC+"DJ"])
            
            RoadMap = RoadMap + str(Step)+' SCWR64N1Relo execution \n'
            
            #xxxxx> Observer
            while os.path.isfile(PATH_EXEC+'SCWR64N1Relo.result') == False :
                time.sleep(1)
            
            end = time.time()
            time.sleep(5)   
            
            RoadMap = RoadMap + str(Step)+' SCWR64N1Relo end of execution \n'
            RoadMap = RoadMap +'!>> ' + str(end-start)[0:8]+' seconds spent in SCWR64N1Relo execution \n \n' 
            
            # Remove obsolete fuelmap, then clean 
            if os.path.isfile(PATH_EXEC+'FMAPRE.out') == True : 
                
                if os.path.isfile(PATH_PROC_DJ+'FMAP.inp') == True : 
                    os.remove(PATH_PROC_DJ+'FMAP.inp')
                    RoadMap = RoadMap + str(Step)+' old FMAP removed \n'
                else :
                    RoadMap = RoadMap + str(Step)+' old FMAP not found, error triggered \n'
                    END = time.time()
                    RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                        File.write(RoadMap)
                    return()

                # Copy new Fuelmap 
                shutil.copyfile(PATH_EXEC+'FMAPRE.out',PATH_PROC_DJ+'FMAP.inp')
                RoadMap = RoadMap + str(Step)+' new FMAP copied in store \n'
                
                # Remove new fuelmap from execution dir 
                os.remove(PATH_EXEC+'FMAPRE.out')
                os.remove(PATH_EXEC+'SCWR64N1Relo.result')
                os.remove(PATH_EXEC+'SCWR64N1Relo.x2m')
                
                
                RoadMap = RoadMap + str(Step)+' SCWR64N1Relo.x2m(+)(FMAPRELO) cleaned \n'
                RoadMap = RoadMap + str(Step)+' CYCLE '+str(CycleIndex) +' TO BEGIN \n'
                
            else :                
                RoadMap = RoadMap + str(Step)+' new FMAP (reloading) not found, error triggered \n'
                END = time.time()
                RoadMap = RoadMap +'\nTime spent during execution '+str(END-START)[0:8]+' seconds \n' 
                with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
                    File.write(RoadMap)
                return()

                            
    # Export Exec_report if everything went good  
                 
    RoadMap = RoadMap +'\nNormal end of execution \n' 
    END = time.time()
    RoadMap = RoadMap +'Time spent during execution '+str(END-START)[0:8]+' seconds \n' 
    RoadMap = RoadMap + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + ' \n'                              
    with open(PATH_EXEC+'Exec_report.txt', 'w') as File:
        File.write(RoadMap)
    
                                                      
    with open(PATH_EXEC+'CaloUpDens_report.txt', 'w') as File:
        File.write(Param_AStore)                              
    with open(PATH_EXEC+'CaloUpTemp_report.txt', 'w') as File:
        File.write(Param_BStore)                              
    with open(PATH_EXEC+'CaloDwDens_report.txt', 'w') as File:
        File.write(Param_CStore)                              
    with open(PATH_EXEC+'CaloDwTemp_report.txt', 'w') as File:
        File.write(Param_DStore)                              
    with open(PATH_EXEC+'FuelTemp_report.txt', 'w') as File:
        File.write(Param_EStore)                            
    with open(PATH_EXEC+'FuelCITemp_report.txt', 'w') as File:
        File.write(Param_FStore)                           
    with open(PATH_EXEC+'FuelCOTemp_report.txt', 'w') as File:
        File.write(Param_GStore)                            
    with open(PATH_EXEC+'SheathITemp_report.txt', 'w') as File:
        File.write(Param_HStore)                           
    with open(PATH_EXEC+'SheathOTemp_report.txt', 'w') as File:
        File.write(Param_IStore)                 
    with open(PATH_EXEC+'MassFlow_report.txt', 'w') as File:
        File.write(Param_MStore)                   
        
    return()

INPUT1       =  1
INPUT2       =  8
INPUT3       = "CANDU5"
INPUT4       = "4c"

Coupling_lvl2(PATH_EXEC,PATH_PROC_DJ,PATH_PROC_CA,INPUT1,INPUT2,INPUT3,INPUT4)
