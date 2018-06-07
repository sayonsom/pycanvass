@ECHO OFF
REM Visualize all GLM Files in a given folder.
IF EXIST %1\nul GOTO DIRECTORYFOUND
PAUSE
:DIRECTORYFOUND
ECHO [i] Press any key to build visualization to multiple GridLAB-D files in a  
ECHO     Directory: %1
ECHO [i] Else, press Ctrl + C to terminate
FOR %%a in (%1\*.glm) DO python visualize.py %%a %%~na
ECHO [i] Finished.


