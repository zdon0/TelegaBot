cd ..
source "venv/bin/activate"
pip install -r "service/requirements.txt"
clear
python "main.py"
deactivate
cd "service" || exit
