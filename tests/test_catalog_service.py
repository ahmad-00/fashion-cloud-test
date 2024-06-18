import json
import tempfile
import unittest
from unittest import mock
from unittest.mock import patch

from catalog_service import CatalogService
from mapping import Mapping


class TestCatalogService(unittest.TestCase):

    @patch('builtins.open', new_callable=mock.mock_open,
           read_data='source;destination;source_type;destination_type\nwinter;Winter;season;season\nEU|42;European size 42;size_group_code|size_code;size')
    def test_get_mapping(self, mock_file):
        catalog_service = CatalogService('dummy_pricat.csv', 'dummy_mapping.csv')
        catalog_service._load_mapping()
        mappings = catalog_service._mapping
        self.assertEqual(len(mappings), 2)
        self.assertEqual(mappings[0].source_types, ['season'])
        self.assertEqual(mappings[0].destination_type, 'season')
        self.assertEqual(mappings[0].source, 'winter')
        self.assertEqual(mappings[0].destination, 'Winter')
        self.assertEqual(mappings[1].source_types, ['size_group_code', 'size_code'])
        self.assertEqual(mappings[1].destination_type, 'size')
        self.assertEqual(mappings[1].source, 'EU|42')
        self.assertEqual(mappings[1].destination, 'European size 42')

    @patch('builtins.open', new_callable=mock.mock_open,
           read_data='source;destination;source_type;destination_type\nwinter;Winter;season;season\nEU|42;European size 42;size_group_code|size_code;size')
    def test_get_variation_compound_source_value(self, mock_file):
        catalog_service = CatalogService('dummy_pricat.csv', 'dummy_mapping.csv')
        variation = {'ean': '8719245200978', 'supplier': 'Rupesco BV', 'brand': 'Via Vai', 'catalog_code': '',
                     'collection': 'Winter Collection 2017/2018', 'season': 'Winter', 'article_structure_code': '10',
                     'article_number': '15189-02', 'article_number_2': '15189-02 Aviation Nero',
                     'article_number_3': 'Aviation', 'color_code': '1', 'size_group_code': 'EU', 'size_code': '38',
                     'size_name': '38', 'currency': 'EUR', 'price_buy_gross': '', 'price_buy_net': '58.5',
                     'discount_rate': '', 'price_sell': '139.95', 'material': 'Aviation', 'target_area': 'Woman Shoes'}
        compound_value = catalog_service._get_variation_compound_source_value(
            variation,
            ['size_group_code', 'size_code']
        )
        self.assertEqual(compound_value, 'EU|38')

    @patch('builtins.open', new_callable=mock.mock_open,
           read_data='ean;supplier;brand;catalog_code;collection;season;article_structure_code;article_number;article_number_2;article_number_3;color_code;size_group_code;size_code;size_name;currency;price_buy_gross;price_buy_net;discount_rate;price_sell;material;target_area\n8719245200978;Rupesco BV;Via Vai;;NW 17 - 18;winter;10;15189-02;15189 - 02 Aviation Nero;Aviation;1;EU;38;38;EUR;;58.5;;139.95;Aviation;Woman Shoes\n8719245231736;Rupesco BV;Via Vai;;NW 17 - 18;winter;10;15189-03;15189 - 02 Mojito Brandy Nero;Mojito;3;EU;42;42;EUR;;62.5;;149.95;Mojito;Woman Shoes')
    def test_create_catalog(self, mock_file):
        catalog_service = CatalogService('dummy_pricat.csv', 'dummy_mapping.csv')
        catalog_service._mapping = [
            Mapping(['season'], 'season', 'winter', 'Winter'),
            Mapping(['size_group_code', 'size_code'], 'size', 'EU|42', 'European size 42')
        ]
        catalog = catalog_service.create_catalog()
        self.assertIn('Via Vai', catalog)
        self.assertIn('15189-02', catalog['Via Vai'])
        self.assertEqual(len(catalog['Via Vai']['15189-02']), 1)
        self.assertEqual(catalog['Via Vai']['15189-02'][0]['season'], 'Winter')
        self.assertIn('Via Vai', catalog)
        self.assertIn('15189-03', catalog['Via Vai'])
        self.assertEqual(len(catalog['Via Vai']['15189-03']), 1)
        self.assertEqual(catalog['Via Vai']['15189-03'][0]['size'], 'European size 42')

    @patch('builtins.open', new_callable=mock.mock_open, read_data='')
    def test_generate_json_output(self, mock_file):
        catalog = {
            'Via Vai': {
                '15189-02': [
                    {'ean': '8719245200978', 'supplier': 'Rupesco BV', 'catalog_code': '', 'collection': 'NW 17 - 18',
                     'season': 'Winter', 'article_structure_code': '10', 'article_number_2': '15189 - 02 Aviation Nero'}
                ]
            }
        }
        catalog_service = CatalogService('dummy_pricat.csv', 'dummy_mapping.csv')
        json_output = catalog_service.generate_json_output(catalog)
        expected_json = json.dumps(catalog, indent=4)
        self.assertEqual(json_output, expected_json)

    def test_load_csv_file(self):
        pricat_data = 'ean;supplier;brand;article_number\n123;new_supplier;new_brand;88\n456;other_supplier;other_brand;99'
        mapping_data = 'source_type;destination_type;source;destination\nseason;season;winter;Winter\ncolor_code;color;1;Navy'

        with tempfile.NamedTemporaryFile() as pricat_file:
            with tempfile.NamedTemporaryFile() as mapping_file:
                pricat_file.write(pricat_data.encode('utf-8'))
                pricat_file.flush()
                mapping_file.write(mapping_data.encode('utf-8'))
                mapping_file.flush()

                pricat_file_path = pricat_file.name
                mapping_file_path = mapping_file.name

                catalog_service = CatalogService(pricat_file_path, mapping_file_path)
                self.assertEqual(len(catalog_service._mapping), 2)

                catalog = catalog_service.create_catalog()
                self.assertEqual(len(catalog), 2)

    @patch('builtins.open', new_callable=mock.mock_open,
           read_data='ean;supplier;brand;catalog_code;collection;season;article_structure_code;article_number;article_number_2;article_number_3;color_code;size_group_code;size_code;size_name;currency;price_buy_gross;price_buy_net;discount_rate;price_sell;material;target_area\n8719245200978;Rupesco BV;Via Vai;;NW 17 - 18;winter;10;15189-02;15189 - 02 Aviation Nero;Aviation;1;EU;38;38;EUR;;58.5;;139.95;Aviation;Woman Shoes\n8719245231736;Rupesco BV;Via Vai;;NW 17 - 18;winter;10;15189-03;15189 - 02 Mojito Brandy Nero;Mojito;3;EU;42;42;EUR;;62.5;;149.95;Mojito;Woman Shoes')
    def test_full_workflow(self, mock_file):
        catalog_service = CatalogService('dummy_pricat.csv', 'dummy_mapping.csv')
        catalog_service._mapping = [
            Mapping(['season'], 'season', 'winter', 'Winter'),
            Mapping(['size_group_code', 'size_code'], 'size', 'EU|42', 'European size 42')
        ]
        catalog = catalog_service.create_catalog()
        json_output = catalog_service.generate_json_output(catalog)
        expected_catalog = {
            'Via Vai': {
                '15189-02': [
                    {
                        'ean': '8719245200978', 'supplier': 'Rupesco BV', 'catalog_code': '',
                        'collection': 'NW 17 - 18',
                        'season': 'Winter', 'article_structure_code': '10',
                        'article_number_2': '15189 - 02 Aviation Nero',
                        'article_number_3': 'Aviation', 'color_code': '1', 'size_group_code': 'EU', 'size_code': '38',
                        'size_name': '38', 'currency': 'EUR', 'price_buy_gross': '', 'price_buy_net': '58.5',
                        'discount_rate': '',
                        'price_sell': '139.95', 'material': 'Aviation', 'target_area': 'Woman Shoes'
                    }
                ], '15189-03': [
                    {
                        'ean': '8719245231736', 'supplier': 'Rupesco BV', 'catalog_code': '',
                        'collection': 'NW 17 - 18',
                        'season': 'Winter', 'article_structure_code': '10',
                        'article_number_2': '15189 - 02 Mojito Brandy Nero',
                        'article_number_3': 'Mojito', 'color_code': '3', 'size_name': '42', 'currency': 'EUR',
                        'price_buy_gross': '', 'price_buy_net': '62.5', 'discount_rate': '', 'price_sell': '149.95',
                        'material': 'Mojito', 'target_area': 'Woman Shoes', 'size': 'European size 42'
                    }
                ]
            }
        }
        expected_json = json.dumps(expected_catalog, indent=4)
        self.assertEqual(json_output, expected_json)
