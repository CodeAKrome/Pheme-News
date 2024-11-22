cat x_${1}.json | jq .wikimap
fgrep "Total Run" y_${1}.txt
