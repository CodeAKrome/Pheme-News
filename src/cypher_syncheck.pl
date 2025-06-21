#!/usr/bin/perl
use strict;
use warnings;

# check cypher statements for syntax errors

while (<>) {
    
    if (/^CREATE \([A-Za-z0-9_]+:[A-Z0-9_]+ \{val: "[^"]+"\}\)\s*$/) {
        next;  # Skip lines that match the pattern  
    }
    else {

#        if (/^CREATE \(\w+\)-\[:[A-Z]+ \{[^}]+\}\]->\(\w+\)$/) {
        if (/^CREATE \([A-Za-z0-9_]+\)-\[:[A-Z0-9_]+\]->\(\w+\)\s*$/) {
            next;
        }
        else {
            print;
        }

    }

}
