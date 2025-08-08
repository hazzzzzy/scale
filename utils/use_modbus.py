import datetime

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

from env import PORT, SLAVE_IDS, BAUDRATE, BYTESIZE, PARITY, STOPBITS, TIMEOUT, ADDRESS, COUNT
from utils import R
from utils.parse_data import parse_scale_data


def read_scale(slave_ids=SLAVE_IDS):
    print(f'******************************{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}******************************')
    client, connection = None, None
    if len(SLAVE_IDS) != 2:
        print(f"SLAVE_IDS配置错误，必须为2个地址: {SLAVE_IDS}")
        return R.failed(f"SLAVE_IDS配置错误，必须为2个地址: {SLAVE_IDS}")
    try:
        # Modbus RTU客户端配置
        client = ModbusSerialClient(
            port=PORT,  # 串口号
            baudrate=BAUDRATE,  # 波特率
            bytesize=BYTESIZE,  # 数据位
            parity=PARITY,  # 无校验
            stopbits=STOPBITS,  # 停止位
            timeout=TIMEOUT  # 超时时间(秒)
        )
        connection = client.connect()

        if connection:
            # print("成功连接到Modbus设备")
            data = {}
            for i in slave_ids:
                result = client.read_holding_registers(address=ADDRESS, count=COUNT, slave=i)
                if not result.isError():
                    # print("保持寄存器值:", result.registers)
                    # print(parse_scale_data(result.registers, i))
                    data[i] = parse_scale_data(result.registers, i)  # 解析寄存器数据
                else:
                    msg = f"读取电子秤地址[{i}]数据失败: {result}"
                    print(msg)
                    return R.failed(msg)
            return R.ok(data)
        else:
            msg = f"无法连接到电子秤，请检查串口号[{PORT}]是否正确"
            print(msg)
            return R.failed(msg)
    except ModbusException as e:
        if str(e) == "Modbus Error: [Input/Output] No response received after 3 retries, continue with next request":
            msg = f"电子秤地址[{SLAVE_IDS}]有误，请检查config.ini中的SLAVE_IDS"
            print(msg)
            return R.failed(msg)
        else:
            msg = f"电子秤异常: {e}"
            print(msg)
            return R.failed(msg)
    finally:
        if connection:
            # 关闭连接
            client.close()


if __name__ == '__main__':
    read_scale()
