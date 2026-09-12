@echo off
chcp 65001 >nul
echo [Mellgen SEO] 正在启动每日 SEO 与 GEO 自动化任务流水线...
cd /d "%~dp0\.."
python scripts\daily_seo_cron.py
echo [Mellgen SEO] 执行完成。
