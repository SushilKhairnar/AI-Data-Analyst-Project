import streamlit as st
from ai_engine import ask_question

st.title("AI Data Analyst Copilot")
st.write(
    "Ask questions about company data, policies, customers, "
    "products, employees, and business performance."
)

question = st.text_input(
    "Enter your question:"
)

if st.button("Ask Question"):
    if question.strip() == "":
        st.warning(
            "Please enter a question."
        )
    else:
        try:
            data = ask_question(
                question
            )
            if isinstance(data, dict):
                st.subheader("Answer")
                st.write(
                    data["answer"]
                )
                if data["chart_path"] is not None:
                    st.subheader("Chart")
                    st.image(
                        data["chart_path"]
                    )
            else:
                st.subheader("Answer")
                st.write(data)
        except Exception as e:
            st.error(
                "An error occurred while processing your question."
            )
            st.write(
                str(e)
            )