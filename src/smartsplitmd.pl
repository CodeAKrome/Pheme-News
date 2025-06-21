#!/usr/bin/perl

use strict;
use warnings;

# Check for correct number of command-line arguments
if (@ARGV != 2) {
    die "Usage: $0 <basename> <line_count>\n";
}

my ($basename, $line_count) = @ARGV;

# Validate line_count
if ($line_count !~ /^\d+$/ || $line_count <= 0) {
    die "Line count must be a positive integer\n";
}

my @buffer;               # Buffer for lines before writing to a file
my $current_file = 1;     # File sequence number
my $line_counter = 0;     # Count of lines in the current section
my $output_file;          # Current output file handle
my $in_section = 0;       # Flag to indicate if we're in a section (after a top-level heading)
my @section_lines;        # Temporary buffer for the current section

# Open the first output file
open_output_file();
$line_counter = 0;

# Read input from STDIN
while (my $line = <STDIN>) {
    chomp $line;

    # Check if the line is a top-level heading
    if ($line =~ /^# /) {
        # If we're already in a section and have enough lines, write the previous section and start a new file
        if ($line_counter >= $line_count) {
            # Write the current section to the file
            print $output_file "$_\n" for @buffer;
            close $output_file if $output_file;

            # Open a new file
            open_output_file();

            # Clear section lines and reset counter
            @buffer = ();
            $line_counter = 0;
        }

    }

    # Store line in buffer
    push @buffer, $line;
    $line_counter++;

}

# Write any remaining section lines to the last file
if (@buffer) {
    print $output_file "$_\n" for @buffer;
}

# Close the last file
close $output_file if $output_file;

sub open_output_file {
    my $filename = "${basename}${current_file}.md";
    open($output_file, '>', $filename) or die "Cannot open $filename for writing: $!\n";
    print "Created file: $filename\n";
    $current_file++;
}