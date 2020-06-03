import json

import requests

from CarMapper import CarMapper
from Helper import retries
from Part import Part
from WebUser import WebUser
from WebDriver import Driver

mapping_english_hebrew = {"misgeret": "מס שלדה",
                          "kinuy_mishari": "כינוי מסחרי",
                          "shnat_yitzur": "שנת ייצור",
                          "tozeret_nm": "תוצרת"}
INF = 500


@retries(num_of_tries=2)
def init_driver():
    my_user = WebUser()
    web_driver = Driver()
    web_driver.login(my_user)
    return web_driver


def main_flow(web_driver, vin: str = '', license_plate='', text='גריל מגן'):
    my_car = add_car_to_db(vin, license_plate)
    parts = Part.get_part_by_name(text)
    return web_driver.show_popup_with_explanation(parts, my_car)


def add_car_to_db(vin: str = '', license_plate=''):
    my_car: CarMapper = CarMapper(vin, license_plate)
    my_car.add_to_db_result()
    return my_car


def search_item(web_driver, text):
    web_driver.search_item_number(text)


def search(text: str):
    response = requests.get(
        f"https://data.gov.il/api/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&q={text}&limit={INF}")
    return json.loads(response.text)['result']


def store_results(parser_response: dict):
    lst = []
    for record in parser_response['records']:
        lst.append({mapping_english_hebrew[k]: v for k, v in record.items() if k in mapping_english_hebrew})
    return lst


def search_thbr(text: str):
    results = search(text)
    records = store_results(results)
    string = ""
    lst = []
    for index, record in enumerate(records, start=1):
        build_string = f"{index}) "
        build_string += ", ".join(f"{k}:{v}" for k, v in record.items())
        lst.append(build_string)
    return lst
