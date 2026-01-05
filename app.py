from flask import Flask, make_response, request
from waitress import serve

from utils import R
from utils.use_modbus import read_scale
from utils.zebra_printer import zebra_printer

app = Flask(__name__)


# CORS(app, supports_credentials=False, origins=['*'])


@app.route('/read', methods=['GET', 'OPTIONS'])
def read():
    if request.method == 'OPTIONS':
        return make_response()  # 直接返回空响应，after_request 会自动加头
    return read_scale()


@app.route('/printer', methods=['GET', 'OPTIONS'])
def printer():
    if request.method == 'OPTIONS':
        return make_response()  # 直接返回空响应，after_request 会自动加头
    interval = request.args.get('interval')
    weight = request.args.get('weight')
    if not interval:
        return R.failed(msg='缺少区号')

    if not weight:
        return zebra_printer(f'区号：{interval}')
    return zebra_printer(f'区号：{interval}，重量：{weight}')


@app.after_request
def after_request(response):
    # 1. 允许跨域
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # 如果前端带了credentials

    # 2. 【关键】允许私有网络访问 (PNA)
    # 这行代码告诉 Edge：我是本地服务，但我允许公网连我
    response.headers['Access-Control-Allow-Private-Network'] = 'true'

    return response


if __name__ == '__main__':
    print("启动成功，等待请求...")
    serve(app, host='127.0.0.1', port=10672)
