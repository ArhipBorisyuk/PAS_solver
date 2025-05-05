@echo off
cd /d %~dp0
pyinstaller --onefile --noconsole ^
--add-data "main.py;." ^
--add-data "FAQ.txt;." ^
--add-data "crit_path.py;." ^
--add-data "FAQ.py;." ^
--add-data "gantt_module.py;." ^
--add-data "modular_split_by_links.py;." ^
--add-data "moduli.py;." ^
--add-data "project_planner_module.py;." ^
--add-data "resource_load_module.py;." ^
--add-data "task_ordering_module.py;." ^
--add-data "word_export.py;." ^
app_launcher.py
pause
