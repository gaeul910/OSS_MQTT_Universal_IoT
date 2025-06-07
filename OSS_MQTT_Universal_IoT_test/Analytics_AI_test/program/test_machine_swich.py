import unittest
from machine_swich import switch
from unittest.mock import patch
import io

class TestMachineSwich(unittest.TestCase):
    def test_switch_on(self):
        uid = "test_uid"
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            switch(True, uid)
            output = fake_out.getvalue()
            self.assertIn("머신들이 작동을 시작하였습니다", output)
            self.assertIn(uid, output)
            self.assertIn('"about": 1', output)

    def test_switch_off(self):
        uid = "test_uid"
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            switch(False, uid)
            output = fake_out.getvalue()
            self.assertIn("머신들이 작동을 멈춥니다", output)
            self.assertIn(uid, output)
            self.assertIn('"about": 1', output)

if __name__ == "__main__":
    unittest.main()