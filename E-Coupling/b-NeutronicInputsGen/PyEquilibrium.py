# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#DONJON PyEquilibrium
##
# @file PyEquilibrium.py 
# 
# @author U. Le Tennier (March 2021)
# 
# @brief Contain ReachEqui(), the function that executes DONJON to reach neutronic equilibrium. 
#
# ReachEqui() is a trivial function that executes DONJON. The calculation options must be directly written 
# in the DONJON input file At the end of execution, the user is able to retrieve the DONJON output required 
# to start coupling calculation. The equilibrium calculation cannot be restarted from where it stopped. 
# If the process is interrupted, it has to be restarted from the beginning. The DONJON files 
# retrieved are .OUT files. To start coupling, the extension of those files must be changed to .INP.
#
# @section Environment Setup the environment
#
# Before executing ReachEqui(), the user must create a proc directory. In this proc must be placed 
# the multicompos and several DONJON procedures (.c2m). If the user wants to take into account 
# the impact of reloading on Pa233 inventories or the impact of corner/side assemblies, different
# .c2m and multicompos must be placed in proc directory. Depending on the loading plan and whether 
# the impact of reloading on fissile inventories is taken into account, the user must provide 
# the good set of multicompos and DONJON procedures.
#
# A total of 9 multicompos must be provided in the \textit{proc} directory. Finally, the DataTherm.INP 
# and both DBREFL1.INP DBREFL2.INP files are required to give a first distribution to thermodynamical 
# parameters and to generate the reflector macrolib.
# 
# The required directories architecture follows :
#
# A) EXEC_DIRECTORY               
#      a) proc 
#             1) SCWR64Geo.c2m \n
#             2) SCWR64FlI.c2m \n
#             3) SCWR64FlC.c2m \n
#             4) SCWR64Cr.c2m  \n
#             5) SCWR64Mc2.c2m    \n
#             6) SCWR64Re.c2m     \n
#             7) SCWR64Mc1.c2m  * \n
#             8) DataTherm.INP    \n
#            9+) DBREXX.INP      \n
#           10+) DBREFLX.INP       \n
#
#      b) SCWR64N1Eq.x2m \n
#      c) donjon.exe \n  
#      d) rdonjon5.bat \n
#
# SCWR64Mc1.c2m is only required when reloading is taken into account. 
# Otherwise, it is not necessary to put this file in proc directory.
#  
# @remarks
# In the SCWR64N1Eq.x2m file, the user must define which options he wants to use. Option 1
# is about the refueling, whether a 3-batches or 4-batches cycle is chosen. The user must 
# then replace the "OPTION1" string in SCWR64N1Eq.x2m by either "3c" or "4c". The second option to 
# choose is the number of cycles to simulate to reach equilibrium. It is advised to replace "OPTION2"
# with 18 if "3c" is used or 29 if "4c" is used. The third option is the time model used. Are
# available "REP1b" "REP2" "CANDU5" "CANDU3" and "CANDU2", a description of each is given is 
# the time loop of each SCWR64N1Eq.x2m file. It is advised to use "CANDU5"
#
# @remarks
# It is possible that Python does not recognize the path automatically given with os.path.dirname(__file__) command. 
# In such case, user must provide manually the absolute paths required. In Windows environment, 
# the directories separator's character in paths is \, which is also a special command in python. 
# Therefore, the separator in python strings must be \\. The paths' strings must be written in the following format :
# C:\\Users\\Desktop\\ .
#

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# Imports
import os         # Basic operations (management of files)
import shutil     # Sophisticated operations (management of files)
import subprocess # Run CATHENA and DONJON 

# PATH_EXEC    = Windows path must be written with "\\" separation mark (ex. "C:\\Users")
PATH_EXEC    = os.path.dirname(__file__)
PATH_PROC    = PATH_EXEC+'proc\\'

os.chdir(PATH_EXEC) 

# Main PyEquilibrium
##
#   INPUTS \n
#   1) PATH_EXEC     ; str, absolute path where to execute DONJON        
#   2) PATH_PROC     ; str, absolute path where DONJON procedures and databases are stored
def ReachEqui(PATH_EXEC,PATH_PROC):
            
    subprocess.run([PATH_EXEC+"rdonjon5.bat", PATH_EXEC+"SCWR64N1Eq", PATH_PROC])
    
    return()