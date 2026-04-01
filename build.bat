@echo off
chcp 65001

:: Request administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ==========================================
echo  Transformer Fault Diagnosis System - Build Script
echo ==========================================
echo.

echo [1/6] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)
echo Python environment OK
echo.

echo [2/6] Checking Nuitka...
python -c "import nuitka" >nul 2>&1
if errorlevel 1 (
    echo Nuitka not found, installing...
    python -m pip install nuitka -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Nuitka installation failed
        pause
        exit /b 1
    )
) else (
    echo Nuitka installed
)
echo.

echo [3/6] Checking UPX...
set UPX_PATH=D:\Code\Python\upx-5.1.1-win64\upx.exe
if exist "%UPX_PATH%" (
    echo UPX found: %UPX_PATH%
    set USE_UPX=1
) else (
    echo Warning: UPX not found, compression will be skipped
    echo Please check path: %UPX_PATH%
    set USE_UPX=0
)
echo.

echo [4/6] Cleaning old files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist main.build rmdir /s /q main.build 2>nul
if exist main.dist rmdir /s /q main.dist 2>nul
if exist main.onefile-build rmdir /s /q main.onefile-build 2>nul
if exist "TransformerFaultDiagnosis.exe" del /f /q "TransformerFaultDiagnosis.exe" 2>nul
echo Cleaned
echo.

echo [5/6] Creating output directory...
if not exist "%~dp0dist" mkdir "%~dp0dist"
echo Directory created
echo.

echo [6/6] Starting build with Zig (low memory)...
echo This may take 30-60 minutes, please wait...
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico="%~dp0resources\icon.ico" ^
    --company-name="Southwest Jiaotong University" ^
    --product-name="Transformer Fault Diagnosis System" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    --file-description="Power Transformer Fault Intelligent Diagnosis System" ^
    --copyright="Copyright (C) 2026 Ouyang Leican" ^
    --zig ^
    --enable-plugin=pyside6 ^
    --include-package=sklearn ^
    --include-package=pandas ^
    --include-package=numpy ^
    --include-package=openpyxl ^
    --include-package=joblib ^
    --include-data-dir="%~dp0resources=resources" ^
    --output-dir="%~dp0dist" ^
    --output-filename=TransformerFaultDiagnosis ^
    --jobs=0 ^
    --low-memory ^
    --show-progress ^
    --remove-output ^
    "%~dp0main.py"

if errorlevel 1 (
    echo.
    echo ==========================================
    echo  Build failed! Please check error messages
    echo ==========================================
    pause
    exit /b 1
)

echo.
echo [Extra] UPX compression...
if "%USE_UPX%"=="1" (
    echo Compressing with UPX...
    "%UPX_PATH%" --lzma "%~dp0dist\TransformerFaultDiagnosis.exe"
    if errorlevel 1 (
        echo UPX compression failed, but program is still usable
    ) else (
        echo UPX compression completed
    )
) else (
    echo Skipping UPX compression
)

echo.
echo ==========================================
echo  Build successful!
echo ==========================================
echo.
echo Output file: %~dp0dist\TransformerFaultDiagnosis.exe

echo File size:
for %%I in ("%~dp0dist\TransformerFaultDiagnosis.exe") do (
    echo   %%~zI bytes
)
echo.
echo Software info:
echo   Company: Southwest Jiaotong University
echo   Product: Transformer Fault Diagnosis System
echo   Version: 1.0.0.0
echo   Copyright: Copyright (C) 2026 Ouyang Leican
echo.
pause
