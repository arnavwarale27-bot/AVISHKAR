import os
import sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURR_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if CURR_DIR not in sys.path:
    sys.path.insert(0, CURR_DIR)

try:
    from api.index import handler
except ImportError:
    from index import handler
