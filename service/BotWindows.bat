@echo off
CALL ..\venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
cls
python main.py
pause