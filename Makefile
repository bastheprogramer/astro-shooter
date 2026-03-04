.PHONY: run build clean

run:
	python3 main.py

build:
	rm -rf build dist *.spec
	pyinstaller main.py \
		--windowed \
		--add-data "sprites:sprites" \
		--add-data "sounds:sounds" \
		--name "Astro shooter" 
		

clean:
	rm -rf build dist *.spec

mprofile:
	rm -f memory_profile.dat memray-flamegraph-memory_profile.html
	memray run -o memory_profile.dat main.py
	memray flamegraph memory_profile.dat

pprofile:
	rm -f profile.dat pstats.txt
	python3 -m cProfile -o profile.dat main.py
	python3 -m pstats profile.dat > pstascalene run

install-deps:
	pip install -r requirements.txt

freeze-deps:
	pip freeze > requirements.txt
