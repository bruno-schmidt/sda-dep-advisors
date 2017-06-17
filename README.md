# :cactus: [Archived] This project is not being maintained here anymore. This version is outdated. The working version was sent as PR and merged to [Serenata de Amor](https://github.com/datasciencebr/serenata-de-amor)

## Serenata de Amor Deputy Advisors

A tool to scrap deputy advisors data and save to a CSV file

## Usage

Clone this repository to a folder and run inside of it:

`$ python fetch_deputies_adivisors.py`

The information of each deputy will be written to a CSV file inside `data` folder.

## File format

The file is generated without headers, but the fields are organized in the following order:

"Ponto", "Nome", "Orgão de Origem", "Data de Publicação do Ato", "Deputy Name" and "Deputy Number".

## Requirements

- Python 3+
- lxml
- requests and grequests
