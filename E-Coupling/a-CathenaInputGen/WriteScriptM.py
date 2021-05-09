# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# CATHENA input creation
##
# @file WriteScriptM.py 
# 
# @author U. Le Tennier (March 2020), (rev. 02/2021 for CNL)
#
# @brief Contain the function CompleteWriting(n) that produces n-channels CANDU-SCWR CATHENA input for coupling.
#
# CompleteWriting(n) calls a total of 6 different functions to create a complete CANDU-SCWR input for CATHENA.
# Its output will be written in the CWRITING.INP file which is created in the directory where WriteScriptM.py is located. 
#
# Each function accounts for one or more definition groups. Functions writeBase(), writeInit() and writeTherMod()
# have special marks (respectively HERE00, HEREMFLi and HEREiIN/HEREiOUT) which are replaced by different values by Coupling_lvl2().
# HERE00 will be replaced by the simulation time, HEREMFLi by the initial mass flow of the channel i and HEREiIN/HEREiOUT
# by the power distribution of the INNER or OUTER rods of the channel i. 
#
# @remarks
# It is possible that os.path.dirname(__file__) does not work. A solution is to give the absolute path of the WriteScriptM.py
# file to PATH_WRITE variable. Besides, such path must be consistent with the computer used. For Windows, the \\ mark separates the different 
# levels. For a use with other OS, the mark must be changed
# 
# @remarks
# At the end of writeSystConst(), the valve component is declared. By default, the gain is of 1E-5 and the period is 30s.
# Some example of different setting are provided as comments. For more information on the valve component, please refer to
# IGE-379.pdf 
# 
# @remarks
# It is recommended to call CompleteWriting(84), for n different than 84, several
# adjustments either in the CATHENA input generating functions and in the coupling functions
# should be made to have a 336 channels core. 
#
# @remarks
# It is possible to remove the HERE marks by giving directly numerical values.
# HEREiIN/HEREiOUT in writeTherMod() must be replaced by several code lines. An example of those lines
# is part of the function but is a comments line. To use it, declare the lines that add the HERE mark as comments and uncomment the lines that declare 
# the power distribution. Even with this modification, the coupling function 
# will not crash but the coupling will not be a coupling anymore because the power will not go from DONJON to CATHENA. 
# 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Imports
import os         # Basic operations (management of files)
import shutil     # Sophisticated operations (management of files)




## Aggregates strings and write the file 'CWRITING.INP' in the dir where WriteScriptM.py is located \n \n
#   INPUTS \n
#   1) n  : int, number of channels to consider (only work with n = 84) \n
def CompleteWriting(n):

    # Absolute path where to write 'CWRITING.INP'
    PATH_WRITE = os.path.dirname(__file__)+'\\'
    #PATH_WRITE = os.path.dirname(__file__)+'/'
    os.chdir(PATH_WRITE)
    
    aggr = ''
    aggr += writeBase()
    aggr += writeCompo(n)
    aggr += writeConnec(n)
    aggr += writeSysCont(n)
    aggr += writeInit(n)
    aggr += writeTherMod(n)
        
       
    with open(PATH_WRITE+'CWRITING.INP', 'w') as File:
        File.write(aggr)
    return()

## Write control group \n
def writeBase():
    les  = ''
    les  = '\'PT-SCWR SINGLE CHANNEL MODEL\', \n'
    les += '\'U. LE TENNIER, AUGUST 2020 FROM D. HUMMEL, OCTOBER 2013\',/\n'
    les += '\'CONTROL GROUP\'/\n'
    les += '\'**------------------------------------------------------------------\'/\n'
    les += '\'* PROGRAM CONTROL \'/\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'SOLUTION CONTROL\'/\n'
    les += '0.00,HERE00, , 1.00E-06, 1.00E-06, 1.00E-01/\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'PRINT CONTROL\'/\n'
    les += '500.00, 500.00, 500.00, , , , .TRUE., /\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'RESTART CONTROL\'/\n'
    les += ', \'SCWR64.rst\', 500.00, , , , /\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'PROCESSING OPTION\'/\n'
    les += '\'RUN\'/\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'NUMERIC OPTIONS\'/ \n'
    les += '\'#-PRESS-HIGH(-3)\',\'#-HF-HIGH(-3)\',\'#-HG-HIGH(-3)\',\'#-VEL-HIGH(-3)\',\n'
    les += '\'#-PRESS-LOW(-3)\', \'#-HF-LOW(-3)\', \'#-HG-LOW(-3)\',\n'
    les += '\'HLWP-VERSION(1)\'/  enable supercritical properties\n'
    les += '\'*-------------------------------------------------------------------\'/\n'
    les += '\'END\'/ \n \n'
        
    return(les)
    
