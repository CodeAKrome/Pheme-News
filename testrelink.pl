#!/usr/bin/env perl

# cat src/output/gemini-2.5-flash-preview-04-17.txt | src/relink.py tmp/top10_idlinksrc.tsv > tmprelink.txt

while (<>) {
    chomp;
    $outfile = $_;
    $outfile=~s/\....$//;
    print("echo '$outfile'\n");
    print("cat '$_' | src/relink.py tmp/dedupe_idlinksrc.tsv '${outfile}_relink.md' > '${outfile}_relink.md' 2> '${outfile}_perc.txt'\n");
}
