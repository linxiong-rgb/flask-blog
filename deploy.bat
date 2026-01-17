@echo off
REM Render 部署脚本 - Windows 版本

chcp 65001 >nul
echo ==========================================
echo linxiong's Blog - 快速部署脚本
echo ==========================================
echo.

REM 检查 git 是否已初始化
if not exist ".git" (
    echo 1. 初始化 Git 仓库...
    git init
    git branch -M main
    echo ✓ Git 仓库初始化完成
) else (
    echo ✓ Git 仓库已存在
)

echo.
echo 2. 生成部署配置...
python deploy.py

echo.
echo 3. 请输入你的 GitHub 仓库地址：
echo 格式: https://github.com/用户名/仓库名.git
set /p REPO_URL="仓库地址: "

if "%REPO_URL%"=="" (
    echo ✗ 未配置 remote，跳过推送步骤
    echo 请手动执行: git push -u origin main
    pause
    exit /b
)

REM 检查是否已配置 remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin %REPO_URL%
    echo ✓ Remote 添加成功
) else (
    git remote set-url origin %REPO_URL%
    echo ✓ Remote 更新成功
)

echo.
echo 4. 提交代码...
git add .
git commit -m "Deploy to Render" || echo ✓ 无新更改需要提交

echo.
echo 5. 推送代码到 GitHub...
git push -u origin main

echo.
echo ==========================================
echo ✓ 代码推送完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 访问 https://dashboard.render.com
echo 2. 创建新的 Web Service
echo 3. 连接此 GitHub 仓库
echo 4. 配置环境变量（见 deploy.py 输出）
echo.
pause
