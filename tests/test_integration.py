from io import StringIO
import filecmp
import unittest
from unittest.mock import patch

from horatio import horatio


class IntegrationTest(unittest.TestCase):

    def test_simple(self):
        output_filename = 'tests/fixtures/output_1.csv'
        expected_output_filename = 'tests/fixtures/expected_output_1.csv'

        with \
                patch('horatio.horatio.sys.stdout', new_callable=StringIO) as mocked_stdout, \
                patch('horatio.horatio.sys.stderr', new_callable=StringIO) as mocked_stderr:
            horatio.run(
                orders_filename='tests/fixtures/orders_1.csv',
                barcodes_filename='tests/fixtures/barcodes_1.csv',
                output_filename=output_filename)

            stdout_value = mocked_stdout.getvalue()
            stderr_value = mocked_stderr.getvalue()

        print(stderr_value)

        # check validation
        self.assertIn('duplicate barcodes: 11.', stderr_value)
        self.assertIn('orders without barcode: 1, 123, 124, 192, 3.', stderr_value)

        # check file output
        self.assertTrue(filecmp.cmp(output_filename, expected_output_filename))

        # check statistics printout
        self.assertIn('customer_id,amount_of_tickets\n16,5\n12,4\n19,3\n10,2\n17,1\n', stdout_value)
        self.assertIn('Amount of unused barcodes: 2', stdout_value)


if __name__ == '__main__':
    unittest.main()
