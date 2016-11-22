from lxml import html
import requests
from multiprocessing import Pool
import csv

CAMARA_URL = 'http://www2.camara.leg.br/transparencia/recursos-humanos/quadro-remuneratorio/consulta-secretarios-parlamentares/layouts_transpar_quadroremuner_consultaSecretariosParlamentares'
USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'

def fetch_deputies_data():
    """
    Returns a list with all deputies names and its numbers through parsing the <select> element in CAMARA_URL
    """
    page = requests.get(CAMARA_URL)
    tree = html.fromstring(page.content)
    deputies_data = list(
        map(lambda element: {"deputy_name": element.xpath("./text()")[0],"deputy_number": element.xpath('./@value')[0]}, tree.xpath('//select[@id="lotacao"]/option')))
    return deputies_data[1:] # removing the first element: it's the "Selecione um deputado" option.


def fetch_advisors_from_deputy(deputy_number):
    """
    Returns a list with all information available of the advisors that corresponds to the deputy with :deputy_number:
    :deputy_number: (int) the number of the deputy got through fetch_deputies_data()
    """
    page = requests.post(CAMARA_URL, data={"lotacao": deputy_number})
    tree = html.fromstring(page.content)
    return list(map(lambda element: element.xpath("./td/text() | ./td/span/text()"), tree.xpath('//tbody[@class="coresAlternadas"]/tr')))

def run(target):
    deputies_data = fetch_deputies_data()

    pool = Pool(processes=2)
    for deputy_information in pool.imap(organize_deputy_data, deputies_data):
        write_to_csv(deputy_information)
        

def organize_deputy_data(deputy):
    """
    Organizes the deputy information to an array
    """
    output = list(fetch_advisors_from_deputy(deputy["deputy_number"]))
    for dep in output:
        dep.append(deputy["deputy_name"])
        dep.append(deputy["deputy_number"])
    
    return output

def write_to_csv(data):
    """
    Writes :data: to output/latest.csv
    :data: (list) the list with organized deputy information ready to be written
    """
    with open("./output/latest.csv", "a", newline="") as latest_file:
        writer = csv.writer(latest_file, quoting=csv.QUOTE_ALL)
        writer.writerows(data)
            

if __name__ == '__main__':
    run(True)