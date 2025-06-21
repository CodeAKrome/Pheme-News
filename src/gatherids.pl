#!/usr/bin/perl

my @ids;

while (<>) {
#    if (/- (\d+) /) {
    if (/\*(\d+)\*/) {
        print;
        push @ids, $1;
    } else {
        if (@ids) {
            print "```\n".join(',', @ids) . "\n```\n";
            @ids = ();
        }
        print;
    }
}

print "@ids";
