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
cycle:
	cat config/oneshot_rss.tsv | python src/read_rss.py
run1:
	cat config/sample_rss_feeds.tsv | python src/read_rss.py > run1.jsonl
run2:
	cat run1.jsonl | python src/read_article.py > run2.jsonl
run3:
	cat run2.jsonl | grep '"art"' > run3.jsonl
run4:
	cat run3.jsonl | python src/sentiment.py | grep CREATE > run4.cypher
testrun4:
	head run3.jsonl | python src/sentiment.py | grep CREATE > testrun4.cypher
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
