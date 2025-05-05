import streamlit as st

def show_faq():
    with st.expander("❓ FAQ (Руководство пользователя)"):
        try:
            with open("faq.txt", "r", encoding="utf-8") as f:
                faq_text = f.read()
            st.markdown(faq_text)
        except FileNotFoundError:
            st.warning("Файл faq.txt не найден. Пожалуйста, создайте его в корне проекта.")
