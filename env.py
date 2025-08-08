import configparser
import os
import sys

# 获取 .exe 所在目录，而不是 _MEIPASS
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

# 获取配置项
PORT = config.get('modbus', 'PORT')
BAUDRATE = config.getint('modbus', 'BAUDRATE')
BYTESIZE = config.getint('modbus', 'BYTESIZE')
PARITY = config.get('modbus', 'PARITY')
STOPBITS = config.getint('modbus', 'STOPBITS')
TIMEOUT = config.getint('modbus', 'TIMEOUT')
SLAVE_IDS = [int(i) for i in config.get('modbus', 'SLAVE_IDS').split(',')]
ADDRESS = config.getint('modbus', 'ADDRESS')
COUNT = config.getint('modbus', 'COUNT')

if __name__ == '__main__':
    print(f"Modbus配置: PORT={PORT}, BAUDRATE={BAUDRATE}, BYTESIZE={BYTESIZE}, PARITY={PARITY}, STOPBITS={STOPBITS},"
          f" TIMEOUT={TIMEOUT}, SLAVE_IDS={SLAVE_IDS}")
