import configparser
import logging
import os
import sys
import time

from pymodbus.client import ModbusSerialClient

COM = input('输入串口号(COM口，例如3 或 4):')
endPort = int(input('输入设备地址号(slave_id最大值，例如10):'))

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_path, 'config.ini')

# 读取配置
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

if not config.sections():  # 判断是否成功读取
    raise FileNotFoundError(f"配置文件未找到或为空: {config_path}")

PORT = config.get('modbus', 'PORT')
BAUDRATE = config.getint('modbus', 'BAUDRATE')
BYTESIZE = config.getint('modbus', 'BYTESIZE')
PARITY = config.get('modbus', 'PARITY')
STOPBITS = config.getint('modbus', 'STOPBITS')
TIMEOUT = config.getint('modbus', 'TIMEOUT')
ADDRESS = config.getint('modbus', 'ADDRESS')
COUNT = config.getint('modbus', 'COUNT')
RETRY = config.getint('modbus', 'RETRY')

passed_slave_ids = []

logging.getLogger("pymodbus").setLevel(logging.ERROR)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=BYTESIZE,
    parity=PARITY,
    stopbits=STOPBITS,
    timeout=TIMEOUT,
    retries=RETRY,  # 提高“连续失败关口”为 retries+3，避免频繁关闭
)

connection = client.connect()
if not connection:
    print(f"串口 COM{COM} 打开失败，请检查连接状态或查看是否被占用")
else:
    print(f"开始扫描 1 ~ {endPort} 的设备地址...\n")
    for sid in range(1, endPort + 1):
        try:
            result = client.read_holding_registers(address=ADDRESS, count=COUNT, slave=sid)
            if not result.isError():
                print(f"✅ 设备地址号 {sid} 响应正常")
                passed_slave_ids.append(sid)
            else:
                print(f"❌ 设备地址号 {sid} 无响应")
        except Exception as e:
            # 发生异常时，主动重连，避免因内部保护机制关闭后无法继续扫描
            client.close()
            connection = client.connect()
            print(f"⚠️ slave_id {sid} 异常: {e}")
        time.sleep(1)  # 每次请求间隔 300ms，防止设备应答重叠

    if connection:
        # 关闭连接
        client.close()
    print('\n可用设备地址号（slave_id）为:', passed_slave_ids)
    print('提示：一般设备地址号为1与3，假如缺少其中一个，则检查两台电子秤之间的链接')

input("扫描结束，按回车退出...")
