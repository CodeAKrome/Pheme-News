import sys
import nltk

# Download the punkt tokenizer if not already downloaded
nltk.download('punkt_tab', quiet=True)
#nltk.download('punkt_tab')

def count_tokens():
    # Read from standard input
    input_text = sys.stdin.read()
    
    # Tokenize the input text using nltk
    tokens = nltk.word_tokenize(input_text)
    
    # Count the number of tokens
    num_tokens = len(tokens)
    
    # Output the number of tokens
    print(num_tokens)

if __name__ == "__main__":
    count_tokens()
