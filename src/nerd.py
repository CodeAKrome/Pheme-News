import wikipedia as wiki
import sys
import ollama
from wikipedia.exceptions import DisambiguationError, PageError
from json import loads, dumps, JSONDecodeError
import os
from litellm import completion
from time import perf_counter
import re
from groq import Groq
from functools import cache
from time import sleep


# from colorama import init, Fore, Back, Style
# init()

from lib.ollamaai import OllamaAI

"""model name, [groq ollama] default ollama"""

# https://github.com/CodeAKrome/ollama-chat/blob/main/ollama_chat.py#L1431


# MODEL = "gemini/gemini-1.5-flash"
# MODEL = "gemini/gemini-1.5-flash-exp-0827"
# API_KEY=os.environ.get('GEMINI_API_KEY')

MODEL = "bespoke-minicheck"
MODEL = "nemotron-mini"
MODEL = "solar-pro"
MODEL = "mistral-nemo"
MODEL = "hermes3:70b"
MODEL = "qwen2.5:72b"
MODEL = "gemma:7b"
MODEL = "phi3:14b"
MODEL = "phi3:medium-128k"
MODEL = "gemma2:27b"
MODEL = "llama3.1:70b"



PATTERN = re.compile(r"[^0-9]")

def numeric(text):
    return PATTERN.sub("", text)

def digits(string):
    digits = ""
    for char in string:
        if char.isdigit():
            digits += char
        else:
            break
    
    sys.stderr.write(f"digits: {digits}\n")
    
    return digits


# ------

