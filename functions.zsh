# Show bias counts by source
strongbias() {
    jq -r 'select(.bias.degree == "strong") | {source: .source, bias: .bias.bias} |  join("\t")' $1 | sort | uniq -c
}

# print bias for comparison of LLMs
showbias() {
    cat $1 | egrep '^\{' | jq -r '[.source, .id, .bias.bias, .bias.degree, .title]|join("\t")'
}

checkbias() {
    cat $1 | egrep '^\{' | jq '[.id, .bias.bias, .bias.degree, .title, .text]'
}

# sorted count of $1 jq .sources
sources() {
    jq .source $1 | sort | uniq -c | sort -rn
}

# Slice by entity list
#Eric Trump	PERSON	3	27680
# entities to filter
# out article ids
ent2ids() {
    cut -f 4 $1 | perl -ne 's/\n//g;print;'
}

# generate cypher quesries
#cat cache/dedupe.jsonl | python src/sentiment.py > cache/dedupe_sentiment.cypher
cypher() {
    cat $1 | /Users/kyle/hub/Pheme-News/src/sentiment.py
}

# add decorations to initial sort
# cat tmp | sed 's/\*\*//g' | python ~/hub/Pheme-News/src/relink.py ~/hub/Pheme-News/tmp/iran_israel_idlinksrc.tsv | ~/hub/Pheme-News/src/gatherids.pl > ~/hub/Pheme-News/tmp/iran_israel.md

# slice out all we need from id list
# graphsumm.sh basename id,id,id
# sync this
slice() {
    jq -c "select(.id | IN($2))" dedupe.jsonl >../tmp/${1}.jsonl
    cat ../tmp/${1}.jsonl | jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' | sort | uniq | sort -t $'\t' -k 2 | grep -E '(PERSON|ORG|EVENT|LOC|FAC|GPE|NORP|DATE)' > ../tmp/${1}_ent.tsv
    cat ../tmp/${1}.jsonl | jq '[.text]' > ../tmp/${1}_text.jsonl
    cat ../tmp/${1}.jsonl | jq -r '[.title,.text]|join("\t")' > ../tmp/${1}_titletext.tsv
    cat ../tmp/${1}.jsonl | jq -r '[.id,.title,.summary]|join("\t")' > ../tmp/${1}_idtitlesumm.tsv
    cat ../prompt/summary.txt  ../tmp/${1}_ent.tsv > ../tmp/${1}_summary_prompt.txt
    cat ../prompt/graphene.txt  ../tmp/${1}_ent.tsv > ../tmp/${1}_cypher_prompt.txt
}

# Pull subset of articles by ids
# Usage: pullrecs in.jsonl "1,2,3"
pullrecs() {
    jq -c --argjson ids "[$2]" 'select(.id | IN($ids[]))' "$1"
}


# Get titles jsonl
gettitletexttab() {
    jq -r '[.title,.text]|join("\t")' $1
}

# Get titles jsonl
gettext() {
    jq '[.text]' $1
}

# make id title summary tsv file for sorting articles
idtitlesumm() {
    jq -r '[.id,.title,.summary]|join("\t")' $1
}

# make id title summary text tsv file for intense analysis
idtitlesummtext() {
    jq -r '[.id,.title,.summary,.text]|join("\t")' $1
}

# Filter entities for ones we want with or without DATEs
dateentfilter() {
    grep -E '(PERSON|ORG|DATE|EVENT|LOC|FAC|GPE|NORP)' $1
}
# no date
entfilter() {
    grep -E '(PERSON|ORG|EVENT|LOC|FAC|GPE|NORP)' $1
}

# Generate list of ids and titles sorted by title and deduped
gettitles() {
    cat $1 | jq -r '[.id, .title] | join("\t")' | sort -k 2 | uniq | awk '!seen[$2]++'
}

# Extract all the entities from a jsonl file and sort by type then filter by types we like
getentfilter() {
    jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' $1 | sort | uniq | sort -t $'\t' -k 2 | grep -E '(PERSON|ORG|EVENT|LOC|FAC|GPE|NORP)'
}

# Extract all the entities from a jsonl file and sort by type then filter by types we like
getentfilterdate() {
    jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' $1 | sort | uniq | sort -t $'\t' -k 2 | grep -E '(PERSON|ORG|EVENT|LOC|FAC|GPE|NORP|DATE)'
}

# Extract all the entities from a jsonl file and sort by type
getent() {
    jq -r '.ner[] | .spans[] | [.text, .value] | @tsv' $1 | sort | uniq | sort -t $'\t' -k 2
}

# Pull subset of articles by ids
# pullrecs in.jsonl 1,2,3
pullrecs_expand() {
    jq -c "select(.id | IN($2))" $1
}
