import streamlit as st
import pandas as pd
from resource_load_module import plot_resource_load
from gantt_module import plot_gantt_diagram
from word_export import save_report_to_word

def run_project_planner_ui():
    st.subheader("🛠️ Ввод данных задач")

    if "planner_ready" not in st.session_state:
        st.session_state["planner_ready"] = False
    if "planner_data" not in st.session_state:
        st.session_state["planner_data"] = {}

    default_df = pd.DataFrame({
        "Задача": [str(i) for i in range(1, 16)],
        "Предшественники": [
            "", "1", "2", "3", "4",
            "5", "6", "7", "8", "9",
            "8", "6", "11", "10,11,12,13", "14"
        ],
        "Дата начала": [pd.Timestamp.today().strftime("%d.%m.%y")] * 15,
        "Длительность": [
            "2", "1", "2", "3", "3", "2", "2", "2", "3", "2",
            "3", "2", "2", "2", "2"
        ],
        "Ресурсы": [
            "Инженер,Рабочий", "Инженер", "Рабочий,Техник", "Инженер,Рабочий",
            "Рабочий,Техник", "Инженер,Рабочий", "Инженер,Рабочий", "Рабочий,Техник",
            "Инженер,Рабочий", "Инженер,Рабочий", "Техник,Рабочий", "Рабочий,Администратор",
            "Рабочий,Инженер", "Администратор,Рабочий", "Администратор,Рабочий"
        ],
        "% Загруженности": ["50,50"] * 15
    })

    task_df = st.data_editor(
        default_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    start_date_input = st.date_input("Дата начала проекта", pd.Timestamp.today())
    workdays_per_week = st.selectbox("Количество рабочих дней в неделе", [5, 6], index=0)

    if st.button("📊 Построить диаграмму и графики"):
        try:
            df_for_gantt = task_df.copy()
            df_for_resource = task_df.copy()

            gantt_fig = plot_gantt_diagram(df_for_gantt, start_date_input, workdays_per_week)
            resource_figs = plot_resource_load(df_for_resource, workdays_per_week)

            # Сохраняем всё в сессию
            st.session_state["planner_ready"] = True
            st.session_state["planner_data"] = {
                "input_table": task_df,
                "gantt_fig": gantt_fig,
                "resource_figs": resource_figs
            }

        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.session_state["planner_ready"] = False

    if st.session_state.get("planner_ready", False):
        st.subheader("📅 Диаграмма Ганта")
        st.pyplot(st.session_state["planner_data"]["gantt_fig"], use_container_width=True)

        st.subheader("📉 Графики загрузки ресурсов")
        cols = st.columns(2)
        for i, fig in enumerate(st.session_state["planner_data"]["resource_figs"]):
            with cols[i % 2]:
                st.pyplot(fig, use_container_width=True)

        if st.button("📄 Сохранить отчет в Word"):
            buffer = save_report_to_word(
                title="Календарное планирование и загрузка ресурсов",
                input_tables={"Исходные данные": st.session_state["planner_data"]["input_table"]},
                output_tables={},
                texts=["Диаграмма Ганта и графики загрузки по ролям"],
                images=[st.session_state["planner_data"]["gantt_fig"]] + st.session_state["planner_data"]["resource_figs"]
            )
            st.download_button("⬇️ Скачать отчет", buffer, file_name="Календарное_планирование.docx")
