# ASCIILibv4
# Print the data-structure architecture
# AUTHOR   :      R. CHAMBON
# date     :      nov 2009
# modified :      avr 2020 
#          :      U. LE TENNIER, to be used with python

import numpy as np
from numpy import *

def ASCIILibv4(ilvl,RecordPos,RecordNumb,RecordName):
        
        # Note : if a record with more than 9 levels happens (X levels for instance)
        #        need to have a X-uplet
        #        change all the code lines with have '#***' at the end
        #        create the code lines where '#****#' exists
        #
        #        Error usually is 'ValueError: could not convert string to float: '1,0' then' 
        
    nel = size(RecordPos)

    # Problem :
    #      This implementation creates a 9-uplet full of ones (RecordPos). If there is only one element at the last level, the 
    #      algorithm will not be able to detect if it is empty or not. The equivalent in matlab reshapes everytime needed the X-uplet. 
    #      Due to this implementation, python can only know that the last dimension is not empty when there is at least two elements in it.
    #
    #      Two ideas, at least, could solve this problem. The first is to totally rethink the algorithm. The second is to develop a test that is able to 
    #      check if the last level is empty or not.
    #
    #      The part emcompassed by #*!*# marks is here because we use this function on an object created with MSTR:. In this object, there is data 
    #      at levels (1,1), (2,1), (3,1) etc. Therefore, the real MaxLvl = 2 when our implementation would give MaxLvl = 1
    
    MaxLvl = len(shape(RecordPos))
    decr   = 0
    for j in range(MaxLvl):
        if size(RecordPos,j) == 1 :
            decr += 1 
            
    MaxLvl = MaxLvl - decr 
    
    #*!*#
    if MaxLvl == 1 :
        MaxLvl = 2 
    #*!*#
        
    CurRecInd             = np.ones((1,MaxLvl))
    CurRecInd[0,MaxLvl-1] = 0
    spacemax              = MaxLvl*3+2
    
    print('"RecordPos" index   |-> ASCII file')
    for i in range(0,nel):
        tmplvl = MaxLvl
        CurRecInd[0,MaxLvl-1] = CurRecInd[0,MaxLvl-1] + 1
        
        if CurRecInd[0,MaxLvl-1] > size(RecordPos,MaxLvl-1) :
            
            while CurRecInd[0,tmplvl-1] > size(RecordPos,tmplvl-1):
                CurRecInd[0,tmplvl-1] = 1
                tmplvl = tmplvl-1
                
                if tmplvl == -1:
                    
                    break
                    
                CurRecInd[0,tmplvl-1] = CurRecInd[0,tmplvl-1] + 1
            
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
        
        for k in range(MaxLvl):
            strpos = strpos + str(int(CurRecInd[0,k])) + ','
            comas += 1
            if comas == 1 :
                A = int(CurRecInd[0,k]) - 1
            elif comas == 2 :
                B = int(CurRecInd[0,k]) - 1
            elif comas == 3 :
                C = int(CurRecInd[0,k]) - 1
            elif comas == 4 :
                D = int(CurRecInd[0,k]) - 1
            elif comas == 5 :
                E = int(CurRecInd[0,k]) - 1
            elif comas == 6 :
                F = int(CurRecInd[0,k]) - 1
            elif comas == 7 :
                G = int(CurRecInd[0,k]) - 1
            elif comas == 8 :
                H = int(CurRecInd[0,k]) - 1
            #***#

        strpos = strpos + '0' 
        
        addcomas = 8 - comas                         #***
        strpos   = strpos + ',0' * addcomas  
                
        indrec = int(RecordNumb[A,B,C,D,E,F,G,H,I])  #***

        if indrec > 0:
            leng   = len(strpos)
            compl  = spacemax - leng 
            strpos = strpos + ' ' * compl
            
            spacelvl='|'
            
            for l in range(1,MaxLvl): 
                if CurRecInd[0,l] > 1 :
                    spacelvl = spacelvl + str(l+1)
                
            print(strpos+' '+spacelvl+'-> '+str(RecordName[indrec-1]))
            
        elif indrec == 0:
            bypass = CurRecInd[0,tmplvl-1] - size(RecordPos,tmplvl-1) + 1
            byplvl = 1
            
            if tmplvl+1 <= MaxLvl:
                for m in range(tmplvl,MaxLvl):
                    byplvl = byplvl * size(RecordPos,m);
                
            bypasstot = bypass * byplvl-1 
            i = i + bypasstot
            CurRecInd[0,tmplvl-1] = 1
            tmplvl = tmplvl-1
            
            if tmplvl == -1:
                break
               
            CurRecInd[0,tmplvl-1] = CurRecInd[0,tmplvl-1] + 1
            
            if CurRecInd[0,tmplvl-1] > size(RecordPos,tmplvl-1):
                while CurRecInd[0,tmplvl-1] > size(RecordPos,tmplvl-1):
                    CurRecInd[0,tmplvl-1] = 1
                    tmplvl = tmplvl - 1
                    
                    if tmplvl == 0:
                        break
                    
                    CurRecInd[0,tmplvl-1] = CurRecInd[0,tmplvl-1] + 1


            CurRecInd[0,MaxLvl-1] = 0

        if tmplvl == 0:
            break

    return()