class GroqAI:
    def __init__(self, system_prompt = None, model="llama3-70b-8192", max_tokens=1500, temperature=.1, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.set_system(system_prompt)

    def set_system(self, prompt):
        self.prompt = prompt or "You are a helpful assistant. You reply with short, accurate answers."
        self.system_prompt = {"role": "system", "content": self.prompt}
        self.chat_history = [self.system_prompt]

    def says(self, prompt):
        self.chat_history.append({"role": "user", "content": prompt})

        
        #sys.stderr.write(f"history: {self.chat_history}\n")
        

        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        self.chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
        return response.choices[0].message.content


# -----    

def gemini_says(system, prompt):
    system = system.replace("\n", " ")

    response = completion(
        model=MODEL,
        messages=[{"role":"system", "content": system}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def wikipeeps00(suspect, max_results=10):
    try:
        # Search for the suspect
        search_results = wiki.search(suspect, results=max_results)
        
        people = []
        for result in search_results:
            try:
                # Get the page for each result
                page = wiki.page(result, auto_suggest=False)
                
                # Check if the page is about a person
                if any(category.lower().endswith('births') for category in page.categories):
                    people.append(page.title)
            except (DisambiguationError, PageError):
                # Skip disambiguation pages and non-existent pages
                continue
        
        return people
    except Exception as e:
        sys.stderr.write(f"An error occurred: {e}")
        return []

@cache
def wikipeeps(suspect):
    # Check if the page is about a person
    try:
        page = wiki.page(suspect, auto_suggest=False)
        if any(category.lower().endswith('births') for category in page.categories):
            return True
    except Exception as e:
        sys.stderr.write(f"An error occurred: {e}")
    return False


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
def nerd(suspect, sentence):
# def nerd(suspect, sentence, partial_matches):
# def nerd(suspect, sentence, art, partial_matches):
    # yes = dumps({"answer": "Yes"})
    # no = dumps({"answer": "No"})
    system_base = f"You are a world famous detective like Sherlock Holmes. You always answer accurately. You will find this person's true identity.\n"
    system_base += "You will correctly identify this person. You will not mistake them for any other person or member of their family like a son, daughter or wife.\n"
    system_base += "Professions, sexes and nationalities must match for correct identification.\n"
    # system = f"{system_base}Only reply with {yes} or {no} to the following question using JSON:"
    system = f"{system_base}Only reply with 'yes' or 'no' to the following question:\n"

# groq
    # sys.stderr.write(F"SYSTEM:\n{system}\n")
    
    assistant.set_system(system)

    usual_suspects = summ_people(suspect)
    
    # Add partial matches from history to the dictionary
    # if partial_matches:
    #     for ent in partial_matches:
    #         usual_suspects[ent] = wiki_cache(ent)
    #         sys.stderr.write(F"ADD PART:\n{ent}\n")
            
    # lineup = {}
    
    for person, summ in usual_suspects.items():
        # prompt = f"Is {suspect} in the following sentence:\n{sentence}\nthe same person as {person} in the following summary:\n{summ}\nAnswer 'yes' or 'no'."
        prompt = f"Is <suspect>{suspect}</suspect> in the following example:\n<example>{sentence}</example>\nthe same person as <person>{person}</person> in the following summary:\n<summary>{summ}</summary>\nAnswer 'yes' or 'no'.\n"
        # prompt = f"Is {suspect} in the following:\n{sentence} in the news article:\n{art}\nthe same person as {person} in the following summary:\n{summ}\nAnswer 'yes' or 'no'.\n"
        # prompt = f"{system} Is {suspect} in the following sentence: {sentence} the same person as {person} in the following summary: {summ}"

        #groq
        raw = assistant.says(prompt)
        
        
        sys.stderr.write(f"RAW: {raw}\n")
        
        
        ans = "no"
        if "yes" in raw.lower():
            ans = "yes"
        
        # ans = ollama_says(prompt)
        # prompt = f"Is {suspect} in the following sentence: {sentence} the same person as {person} in the following summary: {summ}"
        # ans = gemini_says(system, prompt)

        # sys.stderr.write(f"\033[41m\033[91m {suspect} -> {person}\t{ans} \033[0m\n")
        sys.stderr.write(f"{suspect} -> {person}\t{ans}\n")
        # print(f"{Back.WHITE}{Fore.GREEN}{suspect} -> {person}\t{ans}{Style.RESET_ALL}\n", file=sys.stderr)
                
        if "yes" in ans:
            sys.stderr.write(f"\n\n\033[41m\033[91m Match found: {suspect} -> {person}\033[0m\nsummary: {summ}\n")
            return person
            # lineup[person] = summ

    return None
            
    # sys.stderr.write("lineup")
    l = len(lineup)
    if not l: return None
    
    system = f"{system_base}\nThere are {l} people that might match the description of {suspect} in the sentences: {sentence}\n"
    # system = f"{system_base}\nThere are {l} people that might match the description of {suspect} in the sentence: {sentence}\n in the article: {art}.\n"
    system += f"Is <suspect>{suspect}</suspect> in the summary:\n<summary>{summ}</summary>\n the same person as one of the following suspects?\n"
    system += f"These {l} choices will be of the format <id>id</id><summary>summary</summary>.\n"
    system += f"You will reply with the id number and only the id number of the summary that identifies <suspect>{suspect}</suspect> or the None if none of them match. You will not output any other text.\n"
    
    # groq
    assistant.set_system(system)
    prompt = ''
    
    i =0
    for person, summ in lineup.items():
        # groq
        # system += f"<id>{i}<summary>{summ}<end>\n\n"
        prompt += f"<id>{i}</id><summary>{summ}</summary>\n\n"
        sys.stderr.write(f"can: {i}\t{person}\n")
        i += 1

    # groq
    # system += "Which one is it?"
    prompt += f"Reply with an id between 0 and {i - 1} inclusive describing the person or None if no description fits. The name, sex, nationality and profession must match. Do not match sons, daughters, husbands or wives of the person.\n"
    ans = assistant.says(prompt)

    # ans = ollama_says(system)
    # prompt = "Which one is it?"
    # ans = gemini_says(system, prompt)

    # sys.stderr.write(f"\nSYS: {system}")


    sys.stderr.write(f"ANS: {ans}\n")

    if ans == "None" or ans == None:
        sys.stderr.write(f"No match found: {suspect}\n")
        return None

    try:
        match = re.search(r'\d+', ans)
        if match:
            ans = match.group()
        else:
            return None
        idx = int(numeric(ans))
        person, summ = list(lineup.items())[idx]
        
        sys.stderr.write(f"\n\n\033[41m\033[91m Match found: {suspect} -> {person}\033[0m\nsummary: {summ}\n")
        
        # Matches? We need those stinkin' matches!
        # Taken care of below in main()
        # nerd_map[suspect] = person    
        
        
        return person
    except ValueError as e:
        sys.stderr.write(f"\nAnswer was junk: {ans} {e}\n")
    except IndexError as e:
        sys.stderr.write(f"\nAnswer out of range junk: {ans} {e}\n")
    except TypeError as e:
        sys.stderr.write(f"\nAnswer wrong type junk: {ans} {e}\n")
    return None
            
def main(assistant, nerd_map):
    recno = 1

    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            data = loads(line)
        except JSONDecodeError as e:
            sys.stderr.write(f"JSON: {e}\n{line}\n")
            continue
        # This should mean this is an rss flavored record
        if not 'ner' in data:
            print(line)
            continue


        sys.stderr.write(f"\n\n=== RECNO: {recno} ===\n\n")
        recno += 1

        # Have data
        ner = data['ner']
        wikimap = []
        # art = data['text']

        art_map = {}

        # Collect example sentences.
        examples = {}
        for ent in ner:
            for span in ent['spans']:
                if span['value'] == "PERSON":
                    suspect = span['text']
                    sentence = ent['sentence']
                    if suspect in examples:
                        examples[suspect] += sentence
                    else:
                        examples[suspect] = sentence

        # Sentence iteration, 2nd pass.
        for ent in ner:
            start_time = perf_counter()
            sys.stderr.write(f"\n=>\t{ent['sentence']}\n")

            # NER to the D in single sentence
            # alias = {}
                    
            for span in ent['spans']:
                if span['value'] == "PERSON":
                    suspect = span['text']
                    sentence = ent['sentence']

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
                            sys.stderr.write(f"\n\033[41m\033[91m NERD {suspect} -> {res} added {suspect} -> {person} \033[0m\n")
                            break
                    if not res:
                        res = nerd(suspect, examples[suspect])
                        
                    # You look familiar
                    # if suspect in art_map:
                    #     res = art_map[suspect]
                    # if suspect in nerd_map:
                    #     res = nerd_map[suspect]
                        # sys.stderr.write(f"\n{Back.WHITE}{Fore.CYAN}NERD {suspect} -> {res}{Style.RESET_ALL}\n")
                    #     sys.stderr.write(f"\n\033[41m\033[91m NERD {suspect} -> {res} \033[0m\n")
                    # else:
                        # Try substring. They ofter say whole name then refer by last or title. This is 
                                
                            
                        # partial_matches = [key for key in art_map if suspect in key]
                        # partial_matches = [key for key in nerd_map if suspect in key]
                        
                        # if partial_matches:
                        #     sys.stderr.write(f"\033[41m\033[91m partials: {', '.join(partial_matches)} \033[0m\n")
                        
                        
                        # Detection
                    # res = nerd(suspect, examples[suspect])
                        # res = nerd(suspect, examples[suspect], partial_matches)
                        # res = nerd(suspect, examples[suspect], art, partial_matches)
                    
                    if not res: continue
                    # alias[suspect] = res

                    # This will keep mapping, no harm
                    # map found real name to itself.
                    # Persist over data stream. Will keep writing map, is ok.
                    nerd_map[suspect] = res
                    nerd_map[res] = res
                    # resets every article
                    art_map[suspect] = res
                    art_map[res] = res

            wikimap.append(art_map)
            # wikimap.append(alias)
            lap = perf_counter() - start_time
            
            sys.stderr.write(f"\nTime: {lap:.2f}s\n")
            
        data['wikimap'] = wikimap
        print(dumps(data))

if __name__ == "__main__":
    run_start_time = perf_counter()

    # This maps aeveryone we found in entire data stream
    nerd_map = {}    

    if len(sys.argv) > 1:
        MODEL = sys.argv[1]

    assistant_name = "Ollama"

    if len(sys.argv) > 2:
        if sys.argv[2] == 'groq':
            assistant = GroqAI()
            assistant_name = "Groq"
        else:
            assistant = OllamaAI(model=MODEL)
    else:
        assistant = OllamaAI(model=MODEL)
            
    sys.stderr.write(f"\n===\nUsing model: {MODEL} with assistant {assistant_name}\n===\n")

    main(assistant, nerd_map)
    lap = perf_counter() - run_start_time
    lap = lap / 60
    sys.stderr.write(f"\nTotal Run time: {lap:.2f} min.\n")
    
    sys.stderr.write("\n===================\nNERD MAP\n===========\n")
    for key, val in nerd_map.items():
        sys.stderr.write(f"{key}\t{val}\n")
        