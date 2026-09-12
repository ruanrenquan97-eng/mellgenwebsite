@echo off
chcp 65001 >nul
echo ================================================================
echo    美尔健生物科技 - 注册 Windows 每日 SEO 自动化计划任务
echo ================================================================
echo.
set TASK_NAME=MellgenDailySEO
set BAT_PATH=%~dp0run_daily_seo.bat

echo 计划任务名称: %TASK_NAME%
echo 执行脚本路径: %BAT_PATH%
echo 默认执行时间: 每天凌晨 03:00
echo.

schtasks /create /tn "%TASK_NAME%" /tr "\"%BAT_PATH%\"" /sc daily /st 03:00 /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [成功] Windows 计划任务 [%TASK_NAME%] 已成功注册！
    echo 每天凌晨 03:00 操作系统将自动唤醒并执行 SEO 全网推送与地图更新。
) else (
    echo.
    echo [提示] 注册需要管理员权限，如提示权限不足，请右键选择「以管理员身份运行」。
)
echo.
pause
