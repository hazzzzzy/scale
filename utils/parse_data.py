import struct


def parse_scale_data(registers, slave_id):
    """解析电子秤寄存器数据"""

    # 1. 解析重量数据（CDAB顺序的浮点数）
    def cdab_to_float(reg1, reg2):
        bytes_data = struct.pack('>HH', reg2, reg1)  # CDAB顺序
        return struct.unpack('>f', bytes_data)[0]

    # 2. 解析单位（ASCII字符）
    def parse_unit(reg):
        try:
            return reg.to_bytes(2, 'big').decode('ascii').strip()
        except:
            return "Unknown"

    # 3. 解析状态位
    def parse_status(reg):
        bits = bin(reg)[2:].zfill(16)
        return {
            'zero': bool(reg & 0x0001),  # 是否为0
            'stable': bool(reg & 0x0002),  # 是否稳定
            'tare_set': bool(reg & 0x0004),  # 是否有皮重
            'overload': bool(reg & 0x0008),  # 是否超载
            'under': bool(reg & 0x0010),  # 是否低于下限
            'ok': bool(reg & 0x0020),  # 重量是否OK
            'over': bool(reg & 0x0040)  # 是否高于上限
        }

    # 主解析逻辑
    result = {
        'slave_id': slave_id,
        'net_weight': cdab_to_float(registers[0], registers[1]),
        'tare_weight': cdab_to_float(registers[2], registers[3]),
        'gross_weight': cdab_to_float(registers[4], registers[5]),
        'unit': parse_unit(registers[6]),
        'status': parse_status(registers[7]),
        'raw_data': registers
    }
    weight = round(result["net_weight"], 2)
    print(f'电子秤{slave_id}的净重: {weight} {result["unit"]}')
    return weight
