@echo off 
md temp
set entree=%1
set proc=%2
copy %entree%.x2m temp
if "%proc%"=="" GOTO pasdeprocs 
copy %proc%\*.c2m temp
copy %proc%\*.INP temp
:pasdeprocs
copy donjon.exe temp 
cd temp
donjon <%entree%.x2m > %entree%.result
if "%proc%"=="" GOTO cleanprocs 
del *.c2m *.INP
:cleanprocs
if EXIST %entree%.result MOVE %entree%.result ..
MOVE *.out ..
DEL /Q *.*
cd ..
rmdir -r temp
