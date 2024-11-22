cat cache/11rec.jsonl | python src/nerd.py ${1} ${2} > results/x_${1}.json 2> results/y_${1}.txt
