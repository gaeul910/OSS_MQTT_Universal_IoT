import unittest
import sys
import os
import coverage

def run_all_tests():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Start code coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Create a test loader
        loader = unittest.TestLoader()
        
        # Discover all tests in the current directory and subdirectories
        test_suite = loader.discover(current_dir, pattern='test_*.py')
        
        # Create a test runner
        runner = unittest.TextTestRunner(verbosity=2)
        
        # Run the tests
        result = runner.run(test_suite)
        
        # Stop coverage
        cov.stop()
        # Generate coverage report
        cov.report()
        # Generate HTML report
        cov.save()  # Save coverage data to .coverage file
        cov.html_report(directory='coverage_html')
        
        # Return appropriate exit code
        return 0 if result.wasSuccessful() else 1
        
    except ImportError:
        print("Coverage package not installed. Run 'pip install coverage' first.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())