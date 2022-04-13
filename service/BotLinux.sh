cd ..
source "venv/bin/activate"
pip install -r "service/requirements.txt"
python "main.py"
deactivate
cd "service" || exit
