import streamlit as st
import requests

st.title("AI Data Analyst Copilot")
st.write(
    "Ask questions about company data, policies, customers, "
    "products, employees, and business performance."
)

question = st.text_input("Enter your question:")

if st.button("Ask Question"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={
                "question": question
            }
        )
        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            if data["chart_path"] is not None:
                st.subheader("Chart")
                st.image(
                    "http://127.0.0.1:8000/chart"
                )
        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)