@ECHO OFF
CLS
COLOR 1B

:Begin
:: Set script name based on current directory
FOR /F "Delims=" %%D IN ('ECHO %CD%') DO SET ScriptName=%%~nD

:: Set window title
TITLE %ScriptName% Build Script!

:MakeBuildFolder
:: Create Build folder
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating \BUILD\%ScriptName%\ folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
MD BUILD
MD "BUILD\%ScriptName%\"
ECHO.

:GetRevision
:: Extract Revision # and SET %Revision% variable
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Extracting revision number . . .
ECHO.
FOR /F "Tokens=2* Delims=]" %%R IN ('FIND /v /n "&_&_&_&" ".svn\entries" ^| FIND "[11]"') DO SET Revision=%%R

:MakeExcludeFile
:: Create exclude file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating exclude.txt file . . .
ECHO.
ECHO .svn>"BUILD\exclude.txt"
ECHO Thumbs.db>>"BUILD\exclude.txt"
ECHO Desktop.ini>>"BUILD\exclude.txt"

:MakeReleaseBuild
:: Create release build
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Copying required files to \Build\%ScriptName%\ folder . . .
COPY plugin.py "BUILD\%ScriptName%\"
COPY default.tbn "BUILD\%ScriptName%\"
XCOPY resources "BUILD\%ScriptName%\resources" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt

:: Create new default.py with __svn_revision__ embedded
ECHO # %ScriptName% script revision: %Revision% - built with build.bat version 1.0 #> "BUILD\%ScriptName%\default.py"
FOR /F "Tokens=1* Delims=]" %%L IN ('FIND /v /n "&_&_&_&" default.py') DO (
    IF /I "%%M"=="__svn_revision__ = 0" (
        ECHO __svn_revision__ = "%Revision%">> "BUILD\%ScriptName%\default.py"
    ) ELSE IF "%%M"=="" (
        ECHO.>> "BUILD\%ScriptName%\default.py"
    ) ELSE (
        ECHO %%M>> "BUILD\%ScriptName%\default.py"
        )
    )
)
ECHO.

:Cleanup
:: Delete exclude.txt file
::ECHO ----------------------------------------------------------------------
::ECHO.
::ECHO Cleaning up . . .
::DEL "BUILD\exclude.txt"
::ECHO.
::ECHO.

:Finish
:: Notify user of completion
ECHO ======================================================================
ECHO.
ECHO Build Complete - Scroll up to check for errors.
ECHO.
ECHO Final build is located in the \BUILD\ folder.
ECHO.
ECHO copy: \%ScriptName%\ folder from the \BUILD\ folder.
ECHO to: /XBMC/scripts/ folder.
ECHO.
ECHO ======================================================================
ECHO.
PAUSE
