cycle:
	cat config/oneshot_rss.tsv | python src/read_rss.py
run:
	cat config/sample_rss_feeds.tsv | python src/read_rss.py
media_thumbnail:
	cat config/sample_rss_feeds.tsv| grep bbc-eng | python src/read_rss.py
media_content:
	cat config/sample_rss_feeds.tsv| grep cnn-us | python src/read_rss.py
tags:
	cat config/sample_rss_feeds.tsv | grep nyt-world | python src/read_rss.py
harvest:
	scripts/harvest.sh
format:
	black src/*.py src/lib/*.py src/lib/util/*.py
dev: install
	pip install -r requirements-dev.txt
install:
	pip install -r requirements.txt
