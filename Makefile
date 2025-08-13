.PHONY: install lint clean 

install:
	@echo "creating virtual environment..."
	python3 -m venv venv
	@echo "run: source venv/bin/activate"
	venv/bin/pip3 install -r scripts/requirements.txt

lint:
	venv/bin/python3 scripts/auto_fix.py 

clean:
	@echo "🧹 cleaning build artifacts and cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ cleanup complete!"
