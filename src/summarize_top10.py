import re
import json
import sys
import os
import subprocess

def summarize_text_with_gemini(text, ids):
    prompt_file = '/tmp/summarize_prompt.txt'
    prompt_content = f'Summarize the following articles (IDs: {", ".join(map(str, ids))}) into a single cohesive paragraph. Focus on the main events, actors, and outcomes. Mention the article IDs at the end of the summary.'
    with open(prompt_file, 'w') as f:
        f.write(prompt_content)

    ask_gemini_path = '/Users/kyle/hub/Pheme-News/src/ask_gemini.py'
    
    process = subprocess.run(
        [ask_gemini_path, prompt_file],
        input=text,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if process.returncode == 0:
        return process.stdout.strip()
    else:
        return f"Error summarizing: {process.stderr}"

def main():
    top10_md_path = '/Users/kyle/hub/Pheme-News/tmp/top10.md'
    dedupe_jsonl_path = '/Users/kyle/hub/Pheme-News/cache/dedupe.jsonl'

    with open(top10_md_path, 'r', encoding='utf-8') as f:
        markdown_lines = f.readlines()

    all_ids_to_fetch = set()
    for line in markdown_lines:
        if line.strip().startswith('- *'):
            match = re.search(r'\*(\d+)\*', line)
            if match:
                all_ids_to_fetch.add(int(match.group(1)))

    article_texts = {}
    with open(dedupe_jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                article = json.loads(line)
                if article.get('id') in all_ids_to_fetch:
                    article_texts[article['id']] = article.get('text', '')
            except json.JSONDecodeError:
                continue

    new_markdown_content = ""
    section_articles_text = ""
    section_article_ids = []
    
    current_section_lines = []

    for line in markdown_lines:
        is_heading = line.strip().startswith('#')
        
        if is_heading and section_article_ids:
            new_markdown_content += "".join(current_section_lines)
            summary = summarize_text_with_gemini(section_articles_text, section_article_ids)
            new_markdown_content += f"\n**Summary:** {summary}\n\n"
            
            current_section_lines = [line]
            section_articles_text = ""
            section_article_ids = []
        else:
            current_section_lines.append(line)

        if not is_heading and line.strip().startswith('- *'):
            match = re.search(r'\*(\d+)\*', line)
            if match:
                article_id = int(match.group(1))
                if article_id in article_texts:
                    section_article_ids.append(article_id)
                    section_articles_text += f"Article ID: {article_id}\n"
                    section_articles_text += article_texts[article_id] + "\n\n"

    new_markdown_content += "".join(current_section_lines)
    if section_article_ids:
        summary = summarize_text_with_gemini(section_articles_text, section_article_ids)
        new_markdown_content += f"\n**Summary:** {summary}\n"

    with open(top10_md_path, 'w', encoding='utf-8') as f:
        f.write(new_markdown_content)

if __name__ == "__main__":
    main()
