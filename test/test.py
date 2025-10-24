from pymodbus.client import ModbusSerialClient

while True:
    COM = input('输入串口号(COM口，一般为COM3或COM4，COM3输入3，COM4输入4):')
    endPort = input('输入设备地址号(slave_id，一般10以内，建议输入10):')
    if endPort.isdigit() and 1 < int(endPort) < 256:
        endPort = int(endPort)
        break
    else:
        print('输入错误，设备地址号在1 ~ 256之间')

passed_slave_ids = []

client = ModbusSerialClient(
    port=f"COM{COM}",
    baudrate=9600,
    bytesize=8,
    parity='N',  # 无校验
    stopbits=1,
    timeout=1
)

if not client.connect():
    print(
        f"串口打开失败，请检查端口的连接状态和是否被占用。\nwindows系统的电脑可以按下 win+q 搜索“设备管理器”，然后查看端口中电子秤是否已经链接上“COM{COM}”串口，如没有显示，检查电子秤与电脑的链接。\n检查无误后重新打开测试软件")
else:
    for sid in range(1, endPort + 1):
        try:
            # 只显示有响应的站号
            # print(f'正在检查slave id [{sid}] -> ', end='')
            result = client.read_holding_registers(address=512, count=10, slave=sid)
            if result and not result.isError():
                print(f"设备地址号 {sid} 已放行")
                passed_slave_ids.append(sid)
        except Exception as e:
            pass

    client.close()
    print('可用设备地址号（slave_id）为', passed_slave_ids)
    print('提示：一般设备地址号为1与3，假如缺少其中一个，则检查两台电子秤之间的链接')
input("扫描结束，输入回车键退出...")
