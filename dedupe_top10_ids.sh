cut -f 4 tmp/dedupe_top10.tsv | perl -ne 's/\n/,/g;print;' > tmp/dedupe_top10_ids_comma.txt
cat tmp/dedupe_top10_ids_comma.txt | sed 's/\,$//' > tmp/dedupe_top10_ids.txt
