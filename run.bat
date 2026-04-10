@echo off

REM 启动脚本 - 使用虚拟环境运行应用程序
echo 正在启动变压器故障诊断系统...
echo 使用虚拟环境: venv
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo 错误: 虚拟环境不存在!
    echo 请先创建虚拟环境:
    echo   python -m venv venv
    echo   venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 运行应用程序
venv\Scripts\python.exe main.py

REM 等待用户按任意键退出
pause