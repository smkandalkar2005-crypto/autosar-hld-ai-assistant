@echo off
echo Starting AUTOSAR HLD Document Analysis Assistant...
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

echo Generating sample AUTOSAR HLD documents if missing...
python generate_samples.py

echo Launching Streamlit Dashboard...
streamlit run app.py
pause
