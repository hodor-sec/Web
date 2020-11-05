@echo off

set PROGRAM=rev_shell.c
set BASENAME=%PROGRAM:~0,-2%

@echo on

for %%a in (x86 amd64) do (
    setlocal
    call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" %%a
    csc /target:module empty.cs
    cl /c %PROGRAM%
    link /DLL /LTCG /CLRIMAGETYPE:IJW /out:%BASENAME%_%%a.dll %BASENAME%.obj empty.netmodule
    del %BASENAME%.obj empty.netmodule
    endlocal
)

