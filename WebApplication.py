import os
from typing import Iterable

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_login import LoginManager, login_user, login_required, current_user
from selenium.common.exceptions import WebDriverException

from Helper import *
from Kits import Kits
from Users import Users
from main import *


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


@app.route('/get_items', methods=['GET'])
def get_items():
    parts = Part.get_part_names()
    return {"parts": list(parts)}


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    payload = parsing_payload(request)
    if request.method == 'POST':
        user_name = payload['username']
        password = payload['password']
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
    if 'thbrstuff' in request.args:
        return render_template('index.html', thbrstuff=request.args['thbrstuff'])
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
    return dumps(result, ensure_ascii=False).encode('utf8')


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


@app.route('/search_part_api', methods=['POST'])
def search_part_api():
    """
    payload = {"part_name" : [str], "vin": str, "license_plate": str}
    output = {"parts": [{"name": str, "serial_number": str, "image": str}, ...], "license_plate": str, "vin": str}
    """
    payload = parsing_payload(request)
    vin = payload.get('vin', '').upper().strip()
    license_plate = payload.get('license_plate', '').strip()
    part_name = get_parts_list(payload['part_name'])
    # log_search_part(part_name, vin, license_plate)
    current_driver = return_current_driver()
    result = search_parts(current_driver, vin, license_plate, part_name)
    return json.dumps(result, ensure_ascii=False).encode('utf8')


def get_parts_list(var: Iterable):
    if type(var) is str:
        return [var]
    return var


@app.route('/search_tahbura', methods=['POST'])
def search_tahbura():
    """
    payload = {"thbrInput": str}
    output = [{"תוצרת": str, "שנת ייצור": number, "מס שלדה": str, "כינוי מסחרי": str}]
    """
    payload = parsing_payload(request)
    text = payload['thbrInput'].strip()
    results = search_thbr(text)
    return results


@login_manager.user_loader
def load_user(user_id):
    from Users import Users
    return Users.get_user_by_id(user_id)


@app.route('/add_car', methods=['POST'])
def add_car():
    payload = parsing_payload(request)
    try:
        vin = payload['vin'].upper().strip()
        license_plate = payload['license_plate'].strip()
        add_car_to_db(vin, license_plate)
        return redirect(
            url_for('index', vin=vin, license_plate=license_plate), code=302)  # 302 = post
    except:
        return redirect(url_for('index'), code=302)


def parsing_payload(_request):
    return dict(_request.json or _request.form or _request.args)


if __name__ == '__main__':
    app.run()
