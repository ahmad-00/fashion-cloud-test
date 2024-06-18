from catalog_service import CatalogService

if __name__ == '__main__':
    catalog_service = CatalogService(
        pricat_file_path='pricat.csv',
        mapping_file_path='mappings.csv'
    )
    catalog = catalog_service.create_catalog()
    print(catalog_service.generate_json_output(catalog=catalog))
