import csv
import datetime
import gevent
from gevent.pool import Pool
from lxml import html
import os
import os.path
import requests
import grequests
import time

CAMARA_URL = 'http://www2.camara.leg.br/transparencia/recursos-humanos/quadro-remuneratorio/consulta-secretarios-parlamentares/layouts_transpar_quadroremuner_consultaSecretariosParlamentares'
USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data')
DATE = datetime.date.today().strftime('%Y-%m-%d')
FILE_BASE_NAME = '{}-deputies-advisors.csv'.format(DATE)

def run():
    print("Fetching deputies data...")
    deputies_data = fetch_deputies_data()

    print("Preparing to fetch advisors data...")
    counter = 0

    for response in grequests.imap([ get_request_to_page_of_advisors_from_deputy(deputy) for deputy in deputies_data ], size=8):
        counter +=1
        deputy_with_advisors = extract_advisors_from_page(response)
        deputy_information = organize_deputy_data({"deputy_name": deputy_with_advisors["deputy_name"], "deputy_number": deputy_with_advisors["deputy_number"]}, deputy_with_advisors["deputy_advisors"])
        print("Saving data from deputy... ({} of {})".format(counter, len(deputies_data)))
        write_to_csv(deputy_information, os.path.join(DATA_PATH, FILE_BASE_NAME))

    print("Finished!")


def fetch_deputies_data():
    """
    Returns a list with all deputies names and its numbers after parsing the `<select>` element in `CAMARA_URL`
    """
    page = requests.get(CAMARA_URL)
    tree = html.fromstring(page.content)

    deputies_data = [ {"deputy_name": element.xpath("./text()")[0], "deputy_number": element.xpath('./@value')[0]} for element in tree.xpath('//select[@id="lotacao"]/option') ]
    
    return deputies_data[1:] # removing the first element: it's the "Selecione um deputado" option.


def get_request_to_page_of_advisors_from_deputy(deputy):
    """
    Returns a POST Request object from grequests ready to be sent to `CAMARA_URL` with `lotacao` field filled with `deputy_number`
    :deputy: (dict) A Dict with fields `deputy_name` and `deputy_number`
    """
    return grequests.post(CAMARA_URL, data={"lotacao": deputy["deputy_number"]})


def extract_advisors_from_page(page):
    """
    Returns a dict with keys: `deputy_name`, `deputy_number` and `advisors`
    This function will look for these informations in the HTML inside the Response object in `page`.
    :page: (Response) A response object from requests.post|grequests.post call to `CAMARA_URL` with the `lotacao` field filled with `deputy_number`.
    """
    tree = html.fromstring(page.content)

    select = tree.xpath('//select[@id="lotacao"]/option[@selected]')[0]
    deputy = {"deputy_name": select.xpath('./text()')[0], "deputy_number": select.xpath("./@value")[0]}

    deputy["deputy_advisors"] = [element.xpath("./td/text() | ./td/span/text()") for element in tree.xpath('//tbody[@class="coresAlternadas"]/tr')]
    return deputy

def organize_deputy_data(deputy, advisors):
    """
    Organizes all the deputies information in a list. Use this function to prepare data to be written to CSV format
    :deputy: (Dict) A dict with keys `deputy_name` and `deputy_number`
    :advisors: (list) A list of lists with advisors data. Each list with advisor data must have only four elements
    """
    output = list()
    if len(advisors) == 0:
        return list([["", "", "", "", deputy["deputy_name"], deputy["deputy_number"]]])
    else:
        for dep in advisors:
            output.append(dep[:] + [deputy["deputy_name"], deputy["deputy_number"]]) 
    
    return output


def write_to_csv(data, output):
    """
    Writes `data` to `output`
    :data: (list) the list with organized deputy information ready to be written
    :output: (string) the full path to a file where :data: should be written
    """
    with open(output, "a", newline="") as latest_file:
        writer = csv.writer(latest_file, quoting=csv.QUOTE_ALL)
        writer.writerows(data)
            

if __name__ == '__main__':
    run()
    
    