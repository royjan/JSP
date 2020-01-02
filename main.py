from CarMapper import CarMapper
from Helper import retries
from Part import Part
from User import User
from WebDriver import Driver


@retries(num_of_tries=2)
def init_driver():
    my_user = User()
    web_driver = Driver()
    web_driver.login(my_user)
    return web_driver


def main_flow(web_driver, vin: str = '', license_plate='', text='גריל מגן'):
    my_car: CarMapper = CarMapper(vin, license_plate)
    my_car.add_to_db_result()
    parts = Part.get_part_by_name(text)
    return web_driver.show_popup_with_explanation(parts, my_car)


def search_item(web_driver, text):
    web_driver.search_item_number(text)
