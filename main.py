import streamlit as st
from moduli import run_module_partition_ui
from crit_path import run_critical_path_ui
from project_planner_module import run_project_planner_ui
from task_ordering import run_task_ordering_ui
from modular_split_by_links import run_modular_split_ui
from FAQ import show_faq


st.set_page_config(page_title="Project Solver", layout="wide")
st.title("Инструмент для проектных расчётов")
show_faq()

task_option = st.selectbox(
    "Выберите тип задачи:",
    [
        "Анализ критического пути (CPM)",
        "Календарное планирование и график загрузки",
        "Упорядочение множества задач по уровням",
        "Разбиение множества задач по связям",
        "Разбиение на модули по критерию независимости информации"
    ]
)

if task_option == "Анализ критического пути (CPM)":
    run_critical_path_ui()

elif task_option == "Календарное планирование и график загрузки":
    run_project_planner_ui()

elif task_option == "Упорядочение множества задач по уровням":
    run_task_ordering_ui()

elif task_option == "Разбиение множества задач по связям":
    run_modular_split_ui()

elif task_option == "Разбиение на модули по критерию независимости информации":
    run_module_partition_ui()



