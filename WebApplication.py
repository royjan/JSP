from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_login import LoginManager, login_user, login_required, current_user

from Kits import Kits
from Users import Users
from main import *
from selenium.common.exceptions import WebDriverException
import os
from Helper import *


def setup_login_manager(app):
    lm = LoginManager()
    lm.login_view = 'login'
    lm.init_app(app)
    return lm


# static variables #
app = Flask(__name__)
app.secret_key = 'tapuZ'
login_manager = setup_login_manager(app)


# driver = init_driver()
@app.route('/logout', methods=['GET'])
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        user_obj = Users.get_user(user_name)
        if user_obj:
            if user_obj.is_verify(password):
                login_user(user_obj, remember=True)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                error = 'סיסמה שגויה, נא נסה שנית'
        else:
            error = 'שם משתמש או סיסמה שגויים, נא נסה שנית'
    return render_template('login.html', error=error)


@app.route("/", methods=["GET", "POST"])
@login_required
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


def return_current_driver():
    global driver
    try:
        driver._driver.title
    except (WebDriverException, AttributeError, NameError) as e:
        driver = init_driver()
    return driver


def log_search_part(part_name, vin, license_plate):
    body = f"User: {current_user.user_name} is looking for {part_name} for "
    if vin:
        body += f"vin={vin}"
    else:
        body += f"license plate={license_plate}"
    logger.info(body)

def log_search_mkt(mkt):
    logger.info(f"User: {current_user.user_name} is looking for {mkt}")


@app.route('/search_part', methods=['POST'])
def search_part():
    vin = request.form['vin'].upper().strip()
    license_plate = request.form['license_plate'].strip()
    part_name = request.form['part_name']
    log_search_part(part_name, vin, license_plate)
    current_driver = return_current_driver()
    part_numbers, license_plate, vin = main_flow(current_driver, vin, license_plate, part_name)
    return redirect(
        url_for('index', vin=vin, license_plate=license_plate, part_numbers=part_numbers),
        code=307)  # 307 = post


@app.route('/search_mkt', methods=['POST'])
def search_mkt():
    name = request.form['mkt'].strip()
    log_search_mkt(name)
    search_item(driver, name)
    return redirect(url_for('index'), code=302)


@login_manager.user_loader
def load_user(user_id):
    from Users import Users
    return Users.get_user_by_id(user_id)


if __name__ == '__main__':
    app.run()
