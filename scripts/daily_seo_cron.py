# -*- coding: utf-8 -*-
"""
Standalone execution entry point for Daily SEO Automation.
Can be invoked by Windows Task Scheduler (任务计划程序), Linux Crontab, or manual CLI.
Usage:
    python scripts/daily_seo_cron.py
"""

import os
import sys

# Ensure workspace and cms_system are on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
CMS_DIR = os.path.join(WORKSPACE_DIR, "cms_system")

if CMS_DIR not in sys.path:
    sys.path.insert(0, CMS_DIR)

try:
    import daily_scheduler
    result = daily_scheduler.execute_daily_seo_pipeline(trigger_source="os_scheduled_task")
    print("\n" + "="*60)
    print(f"Daily SEO Execution Complete: {result.get('status')}")
    print(f"Summary: {result.get('summary')}")
    print("="*60 + "\n")
    sys.exit(0)
except Exception as e:
    print(f"[-] Fatal error executing daily SEO pipeline: {e}")
    sys.exit(1)
