<h2>Running Requirements</h2>

* No extra library used, hence the empty requirements.txt
* Only python is required

<h2>Running the project</h2>
Just specify the path for two required csv files.
This block of code is edit to main.py with print statement

```commandline
python main.py
```

```python
from catalog_service import CatalogService

# Initializing the service
catalog_service = CatalogService(
    pricat_file_path='<path to pricat.csv>',
    mapping_file_path='<path to mappings.csv>'
)

# Creating dict catalog
catalog = catalog_service.create_catalog()

# Converting to json catalog
print(catalog_service.generate_json_output(catalog=catalog))
```

<h2>Running tests</h2>
```commandline
python -m unittest discover -s tests
```