🧮 MathsGPT — AI-Powered Math Problem Solver

A full-stack project using React (Vite + Tailwind) + Python (Streamlit + LangChain + Groq)

🚀 Overview

MathsGPT is an AI-based math problem solver that can answer word problems, equations, algebra, calculus, and more.
It combines a modern React frontend with a Python backend powered by LangChain + Groq API and (optional) SymPy for symbolic math solving.

This project is designed for learning full-stack AI apps, frontend-backend integration, and LLM tool usage.

🛠️ Tech Stack
Frontend

React (Vite)

TypeScript (TSX)

Tailwind CSS

Modern UI components & clean layout

Backend

Python 3.x

Streamlit (UI + backend API style)

LangChain

Groq API (Llama 3 / Gemma models)

SymPy (optional math solving)

Wikipedia API (optional lookups)

📁 Folder Structure
mathsgpt/    
│    
├── maths-gpt-frontend/       # Full React frontend (Vite + TS + Tailwind)    
│   ├── src/    
│   │   ├── App.tsx    
│   │   ├── main.tsx    
│   │   ├── index.css    
│   │   └── components/ (if any)    
│   ├── index.html    
│   ├── package.json    
│   ├── vite.config.ts    
│   └── tailwind/postcss configs    
│    
├── app.py                    # Python backend (Streamlit + LangChain + SymPy)    
├── requirements.txt          # Python dependencies    
└── README.md                 # You're reading it!    

⚙️ Installation & Setup
🖥️ 1. Clone the Repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

🌐 Frontend Setup (React + Vite + Tailwind)
📦 Install dependencies
cd maths-gpt-frontend
npm install

▶️ Start development server
npm run dev


This will start the React UI at:

👉 http://localhost:5173/

(or the next available port)

🧰 Backend Setup (Python + Streamlit)
🐍 Create a virtual environment (optional but recommended)    
python -m venv venv    
source venv/bin/activate       # Mac/Linux    
venv\Scripts\activate          # Windows    

📦 Install dependencies
pip install -r requirements.txt

🔑 Add Groq API Key

Create a file named .env:

GROQ_API_KEY=your_api_key_here

▶️ Run backend
streamlit run app.py


Backend will start at:

👉 http://localhost:8501/    
 (default Streamlit port)    

🔗 Connecting Frontend & Backend

Frontend calls backend at:

POST /api/ask


Configure the proxy in vite.config.ts:

server: {    
  proxy: {    
    "/api": {    
      target: "http://localhost:8501",    
      changeOrigin: true,    
      secure: false,    
    }    
  }    
}    

🧪 Features
✔️ Equation solving

Example:

Solve x^2 – 5x + 6 = 0

✔️ Word problem solving    

Example:    

Sarah has twice as many apples as Tom...    

✔️ Step-by-step math logic (SymPy + LLM)    
✔️ Works offline for algebra (SymPy)    
✔️ LLM fallback (Groq API)    
✔️ Clean frontend UI with:    

History    

Quick actions    

Model selector    

Error handling    

📌 Roadmap

 Add image upload for handwritten problems

 Add LaTeX rendering

 Add more model support (Groq, OpenAI, DeepSeek)

 Add user authentication

 Deploy on Vercel + Streamlit Cloud

🙌 Author

👤 Vaibhav Sharma
AI Developer | React | Python | Machine Learning    
📎 LinkedIn: https://www.linkedin.com/in/vaibhav-sharma-14b717321/

⭐ Support

If you like this project:

Star ⭐ the repo on GitHub — it really helps!
