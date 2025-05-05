import streamlit as st
import pandas as pd
import numpy as np
from word_export import save_report_to_word  # Не забудь этот импорт

def build_incidence_matrix(edges):
    nodes = sorted(set([e[0] for e in edges] + [e[1] for e in edges]))
    node_index = {node: i for i, node in enumerate(nodes)}
    matrix = np.zeros((len(nodes), len(nodes)), dtype=int)

    for src, dst in edges:
        matrix[node_index[src]][node_index[dst]] = 1

    return pd.DataFrame(matrix, index=nodes, columns=nodes)

def classify_tasks(inc_matrix):
    matrix = inc_matrix.copy()
    classes = []
    while not matrix.empty:
        zero_in = matrix.sum(axis=0)
        current_class = zero_in[zero_in == 0].index.tolist()
        if not current_class:
            return None
        classes.append(current_class)
        matrix = matrix.drop(index=current_class, columns=current_class)
    return classes

def run_task_ordering_ui():
    st.subheader("📐 Упорядочение множества задач (Классификация по уровням)")

    if "ordering_ready" not in st.session_state:
        st.session_state["ordering_ready"] = False
    if "ordering_data" not in st.session_state:
        st.session_state["ordering_data"] = {}

    st.markdown("Введите список дуг между задачами:")
    default_edges = pd.DataFrame({
        "Из задачи": [1, 1, 3],
        "В задачу": [' ' + str(i) for i in [2, 3, 4]]
    })

    edge_df = st.data_editor(
        default_edges,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    if st.button("📊 Упорядочить задачи"):
        try:
            edges = [(int(row["Из задачи"]), int(row["В задачу"])) for _, row in edge_df.iterrows()]
            matrix = build_incidence_matrix(edges)
            result = classify_tasks(matrix)

            if result is None:
                st.session_state["ordering_ready"] = False
                st.error("⚠️ Обнаружен цикл в графе! Упорядочивание невозможно.")
            else:
                texts = []
                for i, cls in enumerate(result, 1):
                    txt = f"Класс {i}: {', '.join(map(str, cls))}"
                    texts.append(txt)

                st.session_state["ordering_data"] = {
                    "edges": edge_df,
                    "matrix": matrix,
                    "texts": texts
                }
                st.session_state["ordering_ready"] = True

        except Exception as e:
            st.session_state["ordering_ready"] = False
            st.error(f"Ошибка обработки: {e}")

    if st.session_state.get("ordering_ready"):
        st.markdown("### 📄 Матрица инциденций")
        st.dataframe(st.session_state["ordering_data"]["matrix"])

        st.markdown("### 🧩 Упорядоченные классы задач:")
        for line in st.session_state["ordering_data"]["texts"]:
            st.markdown(f"**{line}**")

        if st.button("📄 Сохранить отчет в Word"):
            buffer = save_report_to_word(
                title="Упорядочивание задач",
                input_tables={"Список дуг": st.session_state["ordering_data"]["edges"]},
                output_tables={"Матрица инциденций": st.session_state["ordering_data"]["matrix"]},
                texts=st.session_state["ordering_data"]["texts"]
            )
            st.download_button("⬇️ Скачать отчет", buffer, file_name="Упорядочивание_задач.docx")
