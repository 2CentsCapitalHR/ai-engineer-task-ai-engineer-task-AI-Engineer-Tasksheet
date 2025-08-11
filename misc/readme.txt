# Create project folder
mkdir adgm_corporate_agent
cd adgm_corporate_agent

# Create venv with Python 3.10
/opt/homebrew/bin/python3.10 -m venv corporate_agent_env

# Activate venv
source corporate_agent_env/bin/activate



pip install faiss-cpu sentence-transformers pypdf langchain



ollama serve

streamlit run app.py
