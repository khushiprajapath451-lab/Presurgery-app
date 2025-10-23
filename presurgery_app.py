import streamlit as st
from google import genai
from google.genai.types import Part
from fpdf import FPDF

# ====================
# Configuration
# ====================
PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
LOCATION = "us-west4"                # Or your preferred region

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
MODEL_ID = "gemini-2.0-flash-001"

# Create chat session once
chat = client.chat.create(model=MODEL_ID, config={"temperature": 0})

# ====================
# Streamlit UI Styling
# ====================
st.set_page_config(page_title="MedEase – Pre-Surgery Companion", page_icon="🩺", layout="centered")

st.markdown("""
    <style>
    body {background-color: #f0faff; font-family: 'Segoe UI', sans-serif;}
    .stButton>button {
        color:white;
        background-color:#0077b6;
        border-radius:10px;
        height:3em;
        width:16em;
        font-size:1.05em;
        font-weight:600;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius:8px;
        border:1px solid #0077b6;
        padding:6px;
    }
    </style>
""", unsafe_allow_html=True)

# ====================
# Main UI
# ====================
st.title("🩺 MedEase – Your Pre-Surgery Preparation Companion")
st.markdown("Hi! I’m **MedEase**, your AI assistant. Answer a few quick questions and get a personalized pre-surgery guide.")

age = st.number_input("👶 Age", min_value=0, max_value=120)
health_conditions = st.text_input("💊 Pre-existing health conditions (comma-separated)")
medications = st.text_input("💉 Medications currently taking (comma-separated)")
surgery_type = st.text_input("🏥 Surgery Type")
additional_info = st.text_area("🗒️ Additional Information")

def build_prompt(age, conditions, meds, surgery, additional):
    return f"""
    You are an AI assistant helping patients prepare for surgery.
    Patient age: {age}
    Health conditions: {conditions}
    Medications: {meds}
    Surgery type: {surgery}
    Additional info: {additional}

    Provide:
    1. A warm, clear pre-surgery guide.
    2. A checklist of precautions.
    3. Diet and rest instructions.
    4. Common risks or warning signs.
    5. A motivational message for the patient.

    Use markdown formatting and simple tone.
    """

if st.button("✨ Generate Preparation Guide"):
    with st.spinner("Preparing your personalized guide..."):
        prompt_text = build_prompt(age, health_conditions, medications, surgery_type, additional_info)
        response = chat.send_message(Part.from_text(text=prompt_text))
        guide_text = response.text

    st.success("✅ Your Personalized Pre-Surgery Guide is Ready!")
    st.markdown("---")
    st.subheader("📘 Your Guide")
    st.markdown(guide_text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, guide_text)
    pdf_file = "presurgery_guide.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button("📄 Download as PDF", f, file_name="MedEase_Presurgery_Guide.pdf", mime="application/pdf")

st.markdown("---")
st.subheader("💬 Chat with MedEase")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat_msg in st.session_state.chat_history:
    with st.chat_message(chat_msg["role"]):
        st.markdown(chat_msg["content"])

if user_input := st.chat_input("Ask MedEase anything about surgery preparation..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    chat_prompt = f"""
    You are MedEase, a gentle, medically accurate AI assistant.
    Patient Question: {user_input}
    Provide calm, supportive, general surgical guidance with self-care reminders.
    """

    with st.chat_message("assistant"):
        with st.spinner("MedEase is thinking..."):
            ai_response = chat.send_message(Part.from_text(text=chat_prompt)).text
            st.markdown(ai_response)

    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

st.markdown("---")
st.markdown("🌸 **MedEase** is for educational purposes only. Always consult your doctor before any medical decisions.")
