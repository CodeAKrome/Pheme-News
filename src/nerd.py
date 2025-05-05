import wikipedia as wiki
import sys
import ollama
from wikipedia.exceptions import DisambiguationError, PageError
from json import loads, dumps, JSONDecodeError
import os
from litellm import completion
from time import perf_counter
import re

# from groq import Groq
from functools import cache
from time import sleep
from lib.ollamaai import OllamaAI
from lib.groqaai import GroqAI
from lib.geminiai import GeminiAI

"""model name, [groq ollama] default ollama"""

# https://github.com/CodeAKrome/ollama-chat/blob/main/ollama_chat.py#L1431

MODEL = "llama3.1:70b"


@cache
def wiki_cache(suspect):
    try:
        return wiki.search(suspect)
    except Exception as e:
        # Wiki too busy
        sleep(10)


@cache
def wiki_summary_cache(person):
    return wiki.summary(person)


@cache
def summ_people(suspect):
    """Return summaries from wiki search for suspect."""
    dex = {}

    for person in wiki_cache(suspect):
        if True:
            # if wikipeeps(person):
            try:
                dex[person] = wiki_summary_cache(person)
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")
        else:
            sys.stderr.write(f"Not person: {person}\n")
    return dex


@cache
def nerd(tag, suspect, sentence):
    system_base = f"You are a world famous detective like Sherlock Holmes. You always answer accurately.\n"
    system_base += """Tag	Meaning	Example
EVENT	event name	Super Bowl, Olympics
FAC	building name	Empire State Building, Eiffel Tower
GPE	geo-political entity	United States, France
LANGUAGE	language name	English, Spanish
LAW	law name	Constitution, Copyright Act
LOC	location name	New York City, Paris
NORP	affiliation	Republican, Democrat
ORG	organization name	NASA, Google
PERSON	person name	John Doe, Jane Smith
PRODUCT	product name	iPhone, MacBook
WORK_OF_ART	name of work of art	Mona Lisa, Star Wars
"""
    if tag == "PERSON":
        system_base += f"You will correctly identify this <{tag}>person</{tag}>. You will not mistake them for any other person or member of their family like a son, daughter or wife.\n"
        system_base += "Professions, sexes and nationalities must match for correct identification.\n"
    if tag == "EVENT":
        system_base += f"You will correcty identify this <{tag}>event</{tag}>. You will match location time, and other details. You will not confuse it with any other event.\n"
    if tag == "FAC":
        system_base += f"You will correctly identify this <{tag}>facility or building</{tag}>. You will match the location and name. You will not confuse it with any other building or facility.\n"
    if tag == "GPE":
        system_base += f"You will correctly identify this <{tag}>geo-political entity</{tag}>, such as a political party or country.\n"
    if tag == "LANGUAGE":
        system_base += f"You will correctly identify this <{tag}>language</{tag}>. You will not mistake it for any other.\n"
    if tag == "LAW":
        system_base += f"You will correctly identify this <{tag}>law</{tag}>. You will match and legal references and statutes. You will not mistake it for any other.\n"
    if tag == "LOC":
        system_base += f"You will correctly identify this <{tag}>location</{tag}>. You will pay attention to country, state, city and other geographic details.\nYou will not mistake it for any other.\n"
    if tag == "NORP":
        system_base += f"You will correctly identify this <{tag}>affiliation</{tag}>. You will not mistake it for any other.\n"
    if tag == "ORG":
        system_base += f"You will correctly identify this <{tag}>organization</{tag}>. You will match name and type. You will not mistake it for any other.\n"
    if tag == "PRODUCT":
        system_base += f"You will correctly identify this <{tag}>product</{tag}>. You will identify it by brand and name. You will not mistake it for any other.\n"
    if tag == "WORK_OF_ART":
        system_base += f"You will correctly identify this <{tag}>work of art</{tag}>. You will match painter and subject. You will not mistake it for any other.\n"

    system = f"{system_base}Only reply with 'yes' or 'no' to the following question:\n"

    assistant.set_system(system)
    usual_suspects = summ_people(suspect)

    for person, summ in usual_suspects.items():
        prompt = f"Is <{tag}>{suspect}</{tag}> in the following example:\n<example>{sentence}</example>\nthe same as <{tag}>{person}</{tag}> in the following summary:\n<summary>{summ}</summary>\nAnswer 'yes' or 'no'.\n"
        raw = assistant.says(prompt)

        sys.stderr.write(f"RAW: {raw}\n")

        ans = "no"
        if "yes" in raw.lower():
            ans = "yes"

        # sys.stderr.write(f"\033[41m\033[91m {suspect} -> {person}\t{ans} \033[0m\n")
        sys.stderr.write(f"{suspect} -> {person}\t{ans}\n")

        if "yes" in ans:
            sys.stderr.write(
                f"\n\n\033[41m\033[91m Match found: {suspect} -> {person}\033[0m\nsummary: {summ}\n\n"
            )
            return person

    return None


def readstd(callback):
    recno = 1
    for line in sys.stdin:
        sys.stderr.write(f"\n\n=== RECNO: {recno} ===\n\n")
        recno += 1

        line = line.strip()
        if not line:
            continue
        try:
            data = loads(line)
        except JSONDecodeError as e:
            sys.stderr.write(f"JSON: {e}\n{line}\n")
            continue
        # This should mean this is an rss flavored record
        if not "ner" in data:
            print(line)
            continue
        callback(data)


