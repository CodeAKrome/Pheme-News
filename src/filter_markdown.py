#!/usr/bin/env python

import sys

class Node:
    def __init__(self, heading='', level=0):
        self.heading = heading
        self.level = level
        self.articles = []
        self.children = []
        self.keep = False

    def to_markdown(self, level=0):
        if not self.keep:
            return ""
        
        lines = []
        if self.heading:
            lines.append(self.heading)
        
        lines.extend(self.articles)
        
        for child in self.children:
            child_md = child.to_markdown(level + 1)
            if child_md:
                lines.append(child_md)
        
        return '\n'.join(lines)

def parse_markdown_to_tree(lines):
    root = Node('root', 0)
    path = [root]
    
    for line in lines:
        if not line.strip():
            continue
            
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            node = Node(line, level)
            
            while path[-1].level >= level:
                path.pop()
            
            path[-1].children.append(node)
            path.append(node)
        else:
            path[-1].articles.append(line)
            
    return root

def filter_tree(node):
    for child in node.children:
        filter_tree(child)
        
    direct_article_count = 0
    for article in node.articles:
        if article.strip().startswith('-'):
            direct_article_count += 1
            
    if direct_article_count >= 3:
        node.keep = True
    
    has_kept_child = any(child.keep for child in node.children)
    
    if has_kept_child:
        node.keep = True
        
    if node.level == 0:
        node.keep = True

def run():
    content = sys.stdin.read()
    lines = content.split('\n')
    
    tree = parse_markdown_to_tree(lines)
    filter_tree(tree)
    
    output = []
    for child in tree.children:
        md = child.to_markdown()
        if md:
            output.append(md)
            
    print('\n'.join(output))

run()
