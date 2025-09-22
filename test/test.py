from pymodbus.client import ModbusSerialClient

while True:
    endPort = input('输入结束端口号(如247):')
    if endPort.isdigit() and 1 < int(endPort) < 256:
        endPort = int(endPort)
        break

client = ModbusSerialClient(
    port="COM3",
    baudrate=9600,
    bytesize=8,
    parity='N',      # 无校验
    stopbits=1,
    timeout=1
)

if not client.connect():
    print("串口打开失败，请检查端口是否被占用")
else:
    for sid in range(1, endPort + 1):
        try:
            # 只显示有响应的站号
            result = client.read_holding_registers(address=512, count=1, slave=sid)
            if result and not result.isError():
                print(f"找到设备，slave id = {sid}，数据：{result.registers}")
        except Exception:
            # 忽略异常，不打印无响应信息
            pass

    client.close()

input("扫描结束，输入任意键退出...")
