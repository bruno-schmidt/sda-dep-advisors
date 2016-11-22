# Requirements

- Python 3+
- lxml
- requests

# Usage

Clone this repository to a folder and run inside of it:

`$ python fetch_deputies_adivisors.py`

The information of each deputy will be written to a CSV file inside `output` folder.

# File format

The file is generated without headers, but the fields are organized in the following order:

"Ponto", "Nome", "Orgão de Origem", "Data de Publicação do Ato", "Deputy Name" and "Deputy Number".

# Extras

It won't take too long to fetch all the data. The file size will be around 1MB when it finishes fetching.
