flair-markup:
	cat cache/dedupe.jsonl | python src/flair_markup.py > cache/markup.jsonl
gemtest2:
	python src/lib/geminiai.py --prompt_file=/Users/kyle/prompts/dottest0.txt
gemtest:
	python src/lib/geminiai.py --prompt_file=/Users/kyle/prompts/promNavy.txt --system_prompt_file=/Users/kyle/prompts/sysdot0.txt
nerd:
	cat cache/11rec.jsonl | python src/nerd.py
rmchroma:
	rm -Rf chroma/*
entities:
	jq -r '.id as $id | .ner[] | .spans[] | [$id, .text, .value, .sentiment] | @tsv' cache/dedupe.jsonl > cache/entities.tsv
entities2:
	jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' cache/dedupe.jsonl | sort | uniq > cache/entities2.tsv
clearcache:
	rm cache/articles.json
	rm cache/counter.json
grootconn:
	cypher-shell -u neo4j -p $NEO4J_PASS -a neo4j://groot:7687
neo4jmac:
	docker run --restart always --publish=7474:7474 --publish=7687:7687 --env NEO4J_AUTH=neo4j/$NEO4J_PASS --volume=/Users/kyle/hub/Pheme-News/neo4j:/data neo4j:latest
neo4j:
	docker compose up
testload:
	cypher-shell -u neo4j -p $NEO4J_PASS -f testrun4.cypher -d neo4j
sampleload:
	cypher-shell -u neo4j -p $NEO4J_PASS -f sample.cypher -d neo4j
load:
	cypher-shell -u neo4j -p $NEO4J_PASS -f run4.cypher -d neo4j
grootload:
	cypher-shell -u neo4j -p ${NEO4J_PASS} -a neo4j://groot:7687 -f run4.cypher -d neo4j
analize:
	head run3.jsonl | src/analize.py > analize.txt
oneshot:
	cat config/oneshot_rss.tsv | python src/read_rss.py > cache/read_rss.jsonl
run1pol:
	cat config/political_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
run1:
	cat config/sample_rss_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
run2:
	cat cache/read_rss.jsonl | python src/tallyman.py > cache/tallyman.jsonl
run3:
	cat cache/tallyman.jsonl | python src/read_article.py > cache/read_article.jsonl
run4:
	cat cache/read_article.jsonl | grep '"art"' > cache/art.jsonl
run5:
	cat cache/art.jsonl | python src/flair_news.py | egrep '^\{' > cache/flair_news.jsonl
run6:
	cat cache/flair_news.jsonl | python src/dedupe.py > cache/dedupe.jsonl
run6init:
	cat cache/flair_news.jsonl | python src/dedupe_init.py
run7:
	cat cache/dedupe.jsonl| python src/vectorize.py
run8:
	cat cache/dedupe.jsonl | python src/cypher.py > cache/cypher.cypher
testrun:
	head -n 1 batch-0.tsv | python src/read_rss.py | python src/read_article.py | grep '"art"' | tee testrun.jsonl | python src/sentiment.py | grep CREATE > testrun.cypher
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
