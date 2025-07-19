import os
import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# --- App Title ---
st.markdown("<h1 style='text-align: center;'>🧑‍🏫 AI Study Coach</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- File Upload ---
uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")

if uploaded_file is not None:
    pdf_reader = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in pdf_reader:
        text += page.get_text()
    st.session_state.pdf_text = text

    st.markdown("#### 🧾 Extracted PDF Content:")
    st.text_area("PDF Text", value=st.session_state.pdf_text, height=200, disabled=True)

# --- Summarize Document ---
if st.button("📝 Summarize this Document"):
    if st.session_state.pdf_text:
        summary_prompt = f"Summarize the following document:\n{st.session_state.pdf_text}"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        st.session_state.summary = response.choices[0].message.content
    else:
        st.warning("Please upload a PDF first.")

# --- Display Summary ---
if st.session_state.summary:
    st.markdown("### 📄 Summary of Uploaded Document:")
    st.write(st.session_state.summary)

st.markdown("---")

# --- Display Chat History ---
if st.session_state.chat_history:
    st.markdown("### 🧠 Chat History:")
    for turn in st.session_state.chat_history:
        if turn["role"] == "user":
            st.markdown(
                f"""
                <div style="background-color:#555555; padding:10px 15px; border-radius:10px; margin:5px 0; max-width:80%; text-align:left">
                    <strong>💬 You:</strong><br>{turn['content']}
                </div>
                """, unsafe_allow_html=True
            )
        elif turn["role"] == "assistant":
            st.markdown(
                f"""
                <div style="background-color:#1a1a1a; padding:10px 15px; border-radius:10px; margin:5px 0; max-width:80%; text-align:left">
                    <strong>🤖 AI Coach:</strong><br>{turn['content']}
                </div>
                """, unsafe_allow_html=True
            )

# --- Restart Conversation ---
if st.button("🔄 Restart Conversation"):
    st.session_state.chat_history = []
    st.session_state.summary = ""
    st.session_state.pdf_text = ""
    st.rerun()

# --- Chat Input (Always at Bottom) ---
st.markdown("### 💬 Ask a Question:")

with st.form(key="chat_form", clear_on_submit=True):
    user_query = st.text_input("Your question about the document", placeholder="Ask me something about the uploaded content...", key="user_query")
    submit = st.form_submit_button("Submit")

if submit and user_query:
    prompt = f"PDF Content:\n{st.session_state.pdf_text}\n\nUser Question: {user_query}"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an AI study assistant that answers based on the given document."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content

    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

