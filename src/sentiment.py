from json import loads, JSONDecodeError
from lib.flair_sentiment import FlairSentiment
import sys
import re

# CREATE (JoelS:Person {name:'Joel Silver', born:1952})
# CREATE
# (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrix),
# (Carrie)-[:ACTED_IN {roles:['Trinity']}]->(TheMatrix),
# (Laurence)-[:ACTED_IN {roles:['Morpheus']}]->(TheMatrix),
PATTERN = re.compile(r"[^a-zA-Z0-9]")


def alphanumeric0(s):
    return "".join(c for c in s if c.isalnum())


def alphanumeric(text):
    return PATTERN.sub("", text)


def alphanumeric_lower(s):
    return "".join(c for c in s if c.isalnum()).lower()


def esc_quotes(s):
    return s.replace('"', '\\"')


def first_letter(text):
    """Make sure a letter is at beginning otherwise node name is illegal for neo4j"""
    if text and text[0].isalpha():
        return text
    else:
        for i, char in enumerate(text):
            if char.isalpha():
                return text[i:]
    return ""  # Return empty string if no letters are found


def main():
    source = []
    entity = []
    id = 0
    sentiment_analyzer = FlairSentiment()
    # Bias entities for linking
    for bias in ["positive", "negative", "neutral"]:
        print(f"CREATE ({bias}:Bias)")

    dedupe = {}
    dedupe_init = True

    for line in sys.stdin:
        record = line.strip()
        if record:
            try:
                data = loads(record)
            except JSONDecodeError as e:
                sys.stderr.write(f"Error parsing JSON: {e}\n")
            ner = sentiment_analyzer.process_text(data["text"])
            # see if source exists
            srcname = first_letter(alphanumeric(data["source"]))
            if srcname not in source:
                source.append(srcname)
                print(f"CREATE ({srcname}:Source)")
            # article
            artid = f"Art{id}"
            print(f"CREATE ({artid}:Article {{title:\"{esc_quotes(data['title'])}\"}})")
            # link source and article
            # deal with missing data
            if "published_parsed" in data:
                print(
                    f"CREATE ({srcname})-[:PUBLISHED {{date:{data['published_parsed']}}}]->({artid})"
                )
            else:
                if "published" in data:
                    print(
                        f"CREATE ({srcname})-[:PUBLISHED {{date:\"{data['published']}\"}}]->({artid})"
                    )
                else:
                    print(f'CREATE ({srcname})-[:PUBLISHED {{date:"NA"}}]->({artid})')
            # see if entitys exist
            stats = {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
            }

            dupe_count = 0
            for sentence in ner:
                # Get rid of duplicate lines by seeing if current sentence matches ones previously seen
                alpha_sent = alphanumeric(sentence["sentence"])
                if dedupe_init:
                    dedupe[alpha_sent] = True
                else:
                    if alpha_sent in dedupe:
                        dupe_count += 1
                        print(f"DROP\t{sentence["sentence"]}", file=sys.stderr)
                        continue
                    
                print(
                    f"{id}\t{sentence['tag']}\t{sentence['score']}\t{sentence['sentence']}",
                    file=sys.stderr,
                )

                # stats[sentence["tag"]] += 1

                for span in sentence["spans"]:
                    ent = esc_quotes(span["text"])
                    entname = first_letter(alphanumeric(ent))
                    if not entname:
                        newent = f"{span['value']}{span['text']}"
                        entname = first_letter(alphanumeric(newent))
                        print(
                            f"WARN: [{newent}] -> [{entname}]: {span['value']} {span['text']}",
                            file=sys.stderr,
                        )

                    if entname not in entity:
                        entity.append(entname)
                        # create entity
                        print(f"CREATE ({entname}:{span['value']} {{val: \"{ent}\"}})")
                    # link article and entity
                    stats[span["sentiment"]] += 1
                    if span["sentiment"] == "neutral":
                        print(
                            f"CREATE ({artid})-[:REFS {{score: '{span['score']}', prob: '{span['probability']}'}}]->({entname})"
                        )
                    if span["sentiment"] == "positive":
                        print(
                            f"CREATE ({artid})-[:LOVES {{score: '{span['score']}', prob: '{span['probability']}'}}]->({entname})"
                        )
                    if span["sentiment"] == "negative":
                        print(
                            f"CREATE ({artid})-[:HATES {{score: '{span['score']}', prob: '{span['probability']}'}}]->({entname})"
                        )
            # Finished with sentences
            # dedupe should be full now.
            if dedupe_init:
                dedupe_init = False
            else:
            # If we haven't seen any dupes and we didn't just fill it, refill dedupe
                if dupe_count == 0:
                    dedupe_init = True
                    dedupe = {}
                             
            posneg = stats["negative"] + stats["positive"]
            tot = posneg + stats["neutral"]
            bias_dir = "neutral"

            if tot:
                bias = posneg / tot * 100
                if bias > 25:
                    if stats["positive"] - stats["negative"] > 0:
                        bias_dir = "positive"
                    if stats["negative"] - stats["positive"] > 0:
                        bias_dir = "negative"
            print(
                f"CREATE ({artid})-[:BIAS {{bias: {bias:.2f}, pos: {stats['positive']}, neg: {stats['negative']}, neut: {stats['neutral']}, tot: {tot}}}]->({bias_dir})"
            )                
            #            print(f"{dir(stats)}", file=sys.stderr)
            id += 1


if __name__ == "__main__":
    main()
