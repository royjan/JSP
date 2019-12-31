from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file

from Kits import Kits
from main import *
from selenium.common.exceptions import WebDriverException
import os
from Helper import *

app = Flask(__name__)

driver = init_driver()


@app.route("/", methods=["GET", "POST"])
def index():
    parts = Part.get_part_names()
    kits = Kits.get_kits_names()
    all_options = kits | parts
    vins = CarMapper.get_all_cars_vin()
    license_plates = CarMapper.get_all_cars_plate()
    if request.method == "GET":
        return render_template('index.html', parts=all_options, vins=vins, license_plates=license_plates)
    return render_template('index.html', **request.args, parts=all_options, vins=vins, license_plates=license_plates)


@app.route("/get_license_number")
def find_car():
    from json import dumps
    car: CarMapper = CarMapper.get_car_by_vin(request.args['vin'])
    result = {"license_number": car.license_plate}
    return dumps(result, ensure_ascii=False)


@app.route("/get_parts_by_kit")
def get_parts_by_kit():
    from json import dumps
    kit: Kits = Kits.get_parts_by_kit(request.args['name'])
    result = {"parts": kit.get_parts}
    return dumps(result, ensure_ascii=False)


@app.route(f"/{IMAGES_FOLDER}/<folder>/<path>")
def get_image(folder, path):
    path = f"{folder}/{path}"
    path = f"{IMAGES_FOLDER}/{path}"
    path = path.replace("/", "\\")
    return send_file(path, mimetype='image/png')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/search_part', methods=['POST'])
def search_part():
    vin = request.form['vin'].upper()
    license_plate = request.form['license_plate']
    part_name = request.form['part_name']
    global driver
    try:
        driver._driver.title
    except (WebDriverException, AttributeError) as e:
        # if e.msg.startswith('chrome not reachable'):
        driver = init_driver()
    part_numbers, license_plate, vin = main_flow(driver, vin, license_plate, part_name)
    return redirect(
        url_for('index', vin=vin, license_plate=license_plate, part_numbers=part_numbers),
        code=307)  # 307 = post


@app.route('/search_mkt', methods=['POST'])
def search_mkt():
    name = request.form['mkt']
    search_item(driver, name)
    return redirect(url_for('index'), code=302)


if __name__ == '__main__':
    app.run()
