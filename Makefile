.PHONY: run build clean

run:
	python3 main.py

build:
	pyinstaller main.py --windowed \
		--add-data "sprites:sprites" \
		--add-data "sounds:sounds"

clean:
	rm -rf build dist *.spec

mprofile:
	mprof run main.py
	mprof plot


install-deps:
	pip install -r requirements.txt

freeze-deps:
	pip freeze > requirements.txt
