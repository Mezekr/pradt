install: 
	@echo "Installing..."
	pipenv install --ignore-pipfile

activate:
	@echo "Activating virtual environment"
	pipenv shell

setdds:
	@echo "Create directories to save and process Data"
	python src/create_data_dirs.py

