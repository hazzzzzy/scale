from flask import Flask
from flask_cors import CORS
from waitress import serve

from utils.use_modbus import read_scale

app = Flask(__name__)
CORS(app, supports_credentials=False, origins=['*'])


@app.route('/read')
def read():
    return read_scale()


# @app.after_request
# def after_request(response):
#     # origin = request.headers.get('Origin')
#     if response.headers.get('Access-Control-Allow-Origin'):
#         response.headers['Access-Control-Allow-Origin'] = "*"
#     else:
#         response.headers.add('Access-Control-Allow-Origin', "*")
#     # response.headers.add('Access-Control-Allow-Origin', "http://43.139.156.154:12306")
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
#
#     if request.method == 'OPTIONS':
#         response.status_code = 200
#     return response


if __name__ == '__main__':
    print("启动成功，等待请求...")
    serve(app, host='0.0.0.0', port=10672)
