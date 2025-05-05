@echo off
chcp 65001 > nul
cd /d %~dp0

echo [!] Проверка и создание виртуального окружения...
if not exist ".venv" (
    python -m venv .venv
)

echo [!] Активация виртуального окружения...
call .venv\Scripts\activate

echo [!] Установка зависимостей (это может занять пару минут)...
pip install -r requirements.txt

echo [!] Запуск Streamlit-приложения...
start "" http://localhost:8501
streamlit run main.py --server.headless true

echo [!] Работа завершена. Нажмите любую клавишу для выхода.
pause
