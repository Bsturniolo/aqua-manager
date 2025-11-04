# aqua_manager/Makefile
.PHONY: run test clean
run:
	python3 src/main.py
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
clean:
	find . -name "__pycache__" -type d -exec rm -r {} + || true
	rm -rf data || true