def procart(data):
    noproc = ["MONEY", "ORDINAL", "PERCENT", "QUANTITY", "TIME", "DATE", "CARDINAL"]
    ner = data["ner"]
    art_map = {}

    # Pass 1
    examples = {}
    for ent in ner:
        for span in ent["spans"]:
            # ORG/name or PERSON/name etc.
            suspect = f"{span['value']}/{span['text']}"
            sentence = ent["sentence"]
            if suspect in examples:
                examples[suspect] += sentence
            else:
                examples[suspect] = sentence

    wikimap = []
    # PASS 2
    for ent in ner:
        start_time = perf_counter()

        sys.stderr.write(f"\n=>\t{ent['sentence']}\n")

        # NER to the D in single sentence
        for span in ent["spans"]:
            # ORG/name or PERSON/name etc.
            tag = span["value"]
            if tag in noproc:
                continue
            suspect_key = f"{tag}/{span['text']}"
            suspect = span["text"]
            sentence = ent["sentence"]
            res = None

            sys.stderr.write(f"\nTRY: {suspect}\n")

            for aka, entity in art_map.items():
                if suspect in aka:
                    res = art_map[aka]
                else:
                    if suspect in entity:
                        res = art_map[entity]
                if res:
                    art_map[suspect_key] = entity

                    sys.stderr.write(
                        f"\n\033[41m\033[91m NERD {suspect} -> {res} added {suspect_key} -> {entity} \033[0m\n"
                    )

                    break
            if not res:
                if suspect and suspect_key in examples:
                    res = nerd(tag, suspect, examples[suspect_key])

            if not res:
                continue
            # resets every article
            art_map[suspect_key] = res
            art_map[res] = res

        wikimap.append(art_map)
    lap = perf_counter() - start_time

    sys.stderr.write(f"\nTime: {lap:.2f}s\n")

    data["wikimap"] = wikimap
    print(dumps(data))


def main(assistant, nerd_map):
    recno = 1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = loads(line)
        except JSONDecodeError as e:
            sys.stderr.write(f"JSON: {e}\n{line}\n")
            continue
        # This should mean this is an rss flavored record
        if not "ner" in data:
            print(line)
            continue

        sys.stderr.write(f"\n\n=== RECNO: {recno} ===\n\n")

        recno += 1

        # Have data
        ner = data["ner"]
        wikimap = []
        art_map = {}

        # PASS 1
        # Collect example sentences for PERSONs.
        examples = {}
        for ent in ner:
            for span in ent["spans"]:
                if span["value"] == "PERSON":
                    suspect = span["text"]
                    sentence = ent["sentence"]
                    if suspect in examples:
                        examples[suspect] += sentence
                    else:
                        examples[suspect] = sentence

        # PASS 2
        for ent in ner:
            start_time = perf_counter()
            sys.stderr.write(f"\n=>\t{ent['sentence']}\n")

            # NER to the D in single sentence
            for span in ent["spans"]:
                if span["value"] == "PERSON":
                    suspect = span["text"]
                    sentence = ent["sentence"]

                    res = None
                    sys.stderr.write(f"\nTRY: {suspect}\n")
                    for aka, person in art_map.items():
                        if suspect in aka:
                            res = art_map[aka]
                        else:
                            if suspect in person:
                                res = art_map[person]
                        if res:
                            art_map[suspect] = person
                            sys.stderr.write(
                                f"\n\033[41m\033[91m NERD {suspect} -> {res} added {suspect} -> {person} \033[0m\n"
                            )
                            break
                    if not res:
                        if suspect and examples[suspect]:
                            res = nerd(suspect, examples[suspect])

                    if not res:
                        continue
                    # This will keep mapping, no harm
                    # map found real name to itself.
                    # Persist over data stream. Will keep writing map, is ok.
                    nerd_map[suspect] = res
                    nerd_map[res] = res
                    # resets every article
                    art_map[suspect] = res
                    art_map[res] = res

            wikimap.append(art_map)
            lap = perf_counter() - start_time

            sys.stderr.write(f"\nTime: {lap:.2f}s\n")

        data["wikimap"] = wikimap
        print(dumps(data))


if __name__ == "__main__":
    run_start_time = perf_counter()

    # This maps aeveryone we found in entire data stream
    nerd_map = {}
    model = MODEL

    if len(sys.argv) > 1:
        model = sys.argv[1]

    # Default to Ollama
    assistant_name = "Ollama"

    if len(sys.argv) > 2:
        if sys.argv[2] == "groq":
            assistant = GroqAI(model=model)
            assistant_name = "Groq"
        if sys.argv[2] == "gemini":
            assistant = GeminiAI(model=model)
            assistant_name = "Gemini"

    if assistant_name == "Ollama":
        assistant = OllamaAI(model=model)

    sys.stderr.write(
        f"\n===\nUsing model: {MODEL} with assistant {assistant_name}\n===\n"
    )

    # main(assistant, nerd_map)
    readstd(procart)

    lap = perf_counter() - run_start_time
    lap = lap / 60
    sys.stderr.write(f"\nTotal Run time: {lap:.2f} min.\n")

    sys.stderr.write("\n===================\nNERD MAP\n===========\n")
    for key, val in nerd_map.items():
        sys.stderr.write(f"{key}\t{val}\n")
