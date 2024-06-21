install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

run:
	venv/bin/python3 main.py

uninstall:
	rm -rf venv

clean:
	rm -rf */__pycache__/ __pycache__/
