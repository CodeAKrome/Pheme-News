import json
from flair_sentiment import FlairSentiment
import sys

# CREATE (JoelS:Person {name:'Joel Silver', born:1952})
# CREATE
# (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrix),
# (Carrie)-[:ACTED_IN {roles:['Trinity']}]->(TheMatrix),
# (Laurence)-[:ACTED_IN {roles:['Morpheus']}]->(TheMatrix),
def alphanumeric(s):
    return ''.join(c for c in s if c.isalnum())

def alphanumeric_lower(s):
    return ''.join(c for c in s if c.isalnum()).lower()

def esc_quotes(s):
    return s.replace('"', '\\"')

def main():
    source = []
    entity = []
    id = 0
    sentiment_analyzer = FlairSentiment()
    for line in sys.stdin:
        record = line.strip()
        if record:
            data = json.loads(record)    
            ner = sentiment_analyzer.process_text(data['text'])
            # see if source exists  
            if data['source'] not in source:
                srcname = alphanumeric(data['source'])
                source.append(srcname)
                print(f"CREATE ({srcname}:Source)")
            # article
            artid = f"Art{id}"
            print(f"CREATE ({artid}:Article {{title:\"{esc_quotes(data['title'])}\"}})")
            # link source and article
            print(f"CREATE ({srcname})-[:PUBLISHED {{date:{data['published_parsed']}}}]->({artid})")
            # see if entitys exist
            for sentence in ner:
#                print(f"\n\n{sentence['sentence']}")
                for span in sentence['spans']:
                    ent = esc_quotes(span['text'])
                    entname = alphanumeric(ent)
                    if entname not in entity:
                        entity.append(entname)
                        # create entity
                        print(f"CREATE ({entname}:{span['value']} {{val: \"{ent}\"}})")
                    # link article and entity
                    print(f"CREATE ({artid})-[:MENTIONS {{sentiment: '{span['sentiment']}', score: '{span['score']}', probability: '{span['probability']}'}}]->({entname})")
            id += 1

if __name__ == "__main__":
    main()