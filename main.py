import json

import requests

from CarMapper import CarMapper
from Helper import retries
from Part import Part
from WebDriver import Driver
from WebUser import WebUser

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


def main_flow(web_driver, vin: str = '', license_plate='', lst_parts=('גריל מגן')):
    my_car = add_car_to_db(vin, license_plate)
    parts = Part.get_part_by_name(lst_parts)
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
    lst = [{mapping_english_hebrew[k]: v for k, v in record.items() if k in mapping_english_hebrew} for record in
           parser_response['records']]
    return lst


def search_thbr(text: str):
    results = search(text)
    records = store_results(results)
    return json.dumps(records, ensure_ascii=False).encode('utf8')
