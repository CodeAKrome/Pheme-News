#!/usr/bin/env perl

%nodes = {};

while (<>) {
#    print("in $_");
    
    if (/\-\>\([`'"](.*?)[`'"]\)/) {
#	print("-> -$1-\n");
	
	if (! $nodes{$1}) {
	    print("CREATE (`$1`:GHOST {val: \"$1\"})\n");
	}

	print;
	$nodes{$1}++;
    }
    else {

	if (/^CREATE \([`'"](.*?)[`'"]/) {
#	    print("Cr -$1-\n");
	    $nodes{$1}++;
	}
	print;
	
    }

}
