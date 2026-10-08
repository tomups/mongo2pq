import unittest

import pyarrow as pa

from mongo2pq.schema import Schema, infer_type


class CreateRecordBatchTest(unittest.TestCase):
    def test_casts_top_level_and_nested_values(self):
        schema = Schema('t', fields={
            'flag': pa.bool_(),
            'off': pa.bool_(),
            'zero': pa.int32(),
            'meta': pa.struct([
                ('allow', pa.bool_()),
                ('n', pa.int32()),
                ('inner', pa.struct([('x', pa.bool_())])),
            ]),
            'tags': pa.list_(pa.bool_()),
            # A later struct: each struct must be cast with its own type, not the last one.
            'other': pa.struct([('note', pa.string())]),
        })

        batch = schema.create_record_batch([{
            'flag': 'true',
            'off': False,
            'zero': 0,
            'meta': {'allow': 'true', 'n': None, 'inner': {'x': 'yes'}},
            'tags': ['true', False],
            'other': {'note': 'hi'},
        }])

        self.assertEqual(batch.to_pylist(), [{
            'flag': True,
            'off': False,
            'zero': 0,
            'meta': {'allow': True, 'n': None, 'inner': {'x': True}},
            'tags': [True, False],
            'other': {'note': 'hi'},
        }])

    def test_floats_keep_full_precision(self):
        self.assertEqual(infer_type(19997987226.0, 'credits'), pa.float64())


if __name__ == '__main__':
    unittest.main()
