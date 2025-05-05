import streamlit as st
import pandas as pd
from word_export import save_report_to_word

def create_matrix_X(tasks_files, partition):
    X = []
    for task in sorted(tasks_files.keys()):
        row = [int(task in group) for group in partition]
        X.append(row)
    return X

def create_matrix_Y(tasks_files, partition):
    all_files = sorted({f for files in tasks_files.values() for f in files})
    file_index = {f: i for i, f in enumerate(all_files)}
    Y = [[0]*len(partition) for _ in all_files]
    for j, module in enumerate(partition):
        module_files = set()
        for task in module:
            module_files |= tasks_files.get(task, set())
        for f in module_files:
            Y[file_index[f]][j] = 1
    return Y, all_files

def calculate_quality(Y):
    return sum(sum(row) - 1 for row in Y if sum(row) > 1)

def run_module_partition_ui():
    st.subheader("Разбиение на модули по критерию независимости информации")
    st.markdown("### 👇 Введите данные")

    if "mod_ready" not in st.session_state:
        st.session_state["mod_ready"] = False
    if "mod_data" not in st.session_state:
        st.session_state["mod_data"] = {}

    st.markdown("#### 🗂️ Задачи и обрабатываемые файлы")
    task_df = st.data_editor(
        pd.DataFrame({
            "Задача": [1, 2, 3, 4, 5, 6, 7],
            "Файлы (через пробел или запятую)": ["1,2,3", "2", "2 5", "3 4", "1,5,7", "5,6", "7 8"]
        }),
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="module_editor"
    )

    num_modules = st.slider("Сколько модулей в каждом варианте разбиения?", min_value=2, max_value=10, value=3)

    # Значения по умолчанию, каждая задача — отдельная строка
    default_modules = {
        "Модуль 1": ["1", "4", "8"],
        "Модуль 2": ["2", "5", "9"],
        "Модуль 3": ["3", "6", "7"],
    }

    # Собираем столбцы
    module_columns = {}
    for i in range(num_modules):
        col_name = f"Модуль {i + 1}"
        default_col = default_modules.get(col_name, [""] * 3)
        module_columns[col_name] = default_col

    # Создаём датафрейм
    default_partition = pd.DataFrame(module_columns)

    # Отображаем editor
    partition_df = st.data_editor(
        default_partition,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="partition_editor"
    )

    modules_partitions = []
    for _, row in partition_df.dropna().iterrows():
        modules = []
        for col in partition_df.columns:
            cell = str(row[col]).strip()
            if cell:
                module = list(map(int, cell.replace(",", " ").split()))
                modules.append(module)
        if modules:
            modules_partitions.append(tuple(modules))

    if st.button("РЕШИТЬ"):
        try:
            tasks_files = {}
            for _, row in task_df.dropna().iterrows():
                task_str = str(row["Задача"]).strip()
                files_str = str(row["Файлы (через пробел или запятую)"]).strip()
                if task_str and files_str:
                    task = int(float(task_str))
                    files = set(map(int, files_str.replace(",", " ").split()))
                    tasks_files[task] = files

            partitions_data = []
            for idx, partition in enumerate(modules_partitions):
                X = create_matrix_X(tasks_files, partition)
                df_X = pd.DataFrame(X,
                    columns=[f"M{i + 1}" for i in range(len(partition))],
                    index=[f"Задача {i}" for i in range(1, len(tasks_files) + 1)])

                Y, all_files = create_matrix_Y(tasks_files, partition)
                df_Y = pd.DataFrame(Y,
                    columns=[f"M{i + 1}" for i in range(len(partition))],
                    index=[f"Файл {f}" for f in all_files])

                quality = calculate_quality(Y)

                partitions_data.append({
                    "partition": partition,
                    "df_X": df_X,
                    "df_Y": df_Y,
                    "quality": quality
                })

            st.session_state["mod_data"] = {
                "input": task_df,
                "results": partitions_data
            }
            st.session_state["mod_ready"] = True

        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
            st.session_state["mod_ready"] = False

    if st.session_state.get("mod_ready", False):
        results = st.session_state["mod_data"]

        for i, res in enumerate(results["results"], 1):
            st.markdown(f"---\n### 🔹 Вариант {i}: {res['partition']}")

            st.markdown("**📘 Матрица X (Задачи vs Модули):**")
            st.dataframe(res["df_X"])

            st.markdown("**📗 Матрица Y (Файлы vs Модули):**")
            st.dataframe(res["df_Y"])

            st.success(f"📊 Критерий качества (перекрытия файлов): **{res['quality']}**")

        if st.button("📄 Сохранить отчет в Word"):
            tables = {"Исходные данные": results["input"]}
            texts = []

            for i, res in enumerate(results["results"], 1):
                tables[f"Вариант {i} – Матрица X"] = res["df_X"]
                tables[f"Вариант {i} – Матрица Y"] = res["df_Y"]
                texts.append(f"Вариант {i}: Критерий качества = {res['quality']}")

            buffer = save_report_to_word(
                title="Разбиение на модули",
                input_tables={"Исходные данные": results["input"]},
                output_tables=tables,
                texts=texts
            )
            st.download_button("⬇️ Скачать отчет", buffer, file_name="Разбиение_на_модули.docx")
