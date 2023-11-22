SSH_HOST = tortilla

sync:
	unison -repeat watch+3600 ./ ssh://tortilla/cvrace/from-movement

run:
	python3 camera-movement-test.py

run-remote:
	ssh tortilla 'cd cvrace/from-movement/ && make run'