## Write components \n 
def writeCompo(n):
    neutrons  = ''
    neutrons += '\'COMPONENTS\'/ \n'
    neutrons += '\'**------------------------------------------------------------------\'/ \n'
    neutrons += '\'* HYDRAULIC COMPONENT DEFINITION \'/ \n'
    neutrons += '\'*-------------------------------------------------------------------\'/ \n'
    neutrons += '\'INBOUND\', , , , , , , , , \'H2O\' / \n'
    neutrons += '\'PUMPDIS\', 0.500, 0.000, 2.731E-01, 0.593, 4.500E-05, 0.000, \'CIRC\',  \n'
    neutrons += '  3, \'H2O\',1/ \n'
    neutrons += '\'INPLEN\', , , , , , , \'VOLMC\', , \'H2O\', , 68.7190, / \n \n'
    
    for i in range(1,n+1):
        neutrons += '\'* CHANNEL'+str(i)+'\' / \n'
        
        neutrons += '\'INNOZ'+str(i)+'\', 1.697, -1.697, 1.614E-02, 0.100, 4.500E-05, 1.200, \'CIRC\', \n'
        neutrons += '3, \'H2O\','+str(336//n)+', 9.20498, / \n'
        neutrons += '\'FLOWTB'+str(i)+'\', 5.000, -5.000, 6.648E-03, 0.092, 4.500E-05, 0.000, \'CIRC\', \n'
        neutrons += '20, \'H2O\','+str(336//n)+', 11.16798, / \n'
        neutrons += '\'RVVOL'+str(i)+'\', 0.250, 0.000, 1.629E-02, 0.144, 4.50E-05, 1.200, \'CIRC\',1, \n '
        neutrons += '\'H2O\','+str(336//n)+', 1.36803, / \n'
        neutrons += '\'FLCHAN'+str(i)+'\', 5.000, 5.000, 4.565E-03, 0.007, 4.50E-05, 20.000, \n'
        neutrons += '\'CANFLEX\', 20, \'H2O\','+str(336//n)+', 7.66875, / \n'
        neutrons += '\'OUTNOZ'+str(i)+'\', 1.697, 1.697, 3.136E-03, 0.063, 4.500E-05, 1.150, \'CIRC\', \n'
        neutrons += '3, \'H2O\','+str(336//n)+', 1.78825, / \n'
        neutrons += '\'RISER'+str(i)+'\', 0.927, 0.927, 2.992E-03, 0.062, 4.500E-05, 0.000, \'CIRC\', \n'
        neutrons += '3, \'H2O\','+str(336//n)+', 0.93192, / \n'
        
        neutrons += '\n'
        
    neutrons += '\'* ALL CHANNELS DEFINED\' / \n'     
    neutrons += '\'OUTPLEN\', , , , , , , \'VOLMC\', , \'H2O\', , 14.23217, / \n'
    neutrons += '\'TRBPIPE\', 0.990, 0.000, 1.257E-01, 0.400, 4.500E-05, 0.000, \'CIRC\', \n'
    neutrons += '3, \'H2O\', 1, 0.49760, / \n'
    neutrons += '\'OUTBOUND\', , , , , , , , , \'H2O\', , , / \n'
    neutrons += '\'*-------------------------------------------------------------------\'/ \n'
    neutrons += '\'END\'/ \n \n'
    
    return(neutrons)
        
## Write connections \n
def writeConnec(n):
    ne  = ''    
    ne += '\'CONNECTIONS\'/ \n'
    ne += '\'**------------------------------------------------------------------\'/ \n'
    ne += '\'* HYDRAULIC CONNECTIONS DEFINITION \'/ \n'
    ne += '\'*-------------------------------------------------------------------\'/ \n'
    ne += '\'INBOUND\', \'L-PUMPDIS\'/ \n'
    ne += '\'R-PUMPDIS\', \'INPLEN\'/ \n \n'
    
    for i in range(1,n+1):
    ## junctions of every pressure tube 
        
        ne += '\'* CHANNEL'+str(i)+'\' / \n'
        
        ne += '\'INPLEN\', \'L-INNOZ'+str(i)+'\'/ \n'
        ne += '\'R-INNOZ'+str(i)+'\',\'L-FLOWTB'+str(i)+'\'/ \n'
        ne += '\'R-FLOWTB'+str(i)+'\', \'L-RVVOL'+str(i)+'\'/ \n' 
        ne += '\'R-RVVOL'+str(i)+'\', \'L-FLCHAN'+str(i)+'\'/ \n'
        ne += '\'R-FLCHAN'+str(i)+'\', \'L-OUTNOZ'+str(i)+'\'/ \n'
        ne += '\'R-OUTNOZ'+str(i)+'\', \'L-RISER'+str(i)+'\'/ \n'
        ne += '\'R-RISER'+str(i)+'\', \'OUTPLEN\'/ \n'
        
        ne += '\n'
        
    ne += '\'* ALL CONNECTIONS DEFINED\' / \n'  

    ne += '\'OUTPLEN\',\'L-TRBPIPE\'/ \n'
    ne += '\'R-TRBPIPE\', \'OUTBOUND\'/ \n'    
    
    ne += '\'*-------------------------------------------------------------------\'/ \n'
    ne += '\'END\'/ \n \n'
    
    return(ne)
        
## Write initial conditions \n
def writeInit(n):
    sont  = ''
    sont += '\'INITIAL CONDITIONS\'/ \n'
    sont += '\'**------------------------------------------------------------------\'/\n'
    sont += '\'* HYDRAULIC INITIAL CONDITIONS \'/ \n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'PUMPDIS\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/ \n'
    sont += '2.580E+07, , 350.00, 0.00, 5.100/\n'
    sont += '2.580E+07, , 350.00, 0.00, 5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'INPLEN\', \'BY-NODE\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
    sont += '2.580E+07, , 350.00, 0.00, 5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    
    for i in range(1,n+1):   
    ## initial conditions of every pressure tube      
        sont += '\'* CHANNEL'+str(i)+'\' / \n'
        sont += '\'INNOZ'+str(i)+'\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n' 
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'FLOWTB'+str(i)+'\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'RVVOL'+str(i)+'\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.580E+07, , 350.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'FLCHAN'+str(i)+'\', \'BY-NODES\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
        sont += '2.580E+07, , 354.85, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.576E+07, , 357.99, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.572E+07, , 363.10, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.567E+07, , 368.77, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.563E+07, , 376.50, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.559E+07, , 381.20, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.555E+07, , 384.79, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.551E+07, , 386.15, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.546E+07, , 388.33, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.542E+07, , 392.32, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.538E+07, , 399.68, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.534E+07, , 412.76, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.529E+07, , 431.12, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.525E+07, , 454.56, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.521E+07, , 482.85, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.517E+07, , 511.85, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.513E+07, , 540.05, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.508E+07, , 570.05, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.504E+07, , 589.85, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.500E+07, , 609.10, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'OUTNOZ'+str(i)+'\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
        sont += '2.500E+07, , 625.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.500E+07, , 625.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'RISER'+str(i)+'\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
        sont += '2.500E+07, , 625.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '2.500E+07, , 625.00, 0.00, '+'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
      
        
    sont += '\'* ALL COMPONENTS INIT. DEFINED\' / \n '  
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'OUTPLEN\', \'BY-NODE\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
    sont += '2.500E+07, , 625.00, 0.00, 5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'TRBPIPE\', \'BY-ENDS\', \'HG-BY-SAT\', \'HF-BY-TEMP\'/\n'
    sont += '2.500E+07, , 625.00, 0.00, 5.100/\n'
    sont += '2.500E+07, , 625.00, 0.00, 5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'INBOUND\', \'L-PUMPDIS\'/\n'
    sont += '5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'R-PUMPDIS\', \'INPLEN\'/\n'
    sont += '5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
        
    for i in range(1,n+1):  
    ## Initial flow in each junction of each pressure tube.  
    #  The HEREMFLi marks will be replaced by the coupling algorithm with mass flows       
        sont += '\'* CHANNEL'+str(i)+'\' / \n'        
        sont += '\'INPLEN\', \'L-INNOZ'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-INNOZ'+str(i)+'\',\'L-FLOWTB'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-FLOWTB'+str(i)+'\', \'L-RVVOL'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-RVVOL'+str(i)+'\', \'L-FLCHAN'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-FLCHAN'+str(i)+'\', \'L-OUTNOZ'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-OUTNOZ'+str(i)+'\', \'L-RISER'+str(i)+'\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
        sont += '\'R-RISER'+str(i)+'\', \'OUTPLEN\'/\n'
        sont += 'HEREMFL'+str(i)+'/\n'
        sont += '\'*-------------------------------------------------------------------\'/\n'
      
        
    sont += '\'* ALL JUNCTIONS INIT. DEFINED\' / \n '  
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'OUTPLEN\',\'L-TRBPIPE\'/\n'
    sont += '5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'R-TRBPIPE\', \'OUTBOUND\'/\n'
    sont += '5.100/\n'
    sont += '\'*-------------------------------------------------------------------\'/\n'
    sont += '\'END\'/ \n \n'
    
    return(sont)
        
## Write thermal models \n
def writeTherMod(n):
    pas  = ''
    pas += '\'HEAT TRANSFER PACKAGE\'/ \n'
    pas += '\'**------------------------------------------------------------------\'/\n'
    pas += '\'* HEAT GENERATION AND TRANSFER DEFINITIONS \'/\n'
    pas += '\'*-------------------------------------------------------------------\'/\n'
    
    for i in range(1,n+1):    
    ## initial flow in each junction of each pressure tube 
    #  The HEREi marks will be replaced by the coupling algorithm with power distributions
        pas += '\'* CHANNEL'+str(i)+'\' / \n'
        pas += '\'MODEL:(TUBEWL'+str(i)+')\', \'RADIAL CONDUCTION\', , /\n'
        pas += '\'RADIAL:(1,0.046,3,0.047)\', \'AXIAL:(5.0,20)\', , \'CYLINDER:(1,'+str(336//n)+')\'/\n'
        pas += '\'BOUNDARY CONDITIONS:(1,1)\'/\n'
        pas += '\'INSIDE HYDRAULIC:(FLOWTB'+str(i)+')\', \'BRANCH NODE:(1,20)\',\n'
        pas += '\'MODEL NODE:(1,20)\', , , , /\n'
        pas += '\'TUBE-CIR\', , , , , , , , , , , , /\n'
        pas += '\'OUTSIDE HYDRAULIC:(FLCHAN'+str(i)+')\', \'BRANCH NODE:(20,1)\',\n'
        pas += '\'MODEL NODE:(1,20)\', , , , /\n'
        pas += '\'TUBE-CIR\', , , , , , , , , , , , /\n'
        pas += '\'STAINLESS STEEL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'TEMP-2D-RAD-AXI\'/\n'
        pas += '350.00, 479.55, 609.10/\n'
        pas += '350.00, 469.93, 589.85/\n'
        pas += '350.00, 460.43, 570.85/\n'
        pas += '350.00, 445.03, 540.05/\n' 
        pas += '350.00, 430.93, 511.85/\n'
        pas += '350.00, 416.43, 482.85/\n'
        pas += '350.00, 402.28, 454.56/\n'
        pas += '350.00, 390.56, 431.12/\n'
        pas += '350.00, 381.38, 412.76/\n'
        pas += '350.00, 374.84, 399.68/\n'
        pas += '350.00, 371.16, 392.32/\n'
        pas += '350.00, 369.16, 388.33/\n'
        pas += '350.00, 368.08, 386.15/\n'
        pas += '350.00, 367.39, 384.79/\n'
        pas += '350.00, 365.60, 381.20/\n'
        pas += '350.00, 363.25, 376.50/\n'
        pas += '350.00, 359.39, 368.77/\n'
        pas += '350.00, 356.55, 363.10/\n'
        pas += '350.00, 353.99, 357.99/\n'
        pas += '350.00, 352.43, 354.85/\n'
        pas += '\'NO-PRINT-OUT\'/\n'
        pas += '\'*-------------------------------------------------------------------\'/\n'
        pas += '\'MODEL:(INFL'+str(i)+')\', \'RADIAL CONDUCTION\', , /\n'
        pas += '\'RADIAL:(3)\',\'AXIAL:(5.0,20)\', , \'CYLINDER:(1,'+str(10752//n)+')\'/\n'
        pas += '0.0,4,0.004150,2,0.004232,2,0.004750/\n'
        pas += '\'BOUNDARY CONDITIONS:(0,1)\'/\n'
        pas += '\'OUTSIDE HYDRAULIC:(FLCHAN'+str(i)+')\', \'BRANCH NODE:(1,20)\',\n'
        pas += '\'MODEL NODE:(1,20)\', , , , /\n'
        pas += '\'ALPHA-DEFAULT\', \'HT-CRIT-(0,0,6,6,2,2)\',\n'
        pas += '\'HT-CORR-(71,71,43,43,2,2,75,75,2)\', , ,\n'
        pas += '\'WALL-INTERFACE-HEAT-TRANSFER(5,5,5,5,5,5,1)\', , , , , , , /\n'
        pas += '\'MPF-TEMP:(28)\'/\n'
        pas += '27.0, 3.80, 2.18E+06,\n'
        pas += '127.0, 3.42, 2.39E+06,\n'
        pas += '227.0, 3.11, 2.51E+06,\n'
        pas += '327.0, 2.86, 2.60E+06,\n'
        pas += '427.0, 2.64, 2.66E+06,\n'
        pas += '527.0, 2.45, 2.70E+06,\n'
        pas += '627.0, 2.29, 2.72E+06,\n'
        pas += '727.0, 2.15, 2.74E+06,\n'
        pas += '827.0, 2.02, 2.75E+06,\n'
        pas += '927.0, 1.91, 2.75E+06,\n'
        pas += '1027.0, 1.81, 2.75E+06,\n'
        pas += '1127.0, 1.72, 2.75E+06,\n'
        pas += '1227.0, 1.64, 2.75E+06,\n'
        pas += '1327.0, 1.57, 2.76E+06,\n'
        pas += '1427.0, 1.50, 2.76E+06,\n'
        pas += '1527.0, 1.44, 2.78E+06,\n'
        pas += '1627.0, 1.38, 2.79E+06,\n'
        pas += '1727.0, 1.33, 2.82E+06,\n'
        pas += '1827.0, 1.28, 2.86E+06,\n'
        pas += '1927.0, 1.23, 2.91E+06,\n'
        pas += '2027.0, 1.19, 2.98E+06,\n'
        pas += '2127.0, 1.15, 3.06E+06,\n'
        pas += '2227.0, 1.11, 3.15E+06,\n'
        pas += '2327.0, 1.08, 3.26E+06,\n'
        pas += '2427.0, 1.05, 3.40E+06,\n'
        pas += '2527.0, 1.01, 3.55E+06,\n'
        pas += '2627.0, 0.99, 3.73E+06,\n'
        pas += '2727.0, 0.96, 3.93E+06/\n'
        pas += '\'GAP:(50000.0,0.5,0.8)\'/\n'
        pas += '\'STAINLESS STEEL\'/\n'
        
        pas += 'HERE'+str(i)+'IN \n'
        
        # pas += '\'HQ-SPACE:(12.74838E06)\'/ \n'  #84 chn new
        # pas += '\'R-USER:(0.1111 0.3333 0.5556)\', , \'A-USER\', , / \n'
        # pas += '0.0414,0.0454,0.0480,0.0494,0.0504,0.0512,0.0518,0.0524,0.0528,0.0530, \n'
        # pas += '0.0532,0.0531,0.0529,0.0526,0.0521,0.0515,0.0506,0.0491,0.0464,0.0427/ \n'
        
        pas += '\'HQ-NIL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'TEMP-2D-RAD-AXI\'/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '\'NO-PRINT-OUT\'/\n'
        pas += '*-------------------------------------------------------------------\'/\n'
        pas += '\'MODEL:(OUTFL'+str(i)+')\', \'RADIAL CONDUCTION\', , /\n'
        pas += '\'RADIAL:(3)\', \'AXIAL:(5.0,20)\', , \'CYLINDER:(1,'+str(10752//n)+')\' /\n'
        pas += '0.0,4,0.004400,2,0.004482,2,0.005000/\n'
        pas += '\'BOUNDARY CONDITIONS:(0,1)\'/\n'
        pas += '\'OUTSIDE HYDRAULIC:(FLCHAN'+str(i)+')\', \'BRANCH NODE:(1,20)\',\n'
        pas += '\'MODEL NODE:(1,20)\', , , , /\n'
        pas += '\'ALPHA-DEFAULT\', \'HT-CRIT-(0,0,6,6,2,2)\',\n'
        pas += '\'HT-CORR-(71,71,43,43,2,2,75,75,2)\', , ,\n'
        pas += '\'WALL-INTERFACE-HEAT-TRANSFER(5,5,5,5,5,5,1)\', , , , , , , /\n'
        pas += '\'MPF-TEMP:(28)\'/\n'
        pas += '27.0, 4.77, 2.17E+06,\n'
        pas += '127.0, 4.20, 2.38E+06,\n'
        pas += '227.0, 3.75, 2.50E+06,\n'
        pas += '327.0, 3.39, 2.59E+06,\n'
        pas += '427.0, 3.10, 2.64E+06,\n'
        pas += '527.0, 2.85, 2.69E+06,\n'
        pas += '627.0, 2.63, 2.71E+06,\n'
        pas += '727.0, 2.45, 2.73E+06,\n'
        pas += '827.0, 2.29, 2.74E+06,\n'
        pas += '927.0, 2.15, 2.74E+06,\n'
        pas += '1027.0, 2.03, 2.74E+06,\n'
        pas += '1127.0, 1.92, 2.74E+06,\n'
        pas += '1227.0, 1.82, 2.74E+06,\n'
        pas += '1327.0, 1.73, 2.75E+06,\n'
        pas += '1427.0, 1.65, 2.75E+06,\n'
        pas += '1527.0, 1.58, 2.77E+06,\n'
        pas += '1627.0, 1.51, 2.79E+06,\n'
        pas += '1727.0, 1.45, 2.82E+06,\n'
        pas += '1827.0, 1.39, 2.86E+06,\n'
        pas += '1927.0, 1.34, 2.91E+06,\n'
        pas += '2027.0, 1.29, 2.98E+06,\n'
        pas += '2127.0, 1.24, 3.06E+06,\n'
        pas += '2227.0, 1.20, 3.16E+06,\n'
        pas += '2327.0, 1.16, 3.27E+06,\n'
        pas += '2427.0, 1.12, 3.41E+06,\n'
        pas += '2527.0, 1.09, 3.57E+06,\n'
        pas += '2627.0, 1.06, 3.75E+06,\n'
        pas += '2727.0, 1.03, 3.96E+06/\n'
        pas += '\'GAP:(50000.0,0.5,0.8)\'/\n'
        pas += '\'STAINLESS STEEL\'/\n'
        
        pas += 'HERE'+str(i)+'OUT \n'

        # pas += '\'HQ-SPACE:(11.4421E06)\'/ \n'  #84 chn new
        # pas += '\'R-USER:(0.1111 0.3333 0.5556)\', , \'A-USER\', , / \n'
        # pas += '0.0414,0.0454,0.0480,0.0494,0.0504,0.0512,0.0518,0.0524,0.0528,0.0530, \n'
        # pas += '0.0532,0.0531,0.0529,0.0526,0.0521,0.0515,0.0506,0.0491,0.0464,0.0427/ \n'
        
        pas += '\'HQ-NIL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'TEMP-2D-RAD-AXI\'/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '687.0, 687.0, 687.0, 687.0, 687.0, 687.0/\n'
        pas += '\'NO-PRINT-OUT\'/\n'
        pas += '\'*-------------------------------------------------------------------\'/\n'
        pas += '\'MODEL:(PRESTB'+str(i)+')\', \'RADIAL CONDUCTION\', , /\n'
        pas += '\'RADIAL:(4,0.0720,2,0.0725,4,0.0780,2,0.0785,2,0.0905)\',\n'
        pas += '\'AXIAL:(5.0,20)\', ,\'CYLINDER:(1,'+str(336//n)+')\'/\n'
        pas += '\'BOUNDARY CONDITIONS:(1,1)\'/\n'
        pas += '\'INSIDE HYDRAULIC:(FLCHAN'+str(i)+')\', \'BRANCH NODE:(1,20)\',\n'
        pas += '\'MODEL NODE:(1,20)\', , , , /\n'
        pas += '\'TUBE-CIR\', , , , , , , , , , , , /\n'
        pas += '\'OUTSIDE PRESCRIBED:(MODER)\', , , , , \'SURFACE OPTION:(1)\'/\n'        
        pas += '\'SURF-HC,TF-TIME:(4000.0, 80.0,2)\'/ \n'
        pas += '    0.0,      1.0,           1.0, \n'
        pas += '10000.0,      1.0,           1.0/ \n'
        pas += '\'STAINLESS STEEL\'/\n'
        pas += '\'MPF-TEMP:(20)\'/\n'
        pas += '50.0, 2.51, 2.7497E+06,\n'
        pas += '100.0, 2.52, 2.8991E+06,\n'
        pas += '150.0, 2.47, 3.0545E+06,\n'
        pas += '200.0, 2.39, 3.1783E+06,\n'
        pas += '250.0, 2.31, 3.2834E+06,\n'
        pas += '300.0, 2.22, 3.3458E+06,\n'
        pas += '350.0, 2.15, 3.4292E+06,\n'
        pas += '400.0, 2.09, 3.5075E+06,\n'
        pas += '450.0, 2.03, 3.5493E+06,\n'
        pas += '500.0, 1.99, 3.5649E+06,\n'
        pas += '550.0, 1.96, 3.5828E+06,\n'
        pas += '600.0, 1.93, 3.6379E+06,\n'
        pas += '650.0, 1.91, 3.6738E+06,\n'
        pas += '700.0, 1.90, 3.7045E+06,\n'
        pas += '750.0, 1.90, 3.7208E+06,\n'
        pas += '800.0, 1.92, 3.7659E+06,\n'
        pas += '850.0, 1.94, 3.7630E+06,\n'
        pas += '900.0, 1.97, 3.8086E+06,\n'
        pas += ' 950.0, 2.00, 3.8377E+06,\n'
        pas += '1000.0, 2.06, 3.8632E+06/\n'
        pas += '\'ZIRCALOY\'/\n'
        pas += '\'ZIRCALOY\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'HQ-NIL\'/\n'
        pas += '\'TEMP-2D-RAD-AXI\'/\n'
        pas += '354.85, 304.88, 254.90, 204.93, 154.95, 104.98, 55.00/\n'
        pas += '357.99, 307.49, 256.99, 206.49, 156.00, 105.50, 55.00/\n'
        pas += '363.10, 311.75, 260.40, 209.05, 157.70, 106.35, 55.00/\n'
        pas += '368.77, 316.48, 264.18, 211.89, 159.59, 107.30, 55.00/\n'
        pas += '376.50, 322.92, 269.33, 215.75, 162.17, 108.58, 55.00/\n'
        pas += '381.20, 326.83, 272.47, 218.10, 163.73, 109.37, 55.00/\n'
        pas += '384.79, 329.82, 274.86, 219.89, 164.93, 109.96, 55.00/\n'
        pas += '386.15, 330.96, 275.77, 220.58, 165.38, 110.19, 55.00/\n'
        pas += '388.33, 332.77, 277.22, 221.66, 166.11, 110.55, 55.00/\n'
        pas += '392.32, 336.10, 279.88, 223.66, 167.44, 111.22, 55.00/\n'
        pas += '399.68, 342.24, 284.79, 227.34, 169.89, 112.45, 55.00/\n'
        pas += '412.76, 353.13, 293.51, 233.88, 174.25, 114.63, 55.00/\n'
        pas += '431.12, 368.44, 305.75, 243.06, 180.37, 117.69, 55.00/\n'
        pas += '454.56, 387.97, 321.38, 254.78, 188.19, 121.59, 55.00/\n'
        pas += '482.85, 411.54, 340.23, 268.93, 197.62, 126.31, 55.00/\n'
        pas += '511.85, 435.71, 359.57, 283.43, 207.28, 131.14, 55.00/\n'
        pas += '540.05, 459.21, 378.37, 297.53, 216.68, 135.84, 55.00/\n'
        pas += '570.85, 484.88, 398.90, 312.93, 226.95, 140.98, 55.00/\n'
        pas += '589.85, 500.71, 411.57, 322.43, 233.28, 144.14, 55.00/\n'
        pas += '609.10, 516.75, 424.40, 332.05, 239.70, 147.35, 55.00/\n'
        pas += '\'NO-PRINT-OUT\'/\n'
        pas += '\'*-------------------------------------------------------------------\'/\n'
        
    pas += '\'* ALL THERMAL MODELS DEFINED\' / \n'  
    pas += '\'END\'/ '  
    
    return(pas)
        

## Write boundary conditions, system models (control devices) and outputs \n
def writeSysCont(n):

    vivants  = ''
    vivants += '\'BOUNDARY CONDITIONS\'/ \n'
    vivants += '\'**------------------------------------------------------------------\'/ \n'
    vivants += '\'* HYDRAULIC BOUNDARY CONDITIONS DEFINITION \'/ \n'
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
    vivants += '\'RESERVOIR B.C.\', \'INLETBC\'/ \n'
    vivants += '\'INBOUND\'/ \n'
    vivants += '2.58E+07, , 350.00, 0.0 \'HG-BY-SAT\', \'HF-BY-TEMP\'/ \n'
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
    vivants += '\'RESERVOIR B.C.\', \'OUTLETBC\'/ \n'
    vivants += '\'OUTBOUND\'/ \n'
    vivants += '2.50E+07, , 625.00, 0.0 \'HG-BY-SAT\', \'HF-BY-TEMP\'/ \n'
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
    vivants += '\'END\'/ \n \n'
 
    vivants += '\'SYSTEM MODELS\'/ \n'
    vivants += '\'**------------------------------------------------------------------\'/ \n'
    vivants += '\'* SYSTEM MODELS (VALVES) \'/ \n'
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
    
    for i in range(1,n+1):     
        vivants += '\'* CHANNEL'+str(i)+'\' / \n' 
        vivants += '\'VALVE\', \'INORIF'+str(i)+'\'/ \n'
        vivants += '\'R-INNOZ'+str(i)+'\',\'L-FLOWTB'+str(i)+'\'/ \n'
        vivants += '4.072E-03, 0.61, 1.0, , , , , , \'ASME\', \'CHISHOLM\'/ \n'
        vivants += '\'*-------------------------------------------------------------------\'/ \n'
        vivants += '/ \n'
        
    vivants += '\'* ALL VALVES DEFINED\' / \n'  
    vivants += '\'END\'/ \n \n'
    
    vivants += '\'SYSTEM CONTROL\'/ \n'
    vivants += '\'**------------------------------------------------------------------\'/ \n'
    vivants += '\'* SYSTEM CONTROLS (INCLUDING OUTPUTS) \'/ \n'
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
            

    # Mass flow rate CONV  
    vivants += '\'* OUTCONV'+str(i)+'\' / \n' 
    vivants += '\'OUTPUT\',\'CONV\'/ \n'
    vivants += '498,\'CONV.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
    
    for z in range(1,n):
        vivants += '\'MFLO:FLOWTB'+str(z)+'(0.0)\' / \n'
        vivants += '/ \n'
        vivants += '\'MFLO:FLOWTB'+str(z)+'(2.5)\' / \n'
        vivants += '/ \n'
        vivants += '\'MFLO:FLOWTB'+str(z)+'(5.0)\' / \n'
        vivants += '/ \n'
        vivants += '\'MFLO:FLCHAN'+str(z)+'(0.0)\' / \n'
        vivants += '/ \n'
        vivants += '\'MFLO:FLCHAN'+str(z)+'(2.5)\' / \n'
        vivants += '/ \n'
        vivants += '\'MFLO:FLCHAN'+str(z)+'(5.0)\' / \n'
        vivants += '/ \n'
            

    # Mass flow rate   
    vivants += '\'* OUTMFLW'+str(i)+'\' / \n' 
    vivants += '\'OUTPUT\',\'MFLOW\'/ \n'
    vivants += '84,\'MFLOW.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
    
    for z in range(1,n+1):
        vivants += '\'MFLO:FLCHAN'+str(z)+'(5.0)\' / \n'
        vivants += '/ \n'
    
    for i in range(1,5): 
        # Temperature FUELCHAN
        vivants += '\'* OUTTEMPFL'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TEMPFLC'+str(i)+'\'/ \n'
        vivants += '420,\'TEMPFLC'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TEMPF:FLCHAN'+str(z)+'('+str(21-(i-1)*5-j)+')\'/  \n'
                vivants += '/ \n'

        # Temperature FLOWTUBE 
        vivants += '\'* OUTTEMPFLW'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TEMPFLW'+str(i)+'\'/ \n'
        vivants += '420,\'TEMPFLW'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TEMPF:FLOWTB'+str(z)+'('+str((i-1)*5+j)+')\'/  \n'
                vivants += '/ \n'
        
        # Density FUELCHAN
        vivants += '\'* OUTDENSFL'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'DENSFLC'+str(i)+'\'/ \n'
        vivants += '420,\'DENSFLC'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'RHOF:FLCHAN'+str(z)+'('+str(21-(i-1)*5-j)+')\',1.0E-2/  \n'
                vivants += '/ \n'
                

        # Density FLOWTUBE 
        vivants += '\'* OUTDENSFLW'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'DENSFLW'+str(i)+'\'/ \n'
        vivants += '420,\'DENSFLW'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6):
            for z in range(1,n+1):
                vivants += '\'RHOF:FLOWTB'+str(z)+'('+str((i-1)*5+j)+')\',1.0E-2/  \n'
                vivants += '/ \n'

        # Temperature FUELIN  
        vivants += '\'* OUTTEMPI'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLI'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLI'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:INFL'+str(z)+'('+str(21-(i-1)*5-j)+',3,1,1)\' / \n'
                vivants += '/ \n'

        # Temperature FUELOUT  
        vivants += '\'* OUTTEMPO'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLO'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLO'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:OUTFL'+str(z)+'('+str(21-(i-1)*5-j)+',3,1,1)\' / \n'
                vivants += '/ \n'

        # Temperature center FUELIN  
        vivants += '\'* OUTEMPCI'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLCI'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLCI'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:INFL'+str(z)+'('+str(21-(i-1)*5-j)+',1,1,1)\' / \n'
                vivants += '/ \n'

        # Temperature center FUELOUT  
        vivants += '\'* OUTEMPCO'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLCO'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLCO'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:OUTFL'+str(z)+'('+str(21-(i-1)*5-j)+',1,1,1)\' / \n'
                vivants += '/ \n'

        # Temperature sheath FUELIN  
        vivants += '\'* OUTEMPSI'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLSI'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLSI'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:INFL'+str(z)+'('+str(21-(i-1)*5-j)+',8,1,1)\' / \n'
                vivants += '/ \n'

        # Temperature sheath FUELOUT  
        vivants += '\'* OUTEMPSO'+str(i)+'\' / \n' 
        vivants += '\'OUTPUT\',\'TWALLSO'+str(i)+'\'/ \n'
        vivants += '420,\'TWALLSO'+str(i)+'.RES\',\'(1X,F9.3,2(1X,F9.3))\',,500,.TRUE.,.TRUE.,\'GNUPLOT\',2048/ \n'
        
        for j in range(1,6): 
            for z in range(1,n+1):
                vivants += '\'TWALL:OUTFL'+str(z)+'('+str(21-(i-1)*5-j)+',8,1,1)\' / \n'
                vivants += '/ \n'
                
    for i in range(1,n+1):   
        vivants += '\'* CHANNEL'+str(i)+'\' / \n' 
        vivants += '\'CONTROL DEVICE\', \'ORICTL'+str(i)+'\', .TRUE./ \n'
        #vivants += '\'PI\', 5.643E-04, 3.00, , 0.0, , 0.00/ \n'
        #vivants += '\'PI\', 3.E-05, 30.00, , 0.0, , 0.00/ \n'
        vivants += '\'PI\', 1.E-05, 30.00, , 0.0, , 0.00/ \n'
        vivants += '0.01, 1.00/ \n'
        vivants += '\'TEMPF:OUTNOZ'+str(i)+'(1)\'/ \n'
        vivants += '\'CONSTANT(625.00)\',-1.0/ \n'
        vivants += '/ \n'
        vivants += '\'INORIF'+str(i)+'\', \'OPENFR\', .FALSE./ \n'
        vivants += '/ \n'
        vivants += '\'*-------------------------------------------------------------------\'/ \n'
        
    vivants += '\'* ALL SYSTEMS DEFINED\' / \n'  
    vivants += '\'*-------------------------------------------------------------------\'/ \n'
    vivants += '\'END\'/ \n \n'
    
    return(vivants)
