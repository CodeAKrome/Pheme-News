import sys
from json import loads, dumps, JSONDecodeError

"""Do targetted sentiment detection on news articles. If no text field, passthrough."""

# This is the cutoff for ratio of love/hate as percent of total entities referenced in percent.
BIASTHRESHHOLD = 25

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

source = []
entity = []

# Bias entities for linking
for bias in ["positive", "negative", "neutral"]:
    print(f"CREATE ({bias}:Bias)")
   
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        data = loads(line)
    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue
    if not 'text' in data:
        print(line)
        continue

    ner = data['ner']

    # see if source exists
    srcname = first_letter(alphanumeric(data["source"]))
    if srcname not in source:
        source.append(srcname)
        print(f"CREATE ({srcname}:Source)")
    # Article
    artid = data{id}
    print(f"CREATE ({artid}:Article {{title:\"{esc_quotes(data['title'])}\", link:\"{data['link']}\"}})")
    # link source and article
    # deal with missing data
    pubdate = "\"N/A\""
    if "published_parsed" in data:
        pubdate = data['published_parsed']
    else:
        if "published" in data:
            pubdate = data['published']

    print(f'CREATE ({srcname})-[:PUBLISHED {{date: {pubdate}}}]->({artid})')
    # see if entitys exist
    stats = {
        "positive": 0,
        "negative": 0,
        "neutral": 0,
    }

    print(
        f"{artid}\t{data['source']}\t{data['title']}",
        file=sys.stderr,
    )

    for sentence in ner:
        # Get rid of duplicate lines by seeing if current sentence matches ones previously seen
        alpha_sent = alphanumeric(sentence["sentence"])

        for span in sentence["spans"]:
            ent = esc_quotes(span["text"])
            entname = first_letter(alphanumeric(ent))
            # if only non-alphanumerics, will be null. fix it
            if not entname:
                newent = f"{span['value']}{span['text']}"
                entname = first_letter(alphanumeric(newent))

            if entname not in entity:
                entity.append(entname)
                # create entity
                print(f"CREATE ({entname}:{span['value']} {{val: \"{ent}\"}})")
            # link article and entity
            stats[span["sentiment"]] += 1
            if span["sentiment"] == "neutral":
                rel = 'Refs'
            if span["sentiment"] == "positive":
                rel = 'Loves'
            if span["sentiment"] == "negative":
                rel = 'Hates'
            print(
                f"CREATE ({artid})-[:{rel} {{score: {span['score']}, prob: {span['probability']}, sent: '{sentence['sentence']}'}}]->({entname})"
            )

    posneg = stats["negative"] + stats["positive"]
    tot = posneg + stats["neutral"]
    bias_dir = "neutral"

    # div by zero hurts
    if tot:
        bias = posneg / tot * 100
        if bias > BIASTHRESHHOLD:
            if stats["positive"] - stats["negative"] > 0:
                bias_dir = "positive"
            if stats["negative"] - stats["positive"] > 0:
                bias_dir = "negative"
    print(
        f"CREATE ({artid})-[:IsBiased {{bias: {bias:.2f}, pos: {stats['positive']}, neg: {stats['negative']}, neut: {stats['neutral']}, tot: {tot}}}]->({bias_dir})"
    )                
    