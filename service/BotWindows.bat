@echo off
CALL ..\venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
python main.py