include tools.mk
clean: clearcache
	rm/counter.json
runpipe: tbeg pipe tend
pipe:	
	@cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' > tmp/test.jsonl
pipe0:	
	@cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' | python src/dedupe_init.py | python src/dedupe.py >> cache/dedupe.jsonl
allruns: tbeg run1 run2 run3 run4 run5 run6init run6 dedupe entitydict idtitlepubsumm idlinksrcbvalbias top10 top10slice llm tend
testruns: tbeg run1 run2 run3 run4 run5 run6init run6 dedupe entitydict idtitlepubsumm idlinksrcbvalbias top10 top10slice llmtest tend
partruns: run6init run6 dedupe entitydict idtitlepubsumm idlinksrcbvalbias top10 top10slice llm tend
tbeg:
	@echo "BEG" > cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
tend:
	@echo "END" >> cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
clearcache:
	rm cache/articles.json
	rm cache/counter.json
run1:
	@cat config/political_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
run2:
	@cat cache/read_rss.jsonl | python src/dedupe_titles.py | python src/tallyman.py > cache/tallyman.jsonl
run3:
	@cat cache/tallyman.jsonl | python src/read_article.py > cache/read_article.jsonl
run4:
	@cat cache/read_article.jsonl | grep '"art"' > cache/art.jsonl
run5:
	@cat cache/art.jsonl | python src/flair_news.py | egrep '^\{' > cache/flair_news.jsonl
run6init:
	@cat cache/flair_news.jsonl | python src/dedupe_init.py
run6:
	@cat cache/flair_news.jsonl | python src/dedupe.py > cache/dedupe_`date +%m-%d_%H:%M`.jsonl
vectorize:
	@cat cache/dedupe.jsonl| python src/vectorize.py
sentiment:
	@cat cache/dedupe.jsonl | python src/sentiment.py > cache/dedupe_sentiment.cypher
# Restrict stories to those in last day
dedupe:
	@cat `find cache -type f -name 'dedupe_*.jsonl' -newermt '1 day ago'` | src/date_filter.py '-1 day' > cache/dedupe.jsonl
entitydict:
	@cat cache/dedupe.jsonl | python src/jsonl2entitydict.py > cache/dedupe_entity_dictionary.tsv
idtitlesumm:
	@jq -r '[.id,.title,.summary]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idtitlesumm.tsv
idtitlepubsumm:	
	@jq -r '[.id,.title,.published,.summary]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idtitlepubsumm.tsv
idlinksrcbvalbias:
	@jq -r '[.id,.link,.source,.stats.bias_value,.stats.bias]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idlinksrcbvalbias.tsv
top10:
	@cat cache/dedupe_entity_dictionary.tsv | grep -E '(PERSON|ORG|EVENT|FAC|GPE|NORP)' | head -n 10 > tmp/dedupe_top10.tsv
top10slice:
	@cut -f 4 tmp/dedupe_top10.tsv | perl -ne 's/\n//g;print;' > tmp/dedupe_top10_ids.txt
	@cd cache; ./slice.sh top10 `cat ../tmp/dedupe_top10_ids.txt`
	@cut -f 1,2 tmp/dedupe_top10.tsv > tmp/top10_filtent.tsv
	@cat prompt/gemtest.txt tmp/top10_filtent.tsv prompt/attachment.txt tmp/top10_idtitle.tsv > tmp/top10_initial_prompt.txt
	@cp tmp/top10_initial_prompt.txt src/prompt.txt
llm:
	@cat src/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' > tmp/top10_llm.md
	@cat tmp/top10_llm.md | src/filter_markdown.py > tmp/top10_filt.md
	@cat tmp/top10_filt.md | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/filter_markdown.py > tmp/top10_lnk.md
	@cat tmp/top10_lnk.md | src/gatherids.pl > tmp/top10.md
#	@cat src/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' | src/filter_markdown.py | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/gatherids.pl > tmp/top10.md
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10 > mp3/Top10.md 2> mp3/Sound.jsonl
	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
mp3:
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10 > mp3/Top10.md 2> mp3/Sound.jsonl
	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
llmtest:
	@rm -f src/output/*
	@src/geminiai_listmodels.py | src/geminimodelfilter.pl > src/gemtest_runall.sh
	@cd src; ./gemtest_runall.sh
	@find src/output -type f -size +0c -print | ./testrelink.pl > testrelink.sh
	@./testrelink.sh
	@ls -1 src/output/*perc* | src/maxgood.py > tmp/maxgood_llm.txt
# maxgood copies right md file to top10.md
postslicellm:
#	@cat tmp/top10_initial_prompt.txt | src/gemtest.py `cat tmp/maxgood_llm.txt` > tmp/top10.md
#	@cat tmp/top10_initial_prompt.txt | src/gemtest.py > tmp/top10_aiout.md
#	@cat tmp/top10_aiout.md | src/relink.py tmp/dedupe_idlinksrc.tsv top10 | src/gatherids.pl > tmp/top10.md
#	@cp tmp/top10_initial_prompt.txt src/prompt.txt
summarize:
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10`date '+%m%d'` > tmp/Top10`date '+%m%d'`.md 2> tmp/Sound`date '+%m%d'`.jsonl
dev: install
	@pip install -r requirements-dev.txt
install:
	@pip install -r requirements.txt
cleanmp3:
	@rm mp3/*.mp3
	@rm mp3/*.txt
	@rm mp3/*.jsonl
