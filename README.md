The five repertories contain inputs which were developped in support of a nuclear engineering MscA
at Polytechnique Montréal. The thesis carries a coupled thermalhydraulic neutronic study of
the Canadian SCWR, a IVth generation reactor cooled with supercritical water. The design considered
uses all the features proposed before 2020. The codes used are DRAGON5/DONJON5 (neutronics) and 
CATHENA (thermalhydraulics). DRAGON5 and DONJON5 are developped in Polytechnique Montréal, more
information is available at https://www.polymtl.ca/merlin/. CATHENA is owned by Canadian Nuclear 
Laboratories (CNL), its use is restricted therefore the executable is not available here. 

As for the thesis, the repertories A- to D- contain inputs commented in french. However, to deal
with this inputs requires an advanced understanding of nuclear physics, deterministic codes theory 
and DONJON/DRAGON syntax (CLE-2000). A- repertory provides DRAGON and SERPENT input to study the 
Canadian SCWR bundle. SERPENT is a stochastic code developped by VTT Technical Research Centre of 
Finland Ltd, more information available at http://montecarlo.vtt.fi/. The SERPENT input can be used as 
a comparative simulation to assess the precision of DRAGON. B- repertory provides DRAGON inputs 
to make perturbative calculation in order to build a Canadian SCWR bundle database. This database 
serves the core calculation with DONJON. C- repertory provides the input to make neutronics core 
calculation with DONJON. D- repertory provides the input to make thermalhydraulic core calculation 
with CATHENA. 

Finaly, E- repertory contains all the inputs that serve the coupling process. It is referred as
CSCT-D5C3 (Canadian SCWR Coupling Toolset - DONJON5 CATHENA3) and uses Python3. Because CATHENA 
needs a Windows environment, DONJON5 and DRAGON5 executables were created. They are available 
in E- repertory along with the rdonjon.bat file that runs DONJON. From rdonjon.bat, it is easy 
to create a rdragon5.bat (donjon5.exe to be replaced with dragon.exe). To support the execution 
of DONJON, large files are needed (databases, fuelmap, etc.). They are not available here, to 
retrieve it, please contact me at letennier.u@gmail.com. Finally, CSCT-D5C3UsersManual and 
IGE-379 are provided. CSCT-D5C3UsersManual is a technical manual that describes all the python 
functions contained in E- repertory. IGE-379 is a non-technical manual that gives important
information about the way to use the coupling program, the way ot oprerates, about the geometry 
of the core... Before trying to run the main program, it is advised to read carefully IGE-379 
to understand the big picture. Finally, a short presentation (CSCT-D5C3_slides) is provided. 
It gives partial insights about the coupling program and the different manuals. 

For any additional information, feel free to contact the author at letennier.u@gmail.com. 

U. Le Tennier
May 2021
