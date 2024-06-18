import unittest

from mapping import Mapping


class TestMapping(unittest.TestCase):
    def test_mapping_create_single_source_type(self):
        mapping = Mapping(source_types=['color_code'], destination_type='color', source='2', destination='Marrone')
        self.assertFalse(mapping.is_combined)
        self.assertEqual(mapping.source_types, ['color_code'])
        self.assertEqual(mapping.destination_type, 'color')
        self.assertEqual(mapping.source, '2')
        self.assertEqual(mapping.destination, 'Marrone')

    def test_mapping_create_multiple_source_types(self):
        mapping = Mapping(source_types=['size_group_code', 'size_code'], destination_type='size', source='EU|39',
                          destination='European size 39')
        self.assertTrue(mapping.is_combined)
        self.assertEqual(mapping.source_types, ['size_group_code', 'size_code'])
        self.assertEqual(mapping.destination_type, 'size')
        self.assertEqual(mapping.source, 'EU|39')
        self.assertEqual(mapping.destination, 'European size 39')
