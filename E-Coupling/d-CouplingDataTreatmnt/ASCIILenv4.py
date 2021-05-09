# ASCSIILen
# Get the length of a record data in an ASCII file created by DRAGON
# AUTHOR   :      R. CHAMBON
# date     :      nov 2009
# modified :      avr 2020 
#          :      U. LE TENNIER, to be used with python

import numpy as np
from numpy import *

def ASCIILenv4(FileName,ilvl,RecordPos,RecordNumb,RecordName,CurRecInd,RecNameLen):
        
        # Note : if a record with more than 9 levels happens (X levels for instance)
        #        need to have a X-uplet
        #        change all the code lines with have '#***' at the end
        #        create the code lines where '#****#' exists
        #
        #        Error usually is 'ValueError: could not convert string to float: '1,0' then' 
        
    with open(FileName, 'rb') as File: 
        nbdata  = 0
        typdata = 0 
        MaxLvl = size(CurRecInd,1)
        
        if MaxLvl == 2 :
            if size(RecordPos,1) :
                MaxLvl = 1

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
                #****#
    
            for k in range(ilvl,MaxLvl): 
            
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
                #****# 
    
            strpos = strpos + '0'
            
            addcomas = 8 - comas                       #***
            strpos   = strpos + ',0' * addcomas  
            
            pos = int(RecordPos[A,B,C,D,E,F,G,H,I])    #***
            lgn = int(RecordNumb[A,B,C,D,E,F,G,H,I])   #***
            
            if lgn != 0:
                
                
                
                if type(RecordName[lgn-1]) == str :
                    
                    # if elt#b'00000***' is triggered
                    
                    if RecordName[lgn-1][0:4]+RecordName[lgn-1][6:14] == RecNameLen :
                        File.seek(pos,0)  
                        Line = File.readline()
                        Line = Line[0:len(Line)-1] 
                        typdata = int(Line[18:26])
                        nbdata = int(Line[26:34])
                        
                        if typdata == 3 :
                            nbdata = nbdata * 4
                        
                        break
                    
                
                else :
                    if RecordName[lgn-1].decode("utf-8") == RecNameLen :
                        File.seek(pos,0)  
                        Line = File.readline()
                        Line = Line[0:len(Line)-1] 
                        typdata = int(Line[18:26])
                        nbdata = int(Line[26:34])
                        
                        if typdata == 3 :
                            nbdata = nbdata * 4
                        
                        break
            else:
                break

        if nbdata == 0 :
            print('WARNING: record '+ RecNameLen +' not found')

    return(nbdata)