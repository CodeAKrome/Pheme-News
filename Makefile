include tools.mk
tidy:
	black src/*.py
clean: clearcache
runpipe: tbeg pipe tend
pipe:	
	@cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' > tmp/test.jsonl
pipe0:	
	@cat config/political_feeds.tsv | python src/read_rss.py | python src/tallyman.py | python src/read_article.py | grep '"art"' | python src/flair_news.py | egrep '^\{' | python src/dedupe_init.py | python src/dedupe.py >> cache/dedupe.jsonl
allruns: tbeg run1 run2 run3 run4 run5 run6init run6 bias recent entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llm tend

partruns: entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llm tend
#partruns: tbeg run1 run2 run3 run4 run5 run6init run6 bias recent entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice ollamatest tend

testruns: tbeg run1 run2 run3 run4 run5 run6init run6 bias recent entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llmtest tend
testpartruns: run5 run6init run6 bias recent entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llmtest tend
# just run the test_feeds without stripping sparse with llmtest
testfeed: tbeg testrun1 run2 run3 run4 run5 run6init run6 bias entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llmtest tend
testpartfeed: run5 run6init run6 bias entitydict idtitlepubsumm idlinksrcbvalbiasbbiasdeg top10 top10slice llmtest tend
tbeg:
	@echo "BEG" > cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
tend:
	@echo "END" >> cache/runtime.txt ; date +"%m-%d %H:%M:%S" >> cache/runtime.txt
clearcache:
	rm cache/articles.json
	rm cache/counter.json
run1:
	@cat config/political_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
testrun1:
	@cat config/test_feeds.tsv | python src/read_rss.py > cache/read_rss.jsonl
run2:
	@cat cache/read_rss.jsonl | python src/dedupe_titles.py | python src/tallyman.py > cache/tallyman.jsonl
run3:
	@cat cache/tallyman.jsonl | python src/read_article.py > cache/read_article.jsonl
run4:
	@cat cache/read_article.jsonl | grep '"art"' | src/kill_shorty.py config/kill.txt > cache/art.jsonl
run5:
	@cat cache/art.jsonl | python src/flair_news.py | egrep '^\{' > cache/flair_news.jsonl
run6init:
	@cat cache/flair_news.jsonl | python src/dedupe_init.py
run6:
	@cat cache/flair_news.jsonl | python src/dedupe.py > cache/dedupe_deduped.jsonl 
# Restrict stories to those in last 2 days
recent:
	@cat `find cache -type f -name 'dedupe_*.jsonl' -newermt '2 day ago'` | egrep '^\{' | src/date_filter.py '-2 day' > cache/dedupe.jsonl
bias:
	@cat cache/dedupe_deduped.jsonl | src/litellm_ai.py prompt/lcr_reason_exam4k.txt > cache/dedupe_bias.jsonl
	@cp cache/dedupe_bias.jsonl cache/dedupe_`date +%m-%d_%H:%M`.jsonl
vectorize:
	@cat cache/dedupe.jsonl| python src/vectorize.py
sentiment:
	@cat cache/dedupe.jsonl | python src/sentiment.py > cache/dedupe_sentiment.cypherl
entitydict:
	@cat cache/dedupe.jsonl | python src/jsonl2entitydict.py > cache/dedupe_entity_dictionary.tsv
idtitlesumm:
	@jq -r '[.id,.title,.summary]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idtitlesumm.tsv
idtitlepubsumm:	
	@jq -r '[.id,.title,.published,.summary]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idtitlepubsumm.tsv
idlinksrcbvalbias:
	@jq -r '[.id,.link,.source,.stats.bias_value,.stats.bias]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idlinksrcbvalbias.tsv
idlinksrcbvalbiasbbiasdeg:
	@jq -r '[.id,.link,.source,.stats.bias_value,.stats.bias,.bias.bias,.bias.degree]|join("\t")' cache/dedupe.jsonl > tmp/dedupe_idlinksrcbvalbiasbbiasdeg.tsv
# output broken fix
top10entity:
	@cat cache/dedupe_entity_dictionary.tsv | grep -E '(PERSON|ORG|EVENT|FAC|GPE|NORP)' | head -n 10 > tmp/dedupe_entity_top10.tsv
allentity:
	@cat cache/dedupe_entity_dictionary.tsv | grep -E '(PERSON|ORG|EVENT|FAC|GPE|NORP)' | cut -f 1,2 > cache/dedupe_allentity.tsv
allslice:
	@cat cache/dedupe.jsonl | egrep '^\{' | jq -r '[.id,.title]|join("\t")' > tmp/dedupe_idtitle.tsv
	@cat prompt/gemtest.txt cache/dedupe_allentity.tsv prompt/attachment.txt tmp/dedupe_idtitle.tsv > tmp/dedupe_all_initial_prompt.txt
	@cp tmp/dedupe_all_initial_prompt.txt tmp/prompt.txt
top10:
	@cat cache/dedupe_entity_dictionary.tsv | grep -E '(PERSON|ORG|EVENT|FAC|GPE|NORP)' | head -n 10 > tmp/dedupe_top10.tsv
top10slice:
	@./dedupe_top10_ids.sh
#	@cut -f 4 tmp/dedupe_top10.tsv | perl -ne 's/\n/,/g;print;' > tmp/dedupe_top10_ids_comma.txt
#	@cat tmp/dedupe_top10_ids_comma.txt | sed 's/\,$//' > tmp/dedupe_top10_ids.txt
	@cd cache; ./slice.sh top10 `cat ../tmp/dedupe_top10_ids.txt`
	@cut -f 1,2 tmp/dedupe_top10.tsv > tmp/top10_filtent.tsv
	@cat prompt/gemtest.txt tmp/top10_filtent.tsv prompt/attachment.txt tmp/top10_idtitle.tsv > tmp/top10_initial_prompt.txt
	@cp tmp/top10_initial_prompt.txt tmp/prompt.txt
allllm:
	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-pro' > tmp/dedupe_all_llm.md
	@cat tmp/dedupe_all_llm.md | src/filter_markdown.py > tmp/dedupe_all_filt.md
	@cat tmp/dedupe_all_filt.md | src/relink.py tmp/dedupe_idlinksrcbvalbiasbbiasdeg.tsv all | src/filter_markdown.py > tmp/dedupe_all_lnk.md
	@cat tmp/dedupe_all_lnk.md | src/gatherids.pl > tmp/dedupe_all.md
#	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' | src/filter_markdown.py | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/gatherids.pl > tmp/top10.md
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/dedupe_all.md | src/summ_ids.py 'models/gemini-2.5-flash' cache/dedupe.jsonl prompt/summary.txt all > mp3/all.md 2> mp3/Sound_all.jsonl
#	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
llm:
	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-pro' > tmp/top10_llm.md
	@cat tmp/top10_llm.md | src/filter_markdown.py > tmp/top10_filt.md
	@cat tmp/top10_filt.md | src/relink.py tmp/dedupe_idlinksrcbvalbiasbbiasdeg.tsv top10 | src/filter_markdown.py > tmp/top10_lnk.md
	@cat tmp/top10_lnk.md | src/gatherids.pl > tmp/top10.md
#	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' | src/filter_markdown.py | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/gatherids.pl > tmp/top10.md
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10 > mp3/Top10.md 2> mp3/Sound.jsonl
	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
# don't filter the markdown for sparse topics with < 3 articles
testllm:
	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' > tmp/top10_filt.md
#	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' > tmp/top10_llm.md
#	@cat tmp/top10_llm.md | src/filter_markdown.py > tmp/top10_filt.md
#	@cat tmp/top10_filt.md | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/filter_markdown.py > tmp/top10_lnk.md
	@cat tmp/top10_filt.md | src/relink.py tmp/dedupe_idlinksrcbvalbiasbbiasdeg.tsv top10 > tmp/top10_lnk.md
	@cat tmp/top10_lnk.md | src/gatherids.pl > tmp/top10.md
#	@cat tmp/prompt.txt | src/gemtest.py 'models/gemini-2.5-flash' | src/filter_markdown.py | src/relink.py tmp/dedupe_idlinksrcbvalbias.tsv top10 | src/gatherids.pl > tmp/top10.md
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10 > mp3/Top10.md 2> mp3/Sound.jsonl
	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
mp3:
	@rm mp3/*.mp3; rm mp3/*.txt; rm mp3/*.jsonl; rm mp3/*.md
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10 > mp3/Top10.md 2> mp3/Sound.jsonl
	@cd mp3; cat Sound.jsonl | ../src/jsonl2mp3.py
ollamatest:
	@cat prompt/gemtest.txt tmp/top10_filtent.tsv prompt/attachment.txt tmp/top10_idtitle.tsv > tmp/top10_initial_prompt.txt
	@cp tmp/top10_initial_prompt.txt tmp/prompt.txt
	ollama list | cut -f 1 -d ' ' | grep -v NAME | perl -ne 'chomp; print("cat tmp/prompt.txt | src/litellm_std.py \"ollama/$_\" > src/output/$_.txt\n");' > tmp/ollamatest.sh
	source tmp/ollamatest.sh
# This should run src/filter_markdown.py
# Doesn't run summary and move to mp3 dir
# maxgood copies right md file to top10.md
llmtest:
	@rm -f src/output/*
	@src/geminiai_listmodels.py | src/geminimodelfilter.pl > src/gemtest_runall.sh
	@cd src; ./gemtest_runall.sh
	@find src/output -type f -size +0c -print | ./testrelink.pl > testrelink.sh
	@./testrelink.sh
	@ls -1 src/output/*perc* | src/maxgood.py > tmp/maxgood_llm.txt
summarize:
	@cat tmp/top10.md | src/summ_ids.py 'gemini-2.5-flash' cache/dedupe.jsonl prompt/summary.txt top10`date '+%m%d'` > tmp/Top10`date '+%m%d'`.md 2> tmp/Sound`date '+%m%d'`.json
testsummarize:
	@cat tmp/top10.md | src/summ_ids.py `cat tmp/maxgood_llm.txt` cache/dedupe.jsonl prompt/summary.txt top10.md > tmp/Top10.md 2> tmp/Sound.jsonl
dev: install
	@pip install -r requirements-dev.txt
install:
	@pip install -r requirements.txt
cleanmp3:
	@rm mp3/*.mp3
	@rm mp3/*.txt
	@rm mp3/*.jsonl
