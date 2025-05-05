import subprocess
import webbrowser
import time
import socket
import sys
import os

base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
main_script = os.path.join(base_path, "main.py")

log_path = os.path.join(base_path, "log.txt")  # файл, в который будет писаться лог

with open(log_path, "w", encoding="utf-8") as log_file:
    process = subprocess.Popen(
        f"streamlit run \"{main_script}\" --server.headless true --server.port 8501",
        shell=True,
        stdout=log_file,
        stderr=log_file
    )

time.sleep(3)
webbrowser.open("http://localhost:8501")
def find_free_port(start=8501, end=8600):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found")

process.wait()


def is_streamlit_running(port):
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False

def launch_app():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    main_script = os.path.join(base_path, "main.py")

    port = find_free_port()
    cmd = f'streamlit run "{main_script}" --server.headless true --server.port {port}'

    try:
        process = subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print("Ошибка запуска:", e)
        input("Нажмите любую клавишу...")
        return

    print("Запускаем сервер...")
    for _ in range(30):
        if is_streamlit_running(port):
            webbrowser.open(f"http://localhost:{port}")
            break
        time.sleep(1)
    else:
        print("Streamlit не запустился.")

    print("Сервер работает. Закройте браузер для выхода.")
    try:
        while is_streamlit_running(port):
            time.sleep(2)
    except KeyboardInterrupt:
        pass

    print("Останавливаем сервер...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except:
        process.kill()

if __name__ == "__main__":
    launch_app()
