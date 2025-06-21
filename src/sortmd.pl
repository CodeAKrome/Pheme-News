#!/usr/bin/perl
use strict;
use warnings;

# Read input from stdin
my @lines = <STDIN>;
my $content = join("", @lines);

# Split content into sections based on top-level headings
my @sections;
my $current_section = "";
my $in_section = 0;

foreach my $line (@lines) {
    if ($line =~ /^# /) {
        if ($in_section) {
            push @sections, $current_section;
            $current_section = "";
        }
        $in_section = 1;
        $current_section .= $line;
    } elsif ($in_section) {
        $current_section .= $line;
    }
}

# Add the last section if exists
if ($current_section ne "") {
    push @sections, $current_section;
}

# Sort sections based on the first line (heading)
@sections = sort {
    my ($a_head) = $a =~ /^# (.*?)$/m;
    my ($b_head) = $b =~ /^# (.*?)$/m;
    $a_head cmp $b_head;
} @sections;

# Print sorted sections
print join("", @sections);