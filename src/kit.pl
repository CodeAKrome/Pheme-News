#!/usr/bin/perl
use strict;
use warnings;

while (my $filename = <STDIN>) {
    chomp $filename;
    next unless -f $filename;  # Skip if not a regular file
    
    my $comment_count = 0;
    my @lines;
    
    if (open my $fh, '<', $filename) {
        while (my $line = <$fh>) {
            push @lines, $line;
            $comment_count++ if $line =~ /^#/;
        }
        close $fh;
        
        print "=== $filename (# lines: $comment_count) ===\n";
        print @lines;
    } else {
        print "=== $filename ===\n";
        print "Error: Cannot open $filename: $!\n";
    }
    
    print "\n" . "=" x 60 . "\n\n";
}
