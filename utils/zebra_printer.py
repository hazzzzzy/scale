import win32print


from utils import R


def zebra_printer(text_content):
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 1. 尺寸定义 (300dpi 下 60mm x 10mm) ---
    label_w = 709  # 60mm
    label_h = 118  # 10mm

    # --- 2. 字体设置 (扁长标签) ---
    # 高度 70 (约 6mm，留足上下边距，防止打印到纸边缘)
    # 宽度 50 (设窄一点，因为纸很宽，可以让字稍微紧凑些，容纳更多内容)
    font_h = 70
    font_w = 50

    # --- 3. 垂直居中计算 ---
    # (纸高 - 字高) / 2
    # (118 - 70) / 2 = 24
    y_pos = 5  # 稍微上移一点点用于视觉修正

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

    # --- 4. ZPL 指令 ---
    # ^PW472: 关键！必须告诉打印机纸宽是 472，否则居中会偏左
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
        return R.ok(msg="打印成功")
    except Exception as e:
        return R.failed(f"打印失败: {str(e)}")
