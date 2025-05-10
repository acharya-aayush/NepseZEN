"""
Main test runner for NEPSEZEN project
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all test cases"""
    # Get the directory containing this file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all test modules
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    result = run_all_tests()
    
    # Return non-zero exit code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)
