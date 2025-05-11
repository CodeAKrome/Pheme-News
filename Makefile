include tools.mk
clean: clearcache
	rm cache/dedupe.jsonl
runpipe: tbeg pipe tend
pipe:	
	cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' > tmp/test.jsonl
pipe0:	
	cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' | python src/dedupe_init.py | python src/dedupe.py >> cache/dedupe.jsonl
allruns: tbeg run1 run2 run3 run4 run5 run6init run6 tend
tbeg:
	 echo "BEG" > cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
tend:
	 echo "END" >> cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
clearcache:
	rm cache/articles.json
	rm cache/counter.json
run1:
	cat config/political_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
run2:
	cat cache/read_rss.jsonl | python src/tallyman.py > cache/tallyman.jsonl
run3:
	cat cache/tallyman.jsonl | python src/read_article.py > cache/read_article.jsonl
run4:
	cat cache/read_article.jsonl | grep '"art"' > cache/art.jsonl
run5:
	cat cache/art.jsonl | python src/flair_news.py | egrep '^\{' > cache/flair_news.jsonl
run6init:
	cat cache/flair_news.jsonl | python src/dedupe_init.py
run6:
	cat cache/flair_news.jsonl | python src/dedupe.py >> cache/dedupe.jsonl
run7:
	cat cache/dedupe.jsonl| python src/vectorize.py
run8:
	cat cache/dedupe.jsonl | python src/cypher.py > cache/cypher.cypher
dev: install
	pip install -r requirements-dev.txt
install:
	pip install -r requirements.txt
