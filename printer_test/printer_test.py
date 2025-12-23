import win32print


def list_printers():
    # 枚举本地打印机
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    for p in printers:
        print(f"打印机名: {p[2]}")


def zebra_printer(text_content):
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 参数配置 ---
    # 标签尺寸 (300dpi下)
    label_w = 330  # 28mm
    label_h = 142  # 12mm

    # 字体配置 (A0N是内置缩放字体，比较清晰)
    font_h = 85  # 字体高度
    font_w = 80  # 字体宽度

    # 垂直居中计算 Y 坐标
    y_pos = int((label_h - font_h) / 2) - 5  # 减5是为了视觉修正，因为文字有基线

    # 构造 ZPL 指令
    # ^XA: 开始
    # ^PW330: 告诉打印机标签有多宽（防止打印偏出）
    # ^LL142: 告诉打印机标签有多长
    # ^CI28: 尝试开启UTF-8模式 (为了支持中文，见下方注意)
    # ^FO0,{y_pos}: 设置起始坐标，X=0(最左), Y=计算出的垂直居中位置
    # ^A0N,{font_h},{font_w}: 使用0号字体
    # ^FB{label_w},1,0,C,0: 创建一个宽度等于标签总宽的文本块，1行，居中对齐(C)
    # ^FD...^FS: 填充内容
    # ^XZ: 结束

    zpl = f"""
    ^XA
    ^PW{label_w}
    ^LL{label_h}
    ^CI28
    ^FO0,{y_pos}
    ^A0N,{font_h},{font_w}
    ^FB{label_w},1,0,C,0
    ^FD{text_content}^FS
    ^XZ
    """

    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(hPrinter, 1, ("Label Print", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # 必须 encode 为 utf-8
                win32print.WritePrinter(hPrinter, zpl.encode('utf-8'))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return "打印成功"
    except Exception as e:
        return f"打印失败: {str(e)}"


while True:
    order = input('输入 1 查询打印机列表\n输入 2 测试打印（注意：仅适配ZDesigner ZD888-300dpi ZPL打印机）\n输入其他数字结束\n请输入：')
    if not order.isdigit():
        print('只可输入数字')
        continue
    if int(order) == 1:
        list_printers()
        continue
    if int(order) == 2:
        zebra_printer('TEST')
        continue
    break
