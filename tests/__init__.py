import os.path
import unittest

def run_tests():
    start_dir = os.path.dirname(__file__)
    execfile(start_dir + "/test.py")