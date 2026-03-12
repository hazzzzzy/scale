from flask import Flask, make_response, request
from waitress import serve

from utils import R
from utils.use_modbus import read_scale
from utils.zebra_printer import zebra_printer
from utils.zebra_printer_frame import zebra_printer_frame
from utils.zebra_printer_custom_code import zebra_printer_custom_code

app = Flask(__name__)


# CORS(app, supports_credentials=False, origins=['*'])


@app.route("/read", methods=["GET", "OPTIONS"])
def read():
    if request.method == "OPTIONS":
        return make_response()  # 直接返回空响应，after_request 会自动加头
    return read_scale()


@app.route("/printer", methods=["GET", "OPTIONS"])
def printer():
    if request.method == "OPTIONS":
        return make_response()  # 直接返回空响应，after_request 会自动加头
    interval = request.args.get("interval")
    weight = request.args.get("weight")
    if not interval:
        return R.failed(msg="缺少区间")

    if not weight:
        return zebra_printer(f"区间：{interval}")
    return zebra_printer(f"区间：{interval}，重量：{weight}")


@app.route("/frame_printer", methods=["POST", "OPTIONS"])
def frame_printer():
    if request.method == "OPTIONS":
        return make_response()

    data = request.get_json()
    vehicle_type = data.get("vehicle_type", "未知车种")
    specification = data.get("specification", "未知规格")
    scan_code = data.get("scan_code", "")
    material_code = data.get("material_code", "未知料号")
    print_date = data.get("print_date", "")

    if not scan_code:
        return R.failed(msg="缺少15位编码参数")

    return zebra_printer_frame(
        vehicle_type=vehicle_type,
        specification=specification,
        scan_code=scan_code,
        material_code=material_code,
        print_date=print_date,
    )


@app.route("/custom_code_printer", methods=["POST", "OPTIONS"])
def custom_code_printer():
    """自定义编码标签打印：网页一（原始编码含X）和网页三（解析后编码）均调用此接口"""
    if request.method == "OPTIONS":
        return make_response()

    data = request.get_json()
    code = data.get("code", "").strip()

    if not code or len(code) != 15:
        return R.failed(msg="缺少或格式错误的15位编码")

    return zebra_printer_custom_code(code=code)


@app.after_request
def after_request(response):
    # 1. 允许跨域
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,PUT,DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Credentials"] = (
        "true"  # 如果前端带了credentials
    )

    # 2. 【关键】允许私有网络访问 (PNA)
    # 这行代码告诉 Edge：我是本地服务，但我允许公网连我
    response.headers["Access-Control-Allow-Private-Network"] = "true"

    return response


if __name__ == "__main__":
    print("启动成功，等待请求...")
    serve(app, host="127.0.0.1", port=10672)
