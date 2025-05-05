import streamlit as st
import pandas as pd
import networkx as nx
from word_export import save_report_to_word


def run_critical_path_ui():
    st.subheader("Анализ критического пути (CPM)")
    st.markdown("Таблица для ввода задач, длительности и связей")

    # Инициализация состояния
    if "cpm_ready" not in st.session_state:
        st.session_state["cpm_ready"] = False
    if "cpm_data" not in st.session_state:
        st.session_state["cpm_data"] = {}

    # Данные по умолчанию
    dependencies = {
        1: [], 2: [1], 3: [2], 4: [3], 5: [4], 6: [5], 7: [6], 8: [7], 9: [8],
        10: [9], 11: [8], 12: [6], 13: [11], 14: [10, 11, 12, 13], 15: [14]
    }
    durations = {
        1: 2, 2: 1, 3: 2, 4: 3, 5: 3, 6: 2, 7: 2, 8: 2, 9: 3, 10: 2,
        11: 3, 12: 2, 13: 2, 14: 2, 15: 2
    }

    # Составление таблицы по умолчанию
    table_data = []
    for task in sorted(durations.keys()):
        preds = dependencies.get(task, [])
        table_data.append({
            "Задача": task,
            "Длительность": durations[task],
            "Предшественники": " ".join(map(str, preds))
        })

    task_table = st.data_editor(
        pd.DataFrame(table_data),
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    if st.button("📈 Выполнить CPM-анализ"):
        try:
            G = nx.DiGraph()
            durations = {}
            predecessors = {}

            for _, row in task_table.dropna().iterrows():
                task = int(float(row["Задача"]))
                dur = int(float(row["Длительность"]))
                preds = str(row["Предшественники"]).replace(",", " ").split()
                preds = list(map(int, preds)) if preds else []

                durations[task] = dur
                predecessors[task] = preds

                for pred in preds:
                    G.add_edge(pred, task)

            # Ранние сроки
            early_start = {}
            for node in nx.topological_sort(G):
                preds = predecessors.get(node, [])
                early_start[node] = max([early_start[p] + durations[p] for p in preds], default=0)

            project_duration = max(early_start[t] + durations[t] for t in G.nodes)

            # Поздние сроки
            latest_start = {}
            for node in reversed(list(nx.topological_sort(G))):
                succs = list(G.successors(node))
                if not succs:
                    latest_start[node] = project_duration - durations[node]
                else:
                    latest_start[node] = min([latest_start[s] - durations[node] for s in succs])

            # Резервы
            reserves = {n: latest_start[n] - early_start[n] for n in G.nodes}
            critical_path = [n for n in G.nodes if reserves[n] == 0]

            # Таблица 1 – Раннее время
            df_early = []
            for task in G.nodes:
                preds = predecessors.get(task, [])
                early_preds = [early_start[p] for p in preds]
                durations_preds = [durations[p] for p in preds]
                calc = f"max({', '.join(str(e + d) for e, d in zip(early_preds, durations_preds))})" if preds else "-"
                df_early.append([
                    task,
                    ", ".join(map(str, preds)) if preds else "",
                    ", ".join(map(str, early_preds)) if preds else "",
                    ", ".join(map(str, durations_preds)) if preds else "",
                    calc,
                    early_start[task]
                ])
            df_early = pd.DataFrame(df_early, columns=[
                "№ работы", "Предшественники", "Раннее начало пред.",
                "Длительность пред.", "Расчёт", "Итог раннего начала"
            ])

            # Таблица 2 – Позднее время
            df_late = []
            for task in G.nodes:
                succs = list(G.successors(task))
                latest_succs = [latest_start[s] for s in succs]
                calc = f"min({', '.join(str(ls - durations[task]) for ls in latest_succs)})" if succs else "-"
                df_late.append([
                    task,
                    ", ".join(map(str, succs)) if succs else "",
                    ", ".join(map(str, latest_succs)) if succs else "",
                    durations[task],
                    calc,
                    latest_start[task]
                ])
            df_late = pd.DataFrame(df_late, columns=[
                "№ работы", "Последователи", "Позднее начало посл.",
                "Длительность", "Расчёт", "Итог позднего начала"
            ])

            # Таблица 3 – Резервы
            df_reserve = pd.DataFrame([
                [t, early_start[t], latest_start[t], reserves[t]] for t in G.nodes
            ], columns=["№ работы", "Раннее начало", "Позднее начало", "Резерв"])

            # Сохраняем данные в session_state
            st.session_state["cpm_ready"] = True
            st.session_state["cpm_data"] = {
                "task_table": task_table,
                "df_early": df_early,
                "df_late": df_late,
                "df_reserve": df_reserve,
                "critical_path": critical_path,
                "duration": project_duration
            }

        except Exception as e:
            st.error(f"Ошибка CPM-анализа: {e}")
            st.session_state["cpm_ready"] = False

    # Отображение результата и кнопки экспорта
    if st.session_state.get("cpm_ready", False):
        data = st.session_state["cpm_data"]

        st.markdown("### 🧮 Таблица 1 – Раннее время начала работ")
        st.dataframe(data["df_early"], use_container_width=True)

        st.markdown("### 🕓 Таблица 2 – Позднее время начала работ")
        st.dataframe(data["df_late"], use_container_width=True)

        st.markdown("### 🧾 Таблица 3 – Резерв времени работ")
        st.dataframe(data["df_reserve"], use_container_width=True)

        st.success(f"🔴 Критический путь: {' → '.join(map(str, data['critical_path']))}")
        st.info(f"🕒 Общее время проекта: {data['duration']} дней")

        if st.button("📄 Сохранить отчет в Word"):
            buffer = save_report_to_word(
                title="Анализ критического пути",
                input_tables={"Исходные данные": data["task_table"]},
                output_tables={
                    "Таблица 1 – Раннее время": data["df_early"],
                    "Таблица 2 – Позднее время": data["df_late"],
                    "Таблица 3 – Резервы": data["df_reserve"],
                },
                texts=[
                    f"Критический путь: {' → '.join(map(str, data['critical_path']))}",
                    f"Общее время проекта: {data['duration']} дней"
                ]
            )
            st.download_button("⬇️ Скачать отчет", buffer, file_name="Критический_путь.docx")
