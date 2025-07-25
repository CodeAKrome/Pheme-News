titles:
	@src/titles.sh
#titles:
#	cat cache/dedupe.jsonl|jq -r '[.id, .title] | join("\t")' | sort -k 2 | uniq | awk '!seen[$2]++'
links:
	@cat cache/dedupe.jsonl|jq -r '[.id, .title, .link] | join("\t")'
jsonlinks:
	@cat cache/dedupe.jsonl|jq -r '[.id, .title, .link]'
entities:
	@jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' cache/dedupe.jsonl | sort | uniq | sort -t $'\t' -k 2 > cache/entities.tsv
filterentities:
	@grep -E '(PERSON|ORG|DATE|EVENT|LOC|FAC|GPE|NORP)' cache/entities.tsv > cache/entities_filter.tsv
bytypeentities:
	@sort -k 2 cache/entities_filter.tsv > cache/entities_filter_bytype.tsv
orentities:
	@cat cache/dedupe.jsonl | jq '.ner[] | select(.spans[]?.text as $text | $text == "Abdullah" or $text == "Africa")'
andentities:
	@jq '.ner[] | select(.spans as $spans | any($spans[]; .text == "Adesina") and any($spans[]; .text == "Africa"))' cache/dedupe.jsonl
# Experimental
tsv2html:
	cat tmp/0528links.tsv | python src/tsv_idtitlelink2html.py > tmp/0528links.html
html2pdf:
	chrome --headless --disable-gpu --print-to-pdf="tmp/0527idtitlelink.pdf" "file:///Users/kyle/hub/Pheme-News/tmp/0527idtitlelink.html"
ollamacheck:
	python src/lib/ollamaai.py 'llama3.1:8b' 3000 prompt="Capital of Spain"
gpechinavietnam:
	jq -n '[inputs | . as $root | .ner[].spans[] | select(.value? == "GPE" and (.text? | IN("China", "Vietnam") | . == true)) | {text: .text, value: .value, source: $root.source, id: $root.id}]' cache/dedupe.jsonl
workschinavietname:
	jq -n '[inputs | . as $root | .ner[].spans[] | select(type == "object" and (.text? | IN("China", "Vietnam") | . == true)) | {text: .text, value: .value, source: $root.source, id: $root.id}]' cache/dedupe.jsonl
filterobjecttype:
	 jq -n '[inputs | . as $root | .ner[].spans[] | select(type == "object") | {text: .text, value: .value, source: $root.source, id: $root.id}]' cache/dedupe.jsonl
checkspanstype:
	jq -n '[inputs | .ner[].spans[] | {type: type, value: .}]' cache/dedupe.jsonl
schinavietnam:
	jq -n '[inputs | .ner[].spans[] | select(.text | IN("China", "Vietnam"))]' cache/dedupe.jsonl
list:
	head -n 1 cache/dedupe.jsonl | jq .
gpe:
	jq -n '[inputs | .ner[].spans[] | select(.value == "GPE") | .text]' cache/dedupe.jsonl
#entities:
#	jq -n 'inputs | . as $root | [.ner[].spans[] | {text, value, source: $root.source, id: $root.id}]' cache/dedupe.jsonl
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
runsample:
	cat config/sample_rss_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
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
