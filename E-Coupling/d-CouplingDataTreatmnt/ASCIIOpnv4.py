# ASCIIOpnv4
# Open file, read it, extract the structure of the records
# AUTHOR   :      R. CHAMBON
# date     :      nov 2009
# modified :      avr 2020 
#          :      U. LE TENNIER, to be used with python

import numpy as np
from numpy import *

def ASCIIOpnv4(FileName):
        
        # Note : if a record with more than 9 levels happens (X levels for instance)
        #        need to have a X-uplet
        #        change all the code lines with have '#***' at the end
        #        create the code lines where '#****#' exists
        #
        #        Error usually is 'ValueError: could not convert string to float: '1,0' then' 
        
    with open(FileName, 'rb') as File:

        
        indrec    = 1
        MaxLvl    = 1
        CurRecInd = np.zeros((1,99)) 
        CurRecInd[0,0] = 0
        
        ilvl      = 1
        
        RecordPos  = np.zeros((1,1,1,1,1,1,1,1,1)) #***
        RecordNumb = np.zeros((1,1,1,1,1,1,1,1,1)) #***
        RecordName = []

        Lines    = File.read().splitlines()
        File.seek(0,0)
        Line = File.readline()
        Line = Line[0:len(Line)-1] 
        LastLine = Lines[-1].decode("utf-8")
        Last = True
        
        while Last : 
        
        # while Line != LastLine : 
            
            # Retrieve vectorial informations 
            lnotbypass = 1 
            curlvl        = int(Line[4:11])
            currecnamelen = int(Line[12:19])
            curtype       = int(Line[20:27])
            curnum        = int(Line[28:35])
            
            pos = File.tell()-73
            
            
            if (currecnamelen != 0):
                
                Line = File.readline()
                Line = Line[0:len(Line)-1]
                currecname =  Line[0:12]
                
            elif curlvl > 0 and curtype != 99 :
                
                currecname = 'elt#'+str(Line[72:80])
                pos        =  pos - 8
                # -8 for list element records are longer:
                # number of elt added at the end of line (12345678)
            
            if (curlvl == ilvl):
                CurRecInd[0,ilvl-1] = int(CurRecInd[0,ilvl-1]+1)
                
            elif (curlvl == ilvl+1):
                MaxLvl = max(curlvl,MaxLvl)
                ilvl   = curlvl
                CurRecInd[0,ilvl-1] = 1
                
            elif curlvl > 0 and curtype != 99 :
                for i in range (curlvl,ilvl):
                    CurRecInd[0,i] = 1
                
                CurRecInd[0,curlvl-1] = int(CurRecInd[0,curlvl-1]+1);
                ilvl = curlvl
                
            else :
                lnotbypass=0
            
        # Records 
            # Find the position, by default a 7-uplet
            if (lnotbypass == 1) :
                strpos='';
                for i in range (0,ilvl) :
                    inc = double(str(CurRecInd[0,i]))
                    inc = int(inc)
                    strpos = strpos+str(inc) + ',' 
                
                for i in range (ilvl,MaxLvl-1):
                    inc = double(str(CurRecInd[0,i]-1))
                    inc = int(inc)
                    strpos = strpos+str(inc) + ',' 
                
                strpos += '0'
                
                # Complete the position string to have a 7-uplet
                comas = 0
                
                for m in range(len(strpos)) :
                    if strpos[m] == ',':
                        comas += 1
                
                if comas == 0 :                      #***
                    strpos += ',0,0,0,0,0,0,0,0'     #***
                elif comas == 1  :                   #***
                    strpos += ',0,0,0,0,0,0,0'       #***
                elif comas == 2  :                   #***
                    strpos += ',0,0,0,0,0,0'         #***
                elif comas == 3  :                   #***
                    strpos += ',0,0,0,0,0'           #***
                elif comas == 4  :                   #***
                    strpos += ',0,0,0,0'             #***
                elif comas == 5  :                   #***
                    strpos += ',0,0,0'               #***
                elif comas == 6  :                   #***
                    strpos += ',0,0'                 #***
                elif comas == 7  :                   #***
                    strpos += ',0'                   #***
                
                k = 1
                a  = size(RecordPos,0)
                b  = size(RecordPos,1)
                c  = size(RecordPos,2)
                d  = size(RecordPos,3)
                e  = size(RecordPos,4)
                f  = size(RecordPos,5)
                g  = size(RecordPos,6)
                h  = size(RecordPos,7)
                ii = size(RecordPos,8)
                #****#
                
                coma    = 0 
                lastind = 0 
                change  = 0
                
                # Find if RecordPos needs a reshape (change != 0)
                # + retrieve each of the F coordinates (A,B,C,D,E,F,G,H,I)
                
                while coma < 8 :                          #***  
                    if strpos[k] == ',' :
                        val = double(strpos[lastind:k])
                        val = int(val)
                        if coma == 0 :
                            A = val
                            if val + 1 > a :
                                a = val + 1
                                change += 1
                            coma += 1
                            lastind = k+1
                            
                        elif coma == 1 :
                            B = val
                            if val + 1 > b :
                                b = val + 1 
                                change += 1
                            coma += 1
                            lastind = k+1
                            
                        elif coma == 2 :
                            C = val
                            if val + 1 > c :
                                c = val + 1 
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                        elif coma == 3 :
                            D = val
                            if val + 1 > d :
                                d = val + 1
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                        elif coma == 4 :
                            E = val
                            if val + 1 > e :
                                e = val + 1 
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                        elif coma == 5 :
                            F = val
                            if val + 1 > f :
                                f = val + 1 
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                        elif coma == 6 :
                            G = val
                            if val + 1 > g :
                                g = val + 1 
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                        elif coma == 7 :
                            H = val
                            if val + 1 > h :
                                h = val + 1 
                                change += 1
                            coma  += 1
                            lastind = k+1
                            
                            val = double(strpos[lastind:len(strpos)])    #***
                            val = int(val)                               #***
                            I = val                                      #***
                            if val + 1 > ii :                            #***
                                ii = val + 1                             #***
                                change += 1                              #***
                            coma  += 1                                   #***
                            #****#
                            
                    k += 1 
                       
                if change !=  0 :
                    newrecord = np.zeros((a,b,c,d,e,f,g,h,ii))               #***
                    newnumb   = np.zeros((a,b,c,d,e,f,g,h,ii))               #***
                    for r in range(size(RecordPos,0)):
                        for s in range(size(RecordPos,1)):
                            for t in range(size(RecordPos,2)):
                                for u in range(size(RecordPos,3)):
                                    for v in range(size(RecordPos,4)):
                                        for w in range(size(RecordPos,5)):
                                            for x in range(size(RecordPos,6)):
                                                for y in range(size(RecordPos,7)):
                                                    for z in range(size(RecordPos,8)):
                                                        #***#
                                                        newrecord[r,s,t,u,v,w,x,y,z] = RecordPos[r,s,t,u,v,w,x,y,z]       #***
                                                        newnumb[r,s,t,u,v,w,x,y,z]   = RecordNumb[r,s,t,u,v,w,x,y,z]      #***
                             
                    RecordPos  = newrecord
                    RecordNumb = newnumb
                if A == -1 :
                    A = 0 
                if B == -1 :
                    B = 0 
                if C == -1 :
                    C = 0 
                if D == -1 :
                    D = 0 
                if E == -1 :
                    E = 0 
                if F == -1 :
                    F = 0 
                if G == -1 :
                    G = 0 
                if H == -1 :
                    H = 0 
                if I == -1 :
                    I = 0 
                #***#
                     
                RecordPos[A,B,C,D,E,F,G,H,I]  = pos         #***
                RecordNumb[A,B,C,D,E,F,G,H,I] = indrec      #***
                
                RecordName.append(currecname)
                indrec=indrec+1
              
            # change position of cursor to next record line
            if (curtype == 0) or (curtype == 10):
                nskip = 0
                
            elif (curtype == 1):
                nl    = 2*ceil((curnum)/8) #8 int / line
                nskip = nl + curnum*10 # 10 bytes / int + 1 byte / line
                
            elif (curtype == 2):
                nl    = 2*ceil((curnum)/5) #8 real / line
                nskip = nl + curnum*16 # 16 bytes / real + 1 byte / line
                
            elif (curtype==3):
                nl    = 2  * ceil((curnum)/8)  #10 char / '         4'
                nl    = nl + 2*ceil((curnum)/20) #20 char / line
                nskip = nl + curnum*14 # 10+4 bytes / char + 1 byte / line
            
            nskip = int(nskip)
            File.seek(nskip,1)
            
            Line = File.readline()
            Line = Line[0:len(Line)-2].decode("utf-8")
            
            if Line == LastLine : 
                Last = False 
        
        CurRecInd = np.zeros((1,MaxLvl))
        ilvl=1
        
    return(ilvl,RecordPos,RecordNumb,RecordName,CurRecInd)
#ASCIILibv4(pfin,ilvl,RecordPos,RecordNumb,RecordName)
