from json import loads, dumps, JSONDecodeError
import sys
import re
from lib.flair_sentiment import FlairSentiment

fs = FlairSentiment()

def readstd(callback):
    data = ''
    for line in sys.stdin:
        data += line.strip()

    callback(data)

def convert(data):
    """
    This is wrong, should be done using spans!
    """

    ner = fs.process_text(data)
    
    markup = ''
    for rec in ner:
        sent = rec['sentence']
        reps = {}

        for span in rec['spans']:
            txt = span['text']
            cat = span['value']

            key = cat + txt
            if key in reps:
                continue
            reps[key] = True
            
#            pat = r'\b' + re.escape(txt) + r'\b'
            pat = re.escape(txt)
            rep = f"<{cat}>{txt}</{cat}>"
            sent = re.sub(pat, rep, sent)
        markup += sent
#        print(f">>{sent}\n")

    print(markup)

if __name__ == '__main__':
    readstd(convert)
    
