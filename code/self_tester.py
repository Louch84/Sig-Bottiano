#!/usr/bin/env python3
"""Self-Testing: Verify own capabilities"""

class SelfTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_imports(self):
        modules = ["json", "os", "datetime", "subprocess"]
        results = []
        
        for m in modules:
            try:
                __import__(m)
                results.append({"module": m, "status": "pass"})
                self.tests_passed += 1
            except Exception as e:
                results.append({"module": m, "status": "fail", "error": str(e)})
                self.tests_failed += 1
        
        return results
    
    def run_all_tests(self):
        return {
            "imports": self.test_imports(),
            "passed": self.tests_passed,
            "failed": self.tests_failed
        }

tester = SelfTester()
