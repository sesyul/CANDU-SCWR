# ASCIISixv4
# Change the current index to the one of the specified record
#  used for ASCII file created by DRAGON read with ASCIIOpn.m
# AUTHOR   :      R. CHAMBON
# date     :      nov 2009
# modified :      avr 2020 
#          :      U. LE TENNIER, to be used with python
#
# note:
#   move=0 to reset File index
#   move=1 to reset File to the line corresponding to 'RecToMoveTo' at THIS
#           level. If the record does not exist nbdata = 0
#   move=2 to reset File to FIRST record with level= ilvl-1
#

import numpy as np
from numpy import *

def ASCIISixv4(FileName,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,RecToMoveTo,move):
        
        # Note : if a record with more than 9 levels happens (X levels for instance)
        #        need to have a X-uplet
        #        change all the code lines with have '#***' at the end
        #        create the code lines where '#****#' exists
        #
        #        Error usually is 'ValueError: could not convert string to float: '1,0' then' 
        
    with open(FileName, 'rb') as File: 
        nbdata = 0
        
        # Return to first line
        if move == 0 or (move == 2 and ilvl == 1) or (move == 2 and ilvl == 2):
            File.seek(0,0)
            ilvl = 1 
            CurRecInd = zeros((1,9))  #***
            
        # Return to FIRST record with level= ilvl-1
        #   for ilvl=1 or 2 it is the bof,
        #   for ilvl>2 the CurRecInd should not correspond to the bof
        elif move == 2:
            CurRecInd[0,ilvl-2] = 0
            ilvl = ilvl-1 
            
        elif move == 1:
            tmpRecInd = CurRecInd            
            MaxLvl = size(CurRecInd,1)

            for i in range(size(RecordPos,ilvl-1)-1): 
                CurRecInd[0,ilvl-1] = i
                strpos = ''
                
                comas  = 0 
                A = 0
                B = 0 
                C = 0 
                D = 0 
                E = 0
                F = 0
                G = 0 
                H = 0 
                I = 0
                #***#
                
                for j in range (0,ilvl):
                    strpos = strpos + str(int(CurRecInd[0,j])+1) + ',' 
                    comas += 1
                    if comas == 1 :
                        A = int(CurRecInd[0,j]+1) 
                    elif comas == 2 :
                        B = int(CurRecInd[0,j]+1) 
                    elif comas == 3 :
                        C = int(CurRecInd[0,j]+1) 
                    elif comas == 4 :
                        D = int(CurRecInd[0,j]+1) 
                    elif comas == 5 :
                        E = int(CurRecInd[0,j]+1) 
                    elif comas == 6 :
                        F = int(CurRecInd[0,j]+1) 
                    elif comas == 7 :
                        G = int(CurRecInd[0,j]+1) 
                    elif comas == 8 :
                        H = int(CurRecInd[0,j]+1) 
                    #***#
        
                for k in range(ilvl,MaxLvl): #= ilvl+1:MaxLvl
                
                    strpos = strpos + str(int(CurRecInd[0,k])) + ',' 
                    comas += 1
                    if comas == 1 :
                        A = int(CurRecInd[0,k])
                    elif comas == 2 :
                        B = int(CurRecInd[0,k]) 
                    elif comas == 3 :
                        C = int(CurRecInd[0,k]) 
                    elif comas == 4 :
                        D = int(CurRecInd[0,k]) 
                    elif comas == 5 :
                        E = int(CurRecInd[0,k]) 
                    elif comas == 6 :
                        F = int(CurRecInd[0,k]) 
                    elif comas == 7 :
                        G = int(CurRecInd[0,k]) 
                    elif comas == 8 :
                        H = int(CurRecInd[0,k]) 
                    #***#
        
                strpos = strpos + '0'
                
                addcomas = 8 - comas                  #***
                strpos   = strpos + ',0' * addcomas  
                
                lgn = int(RecordNumb[A,B,C,D,E,F,G,H,I])
                
                if lgn != 0:
                    
                    if (type(RecordName[lgn-1]) == str):
                        right = RecordName[lgn-1][6:14]
                        left = RecordName[lgn-1][:4]
                        tot = left+right
                        RecordName[lgn-1] = tot
                        
                        if RecordName[lgn-1] == RecToMoveTo :
                            CurRecInd = tmpRecInd
                            ilvl   = ilvl+1
                            nbdata = -1
                            break
                            
                    else :
                        if RecordName[lgn-1].decode("utf-8") == RecToMoveTo :
                            CurRecInd = tmpRecInd
                            ilvl   = ilvl+1
                            nbdata = -1
                            break
            
                else:
                    break
            
        
            if nbdata == 0:
                print('WARNING: record '+ RecToMoveTo +' not found')
                #     fseek(pfin,position,'bof');
        
        else:
            print('WRONG move number');

    return(ilvl,nbdata,CurRecInd)

