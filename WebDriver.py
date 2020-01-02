from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from Helper import *
from Part import Part
from PartMapper import PartMapper
from User import User
from CarMapper import CarMapper


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance

class Driver:

    def __init__(self):
        self._driver = Chrome("chromedriver.exe")

    def home_page(self):
        self._driver.get("https://servicebox.peugeot.com/docapvpr/")

    def login(self, user: User):
        import time
        self._driver.get(f"https://{user.name}:{user.password}@servicebox.peugeot.com/pages/frames/loadPage.jsp")
        try:
            self._driver.find_element_by_xpath('//*[@id="userid"]').send_keys(user.name)
            self._driver.find_element_by_xpath('//*[@id="password"]').send_keys(user.password)
            for _ in range(NUMBER_OF_RETRIES_FOR_CHANGE_LANGUAGE):
                self._driver.get("https://servicebox.peugeot.com/do/parametrer")
                self._driver.find_element_by_xpath('//*[@id="menuTools"]/li[5]/a').click()
                time.sleep(7)
                self._driver.find_element_by_xpath('//*[@id="langue"]//option[@value="en_GB"]').click()
                time.sleep(7)
                self._driver.find_element_by_xpath('//*[@id="global"]/div/form[1]/table/tbody/tr[6]/td/input').click()
                if self._driver.find_element_by_xpath('//*[@id="menuTools"]/li[5]/a').text == 'My Profile':
                    user.connected = True
                    self.home_page()
                    break
        except NoSuchElementException:
            logger.exception("User name or password are wrong!")
            raise ValueError("User name or password are wrong!")

    def show_popup_with_explanation(self, parts: [Part], car: CarMapper):
        self.close_other_windows()
        self.check_if_timeout()
        self.home_page()
        self.search_vin(car.vin)

        car_name = self.get_car_name()
        if not car_name:
            logger.exception(f"vin not found: {car.vin}")
            return "לא נמצא מספר שלדה", car.license_plate, car.vin
        CarMapper.name_car_by_vin(car, car_name)
        part_numbers = self.over_every_parts(parts, car_name)
        return part_numbers, car.license_plate, car.vin

    def take_screen_shot(self, part_mapper: PartMapper):
        try:
            import os
            folders = os.listdir(IMAGES_FOLDER)
            car_folder = part_mapper.car_name[:MAX_LENGTH_PER_WORD].replace(" ", "_")
            if car_folder not in folders:
                os.makedirs(f'{IMAGES_FOLDER}/{car_folder}')
            file_path = f'{IMAGES_FOLDER}/{part_mapper.car_name[:MAX_LENGTH_PER_WORD]}/' \
                        f'{part_mapper.part_number[:MAX_LENGTH_PER_WORD]}.png'
            file_path = file_path.replace(" ", "_")
            if not os.path.isfile(file_path):
                self._driver.maximize_window()
                self._driver.get_screenshot_as_file(file_path)
            return file_path
        except:
            logger.warning(f"cant take screen shot for {part_mapper.part_number}")
            return ""

    def get_value_from_multi_part_numbers(self, part: Part) -> str:
        parts = part.original_part_name.split("|")
        parts = [item.strip().upper() for item in parts]
        for _part in parts:
            if "LEFT" in _part or "RIGHT" in _part:
                items = self._driver.find_elements_by_xpath('//*[@id="content"]//tr')
                part_number = self.left_and_right_scenario(_part, items)
                return part_number
            else:
                part_number = self._driver.find_elements_by_xpath(
                    f'//tr[./td[not(contains(@class, "info"))]/div[.//text() = "{_part}"]]'
                    f'//td[contains(@class, "colref")]')
                if len(part_number) > 0:
                    return part_number[0].text
        return "NotAValue"

    def copy_part_number(self, part: Part, car_name: str = "") -> str:
        part_number = self.get_value_from_multi_part_numbers(part)
        if not part_number:  # part_number = input("Please enter your own part number: ")
            logger.warning(f"{str(part.original_part_name)} not found for {car_name}")
        part_number = clean_part_number(part_number)
        add_to_clipboard(part_number)
        return part_number

    def search_item_number(self, text: str, vin: str = 'cj500444'):
        self.home_page()
        self.search_vin(vin)
        self._driver.find_element_by_xpath('//*[@id="requete"]').send_keys(text)
        self._driver.find_element_by_xpath('//*[@id="recherche"]').click()
        self._driver.find_element_by_xpath('//*[@id="cadre"]/font/a').click()

    def search_vin(self, vin: str = ''):
        self.close_other_windows()
        self._driver.find_element_by_xpath('//*[@id="short-vin"]').click()
        self._driver.find_element_by_xpath("//*[@id='short-vin']").clear()
        self._driver.find_element_by_xpath("//*[@id='short-vin']").click()
        self._driver.find_element_by_xpath('//*[@id="short-vin"]').send_keys(vin)
        self._driver.find_element_by_xpath('//*[@id="f1"]/input[2]').click()

    def close_other_windows(self):
        if len(self._driver.window_handles) > 1:
            for window in self._driver.window_handles[1:]:
                self._driver.switch_to.window(window)
                self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[0])

    def go_to_part(self, part):
        self._driver.find_element_by_xpath(f'//*[@id="global"]/div[2]/ul//a[text()="{capitalize(part.cat)}"]').click()
        self._driver.find_element_by_link_text(
            f'{capitalize(part.section)}').click()  # white background links with brown titles
        self._driver.implicitly_wait(3)
        self._driver.find_element_by_xpath(
            f'//*[@id="divTabDoc"]//li/a[contains(text(),"Parts")]').click()  # blue background
        self._driver.find_element_by_xpath(
            f'/html/body/div[4]/div[3]/div[3]/table/tbody/tr[3]/td/div[3]/div[2]/table/tbody//td[contains(text(), '
            f'"{part.line.upper()}")]').click()
        self._driver.switch_to.window(self._driver.window_handles[1])

    def get_car_name(self):
        return self._driver.find_element_by_xpath('//*[@id="infosVehicule"]').text

    def check_if_timeout(self):
        web_obj = self._driver.find_elements_by_xpath('//*[@id="expireSessionContainer"]/div/span/a')
        if web_obj:
            web_obj[0].click()

    @staticmethod
    def build_string_from_dict(part_maps: dict, image_path: list) -> str:
        parts = []
        for (part_name, part_number), path in zip(part_maps.items(), image_path):
            path = path.encode("ascii", "ignore")
            path = path.decode('ascii')
            parts.append(f'{part_name} : {part_number} <a target=_blank href={path}>תמונה</a>')
        return "|".join(parts)

    def over_every_parts(self, parts, car_name):
        part_maps = {}
        parts_images = []
        part_mapper = None
        for part in parts:
            self.close_other_windows()
            try:
                self.go_to_part(part)
                part_number = self.copy_part_number(part, car_name)
                part_mapper = PartMapper(part.name, car_name, part_number)
            except NoSuchElementException:
                logger.exception(f"No part {part.original_part_name} for {car_name}")
                part_number = "NotAValue"
            if part_number != "NotAValue":
                PartMapper.add_part(part_mapper)
                image_path = self.take_screen_shot(part_mapper)
            else:
                image_path = ""
            part_maps[part.name] = part_number
            parts_images.append(image_path)
        part_number = self.build_string_from_dict(part_maps, parts_images)
        return part_number

    @staticmethod
    def left_and_right_scenario(part, items):
        temp_string = part.replace(" LEFT", "").replace(" RIGHT", "")
        current_items = []
        for index, item in enumerate(items):
            temp_string_item = item.text.replace("\n", " ")
            if set(temp_string.split(" ")).issubset(set(temp_string_item.split(" "))):
                current_items.append(items[index])
                current_items.append(items[index + 1])
        if current_items:
            for index, item in enumerate(current_items):
                if (temp_string == item.text.splitlines()[-3]) or (
                        temp_string == " ".join([item.text.splitlines()[-3], item.text.splitlines()[-1]])):
                    if ("RIGHT" in part and "RIGHT" in item.text) or ("LEFT" in part and "LEFT" in item.text):
                        return item.find_element_by_class_name("colref").text
                    else:
                        return current_items[index + 1].find_element_by_class_name("colref").text
