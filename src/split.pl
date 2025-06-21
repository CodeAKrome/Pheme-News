#!/usr/bin/perl

use strict;
use warnings;

# Check for correct number of command-line arguments
die "Usage: $0 basename extention count\n" unless @ARGV == 3;

my ($basename, $ext, $count) = @ARGV;

# Validate count is a positive integer
die "Count must be a positive integer\n" unless $count =~ /^\d+$/ && $count > 0;

my $file_number = 0;
my $line_count = 0;
my @buffer;
my $fh;

while (my $line = <STDIN>) {
    push @buffer, $line;
    $line_count++;

    if ($line_count == $count) {
        # Open new output file
        my $filename = sprintf("%s%d.%s", $basename, $file_number, $ext);
        open($fh, '>', $filename) or die "Cannot open $filename: $!\n";
        
        # Write buffered lines to file
        print $fh @buffer;
        
        # Close file and reset counters
        close $fh;
        @buffer = ();
        $line_count = 0;
        $file_number++;
    }
}

# Write any remaining lines to a final file
if (@buffer) {
    my $filename = sprintf("%s%d.%s", $basename, $file_number, $ext);
    open($fh, '>', $filename) or die "Cannot open $filename: $!\n";
    print $fh @buffer;
    close $fh;
}

exit 0;
