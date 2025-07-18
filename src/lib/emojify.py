#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import emoji

# Ensure the emoji library is installed. If not, run: pip install emoji
e = emoji.emojize

def emojify(emojis: list[str]) -> str:
    """
    Convert a list of emoji names to their corresponding emoji characters.
    
    Args:
        emojis (list[str]): List of emoji names (e.g., ['smile', 'heart', 'fire'])
    
    Returns:
        str: String containing the emoji characters corresponding to the input names
    
    Example:
        >>> emojify(['smile', 'heart', 'fire'])
        '😀❤️🔥'
        >>> emojify(['thumbs_up', 'party', 'rocket'])
        '👍🥳🚀'
    """
    
    # Convert emoji names to characters
    outstr = ""
    outlist = []
    
    for emoji in emojis:
        code = f':{emoji}:'
        char = e(code)
        outstr += char
        outlist.append(char)
    return outstr, outlist

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ['dotted_line_face', 'heart', 'fire'],
        ['reverse_button', 'record_button', 'play_button'],
        ['right_arrow_curving_down', 'up-down_arrow', 'right_arrow_curving_up'],
        ['invalid_emoji', 'smile', 'nonexistent'],  # Test with invalid names
    ]
    
    print("Testing emoji conversion function:")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        outstr, outlist = emojify(test_input)
        print(f"Test {i}:")
        print(f"  Input:  {test_input}")
        print(f"  Output: {outstr}")
        print(f"  First: {outlist[0]}")
        print()
    
    # Interactive example
    print("Try it yourself:")
    print("emojify(['dog', 'cat', 'pizza']) =>", emojify(['dog', 'cat', 'pizza']))
    