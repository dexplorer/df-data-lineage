install: pyproject.toml
	pip install --upgrade pip &&\
	pip install --editable . 
	pip install .[cli] 
	pip install .[api] 
	pip install .[test]

lint:
	pylint --disable=R,C src/dl_app/*.py &&\
	pylint --disable=R,C src/dl_app/*/*.py &&\
	pylint --disable=R,C tests/*.py

test:
	python -m pytest -vv --cov=src/dl_app tests

format:
	black src/dl_app/*.py &&\
	black src/dl_app/*/*.py &&\
	black tests/*.py

all:
	install lint format test
