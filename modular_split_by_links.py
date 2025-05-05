import streamlit as st
import pandas as pd
import numpy as np
from word_export import save_report_to_word  # обязательно

def calculate_connectivity(G: np.ndarray):
    return np.sum(G, axis=1)

def split_by_connectivity(G: np.ndarray, T: float):
    n = G.shape[0]
    connectivity = calculate_connectivity(G)
    modules = []
    current_module = []

    for i in range(n):
        if connectivity[i] >= T:
            current_module.append(i + 1)
        else:
            if current_module:
                modules.append(current_module)
            current_module = [i + 1]
    if current_module:
        modules.append(current_module)

    return modules, connectivity

def run_modular_split_ui():
    st.subheader("🔗 Разбиение множества задач по связям")

    if "modular_ready" not in st.session_state:
        st.session_state["modular_ready"] = False
    if "modular_data" not in st.session_state:
        st.session_state["modular_data"] = {}

    st.markdown("Введите верхнетреугольную матрицу связей G (только значения выше главной диагонали):")
    size = 7
    default_data = np.zeros((size, size))
    default_data[0][1] = 2
    default_data[0][2] = 3
    default_data[1][2] = 1
    default_data[2][3] = 4
    default_data[3][4] = 2
    default_data[4][5] = 1
    default_data[5][6] = 3

    df_default = pd.DataFrame(default_data, columns=[f"{i+1}" for i in range(size)], index=[f"{i+1}" for i in range(size)])

    df_G = st.data_editor(
        df_default,
        num_rows="fixed",
        use_container_width=True,
        hide_index=False,
        key="modular_editor"
    )

    if st.button("🚀 Разбить на модули"):
        try:
            G = df_G.to_numpy(dtype=float)
            np.fill_diagonal(G, 0)

            conn = calculate_connectivity(G)
            T = np.mean(conn)
            modules, _ = split_by_connectivity(G, T)

            df_conn = pd.DataFrame({
                "Задача": [f"{i+1}" for i in range(len(conn))],
                "Степень связности": conn
            })

            results_text = [f"Порог связности: T = {T:.2f}"]
            for i, mod in enumerate(modules, 1):
                line = f"Модуль {i}: {', '.join(map(str, mod))}"
                results_text.append(line)

            st.session_state["modular_data"] = {
                "matrix": df_G,
                "connectivity": df_conn,
                "texts": results_text
            }
            st.session_state["modular_ready"] = True

        except Exception as e:
            st.session_state["modular_ready"] = False
            st.error(f"Ошибка обработки: {e}")

    # Вывод результатов, если уже считано
    if st.session_state.get("modular_ready"):
        st.markdown("### 📈 Степени связности задач:")
        st.dataframe(st.session_state["modular_data"]["connectivity"])

        st.markdown(f"### 🧠 Порог связности T")
        st.markdown(f"**{st.session_state['modular_data']['texts'][0]}**")

        st.markdown("### 📦 Результат разбиения:")
        for line in st.session_state["modular_data"]["texts"][1:]:
            st.markdown(f"**{line}**")

        if st.button("📄 Сохранить отчет в Word"):
            buffer = save_report_to_word(
                title="Разбиение множества задач по связям",
                input_tables={"Матрица связей G": st.session_state["modular_data"]["matrix"]},
                output_tables={"Степени связности": st.session_state["modular_data"]["connectivity"]},
                texts=st.session_state["modular_data"]["texts"]
            )
            st.download_button("⬇️ Скачать отчет", buffer, file_name="Разбиение_по_связям.docx")
