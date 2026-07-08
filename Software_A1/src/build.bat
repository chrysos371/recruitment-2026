@echo off
REM ============================================================
REM  Software_A1/A2 — VS 2022 MSVC 一键编译脚本
REM  河海大学智泽实验室 2026 招新考核
REM ============================================================

REM 设置 VS 2022 MSVC 环境 (D:\新建文件夹\)
set "MSVC_PATH=D:\新建文件夹\VC\Tools\MSVC\14.44.35207"
set "SDK_PATH=D:\Windows Kits\10"
set "SDK_VER=10.0.26100.0"

REM INCLUDE
set "INCLUDE=%MSVC_PATH%\include"
set "INCLUDE=%INCLUDE%;D:\新建文件夹\VC\Auxiliary\VS\include"
set "INCLUDE=%INCLUDE%;%SDK_PATH%\Include\%SDK_VER%\ucrt"
set "INCLUDE=%INCLUDE%;%SDK_PATH%\Include\%SDK_VER%\um"
set "INCLUDE=%INCLUDE%;%SDK_PATH%\Include\%SDK_VER%\shared"
set "INCLUDE=%INCLUDE%;%SDK_PATH%\Include\%SDK_VER%\winrt"

REM LIB
set "LIB=%MSVC_PATH%\lib\x64"
set "LIB=%LIB%;D:\新建文件夹\VC\Auxiliary\VS\lib\x64"
set "LIB=%LIB%;%SDK_PATH%\Lib\%SDK_VER%\ucrt\x64"
set "LIB=%LIB%;%SDK_PATH%\Lib\%SDK_VER%\um\x64"

REM PATH
set "PATH=%MSVC_PATH%\bin\Hostx64\x64;%PATH%"

echo ============================================================
echo   VS 2022 MSVC Environment Ready
echo ============================================================
echo.
echo Compiling Rational (A1)...
cl /EHsc /std:c++20 /utf-8 /nologo /Fe:rational_demo.exe rational.cpp main.cpp
if %ERRORLEVEL% NEQ 0 (
    echo A1 compilation FAILED!
) else (
    echo A1 compilation SUCCESS! Run: rational_demo.exe
)

echo.
echo Compiling Shape (A2)...
cd ..\..\Software_A2\src
cl /EHsc /std:c++20 /utf-8 /nologo /Fe:shape_demo.exe shape.cpp main.cpp
if %ERRORLEVEL% NEQ 0 (
    echo A2 compilation FAILED!
) else (
    echo A2 compilation SUCCESS! Run: shape_demo.exe
)

echo.
echo Done.
pause
