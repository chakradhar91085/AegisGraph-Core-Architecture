import os
import glob
import re

tests_dir = os.path.join("tests")

for test_file in glob.glob(os.path.join(tests_dir, "test_*.py")):
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Rename def test_ to def _test_
    content = re.sub(r"^async def test_", "async def _test_", content, flags=re.MULTILINE)
    content = re.sub(r"^def test_", "def _test_", content, flags=re.MULTILINE)
    
    # Rename calls to test_ to _test_ inside main()
    # E.g. await test_ -> await _test_
    content = re.sub(r"await test_", "await _test_", content)
    content = re.sub(r"(\s+)test_([a-zA-Z0-9_]+)\(", r"\1_test_\2(", content)
    
    # Add TestSuite class before if __name__ == '__main__':
    if "class TestSuite(" not in content:
        is_async = "async def main" in content
        
        if is_async:
            suite_code = """
import unittest
class TestSuite(unittest.IsolatedAsyncioTestCase):
    async def test_all(self):
        try:
            await main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
"""
        else:
            suite_code = """
import unittest
class TestSuite(unittest.TestCase):
    def test_all(self):
        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
"""
        
        content = content.replace('if __name__ == "__main__":', suite_code + '\nif __name__ == "__main__":')
        
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(content)

print("Modified all test files to support unittest and pytest natively.")
