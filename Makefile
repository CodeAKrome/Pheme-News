cycle:
	cat config/oneshot_rss.tsv | src src/read_rss.py
harvest:
	scripts/harvest.sh
format:
	black src/*.py src/lib/*.py
dev: install
	pip install -r requirements-dev.txt
install:
	pip install -r requirements.txt