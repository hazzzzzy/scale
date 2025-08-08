"""
    返回结果
    code 类型码 0-成功 1-失败
    data 数据
    msg 提示信息
    kwargs 其他参数
"""
from flask import jsonify, make_response


# 返回成功
def ok(data=None, statusCode=200, msg="操作成功", code=0, headers=None, **kwargs):
    result = {"code": code, "data": data, "msg": msg}
    if kwargs:
        result.update(kwargs)

    response = make_response(jsonify(result), statusCode)

    # 添加自定义 headers
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response


# 返回失败
def failed(msg="操作成功", statusCode=200, data=None, code=-1, headers=None, **kwargs):
    result = {"code": code, "data": data, "msg": msg}
    if kwargs:
        result.update(kwargs)

    response = make_response(jsonify(result), statusCode)

    # 添加自定义 headers
    if headers:
        for key, value in headers.items():
            response.headers[key] = value

    return response
