#!/usr/bin/env perl

# --------------------------------------------------
# Model Name: models/gemini-1.5-flash-002
# Description: Stable version of Gemini 1.5 Flash, our fast and versatile multimodal model for scaling across diverse tasks, released in September of 2024.
# Supported Methods: generateContent, countTokens, createCachedContent
# --------------------------------------------------

while (<>) {

    if (/^Model Name: (.*)/) {
	$model = $1;
    }

    if (/Supported Methods:/) {

	if (/generateContent/) {

		# gemma doesn't work with this script
		if ($model =~ /gemma/) {
			next;
		}

	    $outfile = $model;
	    $outfile=~s/models\///;
	    print("cat prompt.txt | ./gemtest.py '$model' > 'output/${outfile}.txt'\n");
	}
	else {
	    
	}
       
	
    }

}
