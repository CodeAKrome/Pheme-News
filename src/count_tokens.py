#!/usr/bin/env python3
"""
Token counter for LLM tokenization methods.
Reads from stdin, counts tokens, writes count to stdout.
"""

import sys
import re
from typing import List

def simple_whitespace_tokenize(text: str) -> List[str]:
    """Simple whitespace-based tokenization."""
    return text.split()

def word_tokenize(text: str) -> List[str]:
    """Basic word tokenization with punctuation separation."""
    # Split on whitespace and punctuation, keep non-empty tokens
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return [token for token in tokens if token.strip()]

def subword_estimate(text: str) -> int:
    """
    Rough estimate of subword tokens (like BPE/SentencePiece).
    This approximates GPT-style tokenization without external libraries.
    Rule of thumb: ~0.75 tokens per word for English text.
    """
    words = simple_whitespace_tokenize(text)
    # Count characters to adjust for longer words
    char_count = len(text.replace(' ', ''))
    # Rough approximation: base word count + adjustment for subword splits
    estimated_tokens = len(words) + (char_count // 6)  # Extra tokens for longer words
    return estimated_tokens

def count_tokens(text: str, method: str = "subword") -> int:
    """Count tokens using specified method."""
    if method == "whitespace":
        return len(simple_whitespace_tokenize(text))
    elif method == "word":
        return len(word_tokenize(text))
    elif method == "subword":
        return subword_estimate(text)
    else:
        raise ValueError(f"Unknown tokenization method: {method}")

def main():
    # Read all input from stdin
    try:
        text = sys.stdin.read()
    except KeyboardInterrupt:
        sys.exit(1)
    
    # Default to subword estimation (most similar to modern LLMs)
    method = "subword"
    
    # Allow method override via command line argument
    if len(sys.argv) > 1:
        method = sys.argv[1].lower()
        if method not in ["whitespace", "word", "subword"]:
            print(f"Error: Unknown method '{method}'. Use: whitespace, word, or subword", 
                  file=sys.stderr)
            sys.exit(1)
    
    # Count tokens
    token_count = count_tokens(text, method)
    
    # Write count to stdout
    print(token_count)

if __name__ == "__main__":
    main()