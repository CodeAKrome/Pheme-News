import sys
import os
sys.path.append(os.path.abspath('../src'))
import read_rss

def test_truncurl():
    assert truncurl('http://example.com') == 'http://example.com'
    