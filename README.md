# 📄 AI Research Paper Assistant – Chat with PDF

> **College B.Tech AI Assignment Project**  
> An AI-powered web application that enables students to upload academic research papers in PDF format and ask questions about their content. The system extracts text across all pages and uses the official Google Gemini API to deliver grounded, factual explanations in simple, student-friendly English.

---

## 🌟 Key Features

1. **Multi-Page PDF Processing (`pypdf`)**:
   - Upload any academic paper in PDF format.
   - Extracts readable digital text across all pages.
   - Preserves page demarcation (`[Page X]`) for citation transparency.
   - Resilient error handling for empty (0 bytes), password-protected, corrupted, or scanned image-only PDFs without crashing.

2. **Strict Grounded AI Answers (`google-genai` SDK)**:
   - Uses the official `google-genai` SDK with the high-speed `gemini-2.5-flash` model (and automatic fallbacks).
   - **Zero Hallucination**: The AI answers strictly using information found in the uploaded paper.
   - **Absence Guarantee**: If an answer is not mentioned in the paper, it responds with the exact phrase:
     > `"This is not mentioned in the paper."`
   - Explains complex academic jargon and mathematical concepts in simple, accessible bullet points.

3. **Persistent Chat & Session Management**:
   - Interactive chat interface with separate user and assistant message bubbles.
   - Conversation history preserved across multiple questions on the same paper.
   - One-click **Clear Chat History** button.
   - Automatic session reset when a new PDF document is uploaded.

4. **Modern UI/UX Design**:
   - Clean, professional aesthetic featuring white and light-blue background gradients with royal blue and purple accents.
   - Responsive sidebar with document statistics (pages, word count, character count).
   - Interactive quick-start question chips.
   - Real-time animated loading spinner while Gemini analyzes the document.

5. **Security First**:
   - Zero hardcoded credentials.
   - Reads API keys securely from `.streamlit/secrets.toml` or environment variables.
   - Optional masked password input fallback in the sidebar.
   - `.gitignore` configured to prevent accidental leaks.

---

## 📁 Project Structure

```text
research_paper_chatbot/
│
├── app.py                      # Main Streamlit web application & AI logic
├── requirements.txt            # Python dependencies (Streamlit, google-genai, pypdf)
├── README.md                   # Full documentation & assignment report guide
├── .gitignore                  # Git ignore rules for secrets, cache & virtual env
├── sample_research_paper.pdf   # Pre-generated sample research paper for instant testing
│
└── .streamlit/
    ├── secrets.toml.example    # Template showing how to store your Gemini API key
    └── secrets.toml            # (Local only) Your actual private Gemini API key
```

---

## 🚀 Step-by-Step Setup & Run Guide

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File > Open Folder...** and select the `research_paper_chatbot` folder.
3. Open the built-in terminal in VS Code:
   - Press `` Ctrl + ` `` (Control + Backtick) or go to **Terminal > New Terminal**.

---

### Step 2: Create and Activate a Python Virtual Environment

```bash
# Windows (PowerShell / Command Prompt)
python -m venv .venv

# Activate the virtual environment
# In PowerShell:
.\.venv\Scripts\Activate.ps1

# In Command Prompt (cmd):
.\.venv\Scripts\activate.bat
```

> **Note for PowerShell execution policy:** If you encounter an execution policy warning, run:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

### Step 3: Install Required Dependencies

Install the official libraries:

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` (Modern web frontend)
- `google-genai` (Official Google Gemini SDK)
- `pypdf` (PDF text parsing engine)

---

### Step 4: Get a Free Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **"Create API Key"** and copy the generated key.

---

### Step 5: Configure the API Key Securely

Inside the `.streamlit` directory:
1. Make a copy of `secrets.toml.example` and name it `secrets.toml`:
   ```bash
   # In Windows PowerShell:
   Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Open `.streamlit/secrets.toml` in VS Code and paste your key:
   ```toml
   GEMINI_API_KEY = "AIzaSyYourActualApiKeyHere"
   ```

*(Alternatively, you can also paste your API key directly into the password-masked input in the app's sidebar during runtime.)*

---

### Step 6: Launch the Web Application

Run the Streamlit application:

```bash
streamlit run app.py
```

Your default browser will automatically open:  
👉 **http://localhost:8501**

---

## 🧪 Testing Guide

We have included a pre-generated academic paper: `sample_research_paper.pdf` (*"Deep Learning Approaches for Automated Medical Diagnosis: An Empirical Study"*).

### Test Case 1: Upload and Verification
1. Click **"Browse files"** in the sidebar and select `sample_research_paper.pdf`.
2. Notice the green success alert and the sidebar card showing:
   - **Document Name**: `sample_research_paper.pdf`
   - **Pages**: 2 Pages
   - **Word Count**: ~247 Words

### Test Case 2: Grounded Q&A (Content Present)
Ask the following questions in the chat box:
- **Question**: *"What is the name of the proposed neural network architecture and what is its accuracy?"*
  - **Expected Answer**: MedVisionNet, achieving an accuracy of 94.8% on the test benchmark.
- **Question**: *"What are the limitations of this study?"*
  - **Expected Answer**: The dataset primarily contains adult cohorts (pediatric data was not evaluated), and performance degrades under extreme optical motion blur.

### Test Case 3: Negative Grounding (Information Not in Paper)
- **Question**: *"What is the population of Tokyo?"* or *"Who won the 2022 FIFA World Cup?"*
  - **Expected Answer**:
    > `This is not mentioned in the paper.`

### Test Case 4: Clear Chat & Document Switching
1. Click **"🗑️ Clear Chat History"** in the sidebar. All previous messages will be cleared.
2. Upload a new PDF. Notice that the chat history automatically resets for the new document.

### Test Case 5: Error Handling
- **Empty PDF**: Upload a 0-byte file -> Displays *"The uploaded file is empty (0 bytes)"*.
- **Invalid File**: Upload a corrupted non-PDF -> Displays *"Unable to parse... The file appears corrupted"*.
- **Missing API Key**: Leave the key empty -> Alerts *"Gemini API Key Missing"*.

---

## 📸 How to Take Screenshots for Your College Assignment

For your project submission report or presentation slides:

1. **Screenshot 1: Welcome & UI State**
   - Take a screenshot of the homepage before uploading a document.
   - Highlights the modern hero header, blue/purple gradient banner, and sidebar.

2. **Screenshot 2: Document Loaded & Sidebar Metadata**
   - Upload `sample_research_paper.pdf`.
   - Capture the sidebar displaying the active document card (page count, word count, character count) and the green API key active badge.

3. **Screenshot 3: Grounded Answers with Formatted Explanations**
   - Ask: *"Summarize the methodology of MedVisionNet and its experimental results."*
   - Capture the clean chat bubble showing headings, bullet points, and citations.

4. **Screenshot 4: Grounded Absence Test ("Not mentioned")**
   - Ask an out-of-context question like *"What is quantum computing?"*
   - Capture the exact AI response: `"This is not mentioned in the paper."` to prove strict adherence to the project problem statement.

---

## 🛡️ Academic Integrity & Security Note
- Never commit `secrets.toml` or any file containing your Gemini API key to public repositories (such as GitHub).
- The included `.gitignore` protects `.streamlit/secrets.toml` by default.
