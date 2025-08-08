from flask import Flask
from waitress import serve

from utils.use_modbus import read_scale

app = Flask(__name__)


@app.route('/read')
def read():
    return read_scale()


if __name__ == '__main__':
    print("启动成功，等待请求...")
    serve(app, host='0.0.0.0', port=10672)
