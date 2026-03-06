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
	python3 main.py > mprofile.txt 

pprofile:
	rm -f profile.dat pstats.txt
	python3 -m cProfile -o profile.dat main.py
	python3 -m pstats profile.dat > pstascalene run

install-deps:
	pip install -r requirements.txt

freeze-deps:
	pip freeze > requirements.txt
