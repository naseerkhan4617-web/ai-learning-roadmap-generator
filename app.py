import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Streamlit page configuration
st.set_page_config(
    page_title="AI Learning Roadmap Generator",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Learning Roadmap Generator")
st.write("Generate a personalized learning roadmap using AI.")


# Check API key
if not api_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
    st.stop()


# Initialize Groq client
client = Groq(api_key=api_key)


# -----------------------------
# Function to read uploaded files
# -----------------------------
def read_file(uploaded_file):

    file_text = ""

    try:
        # TXT files
        if uploaded_file.type == "text/plain":
            file_text = uploaded_file.read().decode("utf-8")

        # PDF files
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)

            for page in pdf_reader.pages:
                text = page.extract_text()

                if text:
                    file_text += text + "\n"

    except Exception as e:
        return f"Error reading file: {str(e)}"

    return file_text


# -----------------------------
# User Inputs
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    domain = st.text_input(
        "📚 What do you want to learn?",
        placeholder="Example: Python, Machine Learning, Web Development"
    )

with col2:
    skill_level = st.selectbox(
        "🎯 Select your skill level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert"
        ]
    )


time_to_learn = st.text_input(
    "⏳ How much time do you have?",
    placeholder="Example: 30 days, 3 months, 10 hours per week"
)


learning_goal = st.text_area(
    "🎯 What is your learning goal?",
    placeholder="Example: I want to become a Machine Learning Engineer"
)


uploaded_files = st.file_uploader(
    "📁 Upload learning materials (Optional)",
    type=["txt", "pdf"],
    accept_multiple_files=True
)


# -----------------------------
# Generate Roadmap Button
# -----------------------------

if st.button("🚀 Generate My Learning Roadmap", use_container_width=True):

    if not domain:
        st.warning("⚠️ Please enter a domain or topic.")
        st.stop()

    if not time_to_learn:
        st.warning("⚠️ Please enter the time available for learning.")
        st.stop()


    # Read uploaded files
    uploaded_content = ""

    if uploaded_files:

        with st.spinner("📄 Reading uploaded files..."):

            for file in uploaded_files:

                uploaded_content += (
                    f"\n\n--- File: {file.name} ---\n"
                )

                uploaded_content += read_file(file)


    # Limit file content to avoid extremely large prompts
    uploaded_content = uploaded_content[:12000]


    # Create AI prompt
    prompt = f"""
You are an expert AI learning mentor and curriculum designer.

Create a personalized and practical learning roadmap.

DOMAIN:
{domain}

CURRENT SKILL LEVEL:
{skill_level}

TIME AVAILABLE:
{time_to_learn}

LEARNING GOAL:
{learning_goal}

UPLOADED LEARNING MATERIALS:
{uploaded_content if uploaded_content else "No files uploaded."}

Create a clear roadmap with:

1. A short overview of the learning journey
2. Learning phases in the correct order
3. Topics to learn in each phase
4. Important concepts
5. Practical projects for each phase
6. Suggested timeline based on the user's available time
7. Skills the user should have at the end
8. A final capstone project

Format the response using clean Markdown.

Make the roadmap practical, realistic, and suitable for the user's skill level.
"""


    # Generate response
    try:

        with st.spinner("🤖 AI is creating your roadmap..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert learning roadmap generator."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_completion_tokens=3000
            )


            roadmap = response.choices[0].message.content


        # Display roadmap
        st.success("✅ Your learning roadmap is ready!")

        st.markdown("---")

        st.markdown(roadmap)


        # Download button
        st.download_button(
            label="📥 Download Roadmap",
            data=roadmap,
            file_name="my_learning_roadmap.md",
            mime="text/markdown"
        )


    except Exception as e:

        st.error("❌ An error occurred while generating the roadmap.")

        st.exception(e)
