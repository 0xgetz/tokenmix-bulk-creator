.PHONY: install test lint clean demo

install:
	python -m pip install -e ".[dev]"
	playwright install chromium

test:
	python -m pytest

demo:
	python -m tokenmix_bulk --count 1 --key-prefix demo

clean:
	rm -rf build dist *.egg-info .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
