#for first time
python -m venv myenv
myenv/Scripts/Activate
pip install -r requirements.txt


for every run
myenv/Scripts/Activate
uvicorn main:app --reload


my name is Umar