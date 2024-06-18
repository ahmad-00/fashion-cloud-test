import csv
import json
from typing import List, Optional

from mapping import Mapping


class CatalogService:

    def __init__(self, pricat_file_path: str, mapping_file_path: str):
        self.pricat_file_path = pricat_file_path
        self.mapping_file_path = mapping_file_path
        self._load_mapping()

    def _load_csv(self, file_path: str, delimiter: str = ';'):
        with open(file_path, mode='r', newline='') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            for row in csv_reader:
                yield row

    def _load_mapping(self):
        mappings: List[Mapping] = []
        for mapping_dict in self._load_csv(self.mapping_file_path):
            source_types = mapping_dict.get('source_type')
            destination_type = mapping_dict.get('destination_type')
            if source_types and destination_type:
                source_types = source_types.split('|')
                mappings.append(Mapping(
                    source_types=source_types,
                    destination_type=destination_type,
                    source=mapping_dict.get('source'),
                    destination=mapping_dict.get('destination')
                ))
        self._mapping = mappings

    def _get_variation_compound_source_value(self, variation: dict, keys: list) -> Optional[str]:
        try:
            return '|'.join(variation[key] for key in keys)
        except KeyError:
            return None

    def _apply_mapping(self, variation: dict) -> dict:
        for mapping in self._mapping:
            if mapping.is_combined:
                variation_compound_source = self._get_variation_compound_source_value(variation, mapping.source_types)
                if not variation_compound_source:
                    # key already replaced and it should go to next loop
                    continue
                if mapping.source == variation_compound_source:
                    variation[mapping.destination_type] = mapping.destination
                    for key_to_remove in mapping.source_types:
                        del variation[key_to_remove]
            else:
                source_type = mapping.source_types[0]
                variation_source_type = variation.get(source_type)
                if not variation_source_type:
                    # key already replaced and it should go to next loop
                    continue
                if mapping.source == variation_source_type:
                    variation[mapping.destination_type] = mapping.destination
                    if source_type != mapping.destination_type:
                        del variation[source_type]
        return variation

    def create_catalog(self) -> dict:
        catalog = {}
        for variation in self._load_csv(self.pricat_file_path):
            variation = self._apply_mapping(variation)
            brand = variation.pop('brand')
            article_number = variation.pop('article_number')
            if brand not in catalog:
                catalog[brand] = {}
            if article_number not in catalog[brand]:
                catalog[brand][article_number] = []
            catalog[brand][article_number].append(variation)
        return catalog

    def generate_json_output(self, catalog):
        return json.dumps(catalog, indent=4)
