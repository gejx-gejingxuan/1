@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================================
echo   自动安装脚本
echo   Ollama + qwen3:1.5b + Python + Flask
echo ================================================
echo.

:: ============================================================
:: 1. 安装 Ollama
:: ============================================================
echo [1/4] 检查 Ollama 是否已安装...
where ollama >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Ollama 已安装，跳过。
) else (
    echo [INFO] 正在下载并安装 Ollama...
    curl -fsSL -o "%TEMP%\OllamaSetup.exe" "https://ollama.com/download/OllamaSetup.exe"
    if !errorlevel! neq 0 (
        echo [ERROR] Ollama 下载失败，请检查网络连接。
        pause
        exit /b 1
    )
    echo [INFO] 正在静默安装 Ollama...
    "%TEMP%\OllamaSetup.exe" /S
    if !errorlevel! neq 0 (
        echo [ERROR] Ollama 安装失败。
        pause
        exit /b 1
    )
    :: 刷新 PATH
    call refreshenv >nul 2>&1
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
    echo [OK] Ollama 安装完成。
)
echo.

:: ============================================================
:: 2. 拉取 qwen3:1.5b 模型
:: ============================================================
echo [2/4] 正在拉取 qwen3:1.5b 模型（首次拉取需要一些时间）...
ollama pull qwen3:1.5b
if %errorlevel% neq 0 (
    echo [WARN] 模型拉取失败，可能 Ollama 服务未启动，尝试启动后重拉...
    start /b ollama serve
    timeout /t 5 /nobreak >nul
    ollama pull qwen3:1.5b
    if !errorlevel! neq 0 (
        echo [ERROR] qwen3:1.5b 拉取失败，请稍后手动运行: ollama pull qwen3:1.5b
    ) else (
        echo [OK] qwen3:1.5b 拉取完成。
    )
) else (
    echo [OK] qwen3:1.5b 拉取完成。
)
echo.

:: ============================================================
:: 3. 检查 / 安装 Python
:: ============================================================
echo [3/4] 检查 Python 是否已安装...
python --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK] 已检测到 %%v，跳过安装。
) else (
    echo [INFO] Python 未找到，正在下载 Python 3.12 安装包...
    curl -fsSL -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
    if !errorlevel! neq 0 (
        echo [ERROR] Python 下载失败，请检查网络连接。
        pause
        exit /b 1
    )
    echo [INFO] 正在静默安装 Python（添加到 PATH）...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if !errorlevel! neq 0 (
        echo [ERROR] Python 安装失败。
        pause
        exit /b 1
    )
    :: 刷新 PATH
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
    echo [OK] Python 安装完成。
)
echo.

:: ============================================================
:: 4. 安装 Python 模块 flask 和 requests
:: ============================================================
echo [4/4] 正在安装 Python 模块: flask, requests...
python -m pip install --upgrade pip --quiet
python -m pip install flask requests
if %errorlevel% neq 0 (
    echo [ERROR] pip 安装模块失败，请检查 Python 环境。
    pause
    exit /b 1
)
echo [OK] flask 和 requests 安装完成。
echo.

:: ============================================================
:: 完成
:: ============================================================
echo ================================================
echo   全部安装完成！
echo   - Ollama:      ollama --version
echo   - 模型:        ollama list
echo   - Python:      python --version
echo   - Flask:       python -c "import flask; print(flask.__version__)"
echo   - Requests:    python -c "import requests; print(requests.__version__)"
echo ================================================
echo.
pause
