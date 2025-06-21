#!/usr/bin/env perl
use strict;
use warnings;

# Remove empty markdown level 1 and 2 headings stdin stdout

my @lines = <STDIN>;
my @output;
my $i = 0;

while ($i < @lines) {
    my $line = $lines[$i];
    
    # Check if this is a level 1 or level 2 heading
    if ($line =~ /^(##?) /) {
        my $heading_level = $1;
        
        # Look ahead to see if there's any content before the next heading of same or higher level
        my $j = $i + 1;
        my $has_content = 0;
        
        while ($j < @lines) {
            my $next_line = $lines[$j];
            
            # Define what constitutes a "same or higher level" heading
            my $stop_pattern;
            if ($heading_level eq '#') {
                # For level 1, stop at any other level 1 heading
                $stop_pattern = qr/^# /;
            } else {
                # For level 2, stop at level 1 or level 2 headings
                $stop_pattern = qr/^##? /;
            }
            
            # If we hit a heading of same or higher level, stop looking
            if ($next_line =~ /$stop_pattern/) {
                last;
            }
            
            # If we find any non-empty line that's not just whitespace, we have content
            if ($next_line =~ /\S/) {
                $has_content = 1;
                last;
            }
            
            $j++;
        }
        
        # Only include this heading if it has content
        if ($has_content) {
            push @output, $line;
        }
        else {
            print STDERR "MT: $line";
        }
    } else {
        # For non-heading lines, always include them
        push @output, $line;
    }
    
    $i++;
}

print @output;
