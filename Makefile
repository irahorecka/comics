black: ## Black format every python file to line length 100
	find . -type f -name "*.py" | xargs black --line-length=100;
	make clean;

flake8: ## Flake8 every python file
	find . -type f -name "*.py" -a | xargs flake8;

pylint: ## pylint every python file
	find . -type f -name "*.py" -a | xargs pylint;

clean: ## Remove caches and .DS_Store
	find . -type d -name "__pycache__" | xargs rm -r;
	find . -type f -name ".DS_Store" | xargs rm -r;
