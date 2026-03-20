.PHONY: run build clean mprofile pprofile install-deps freeze-deps

OS := $(shell uname)

ifeq ($(OS),Darwin)
	DATASEP := :
	EXTRA_FLAGS :=
else
	DATASEP := ;
	EXTRA_FLAGS := --onefile
endif


run:
	python3 main.py


build:
	rm -rf build dist *.spec
	pyinstaller main.py \
		--windowed \
		$(EXTRA_FLAGS) \
		--collect-all jaraco \
		--add-data "sprites$(DATASEP)sprites" \
		--add-data "sounds$(DATASEP)sounds" \
		--name "Astro shooter"


clean:
	rm -rf build dist *.spec


mprofile:
	python3 main.py > mprofile.txt


pprofile:
	rm -f profile.dat pstats.txt
	python3 -m cProfile -o profile.dat main.py
	python3 -m pstats profile.dat > pstats.txt


install-deps:
	pip install -r requirements.txt


freeze-deps:
	pip freeze > requirements.txt