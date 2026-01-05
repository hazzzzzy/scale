import win32print

from utils import R

import win32print


def zebra_printer(text_content, width_mm=60, height_mm=10):
    """
    通用斑马打印函数
    :param text_content: 打印内容
    :param width_mm: 标签宽度 (毫米)
    :param height_mm: 标签高度 (毫米)
    """
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    try:
        # --- 1. 自动单位换算 (mm -> dots) ---
        # 300 dpi 设备：1mm ≈ 11.81 dots
        dots_per_mm = 11.81

        label_w = int(width_mm * dots_per_mm)
        label_h = int(height_mm * dots_per_mm)

        # --- 2. 动态计算字号 ---
        # 策略：字体高度占纸张高度的 60%，留出上下空隙
        # 但为了防止字体过大（比如正方形纸），限制最大字体高度为 150
        calc_font_h = int(label_h * 0.6)
        if calc_font_h > 150:
            calc_font_h = 150

        # 字体宽度设为高度的 60-70%，保持比例
        calc_font_w = int(calc_font_h * 0.65)

        # --- 3. 动态垂直居中 ---
        # 公式：(纸高 - 字高) / 2
        y_pos = int((label_h - calc_font_h) / 2) - 5  # 减5做视觉修正
        if y_pos < 0:
            y_pos = 0  # 防止负数

        # --- 4. 生成 ZPL (支持中文版) ---
        zpl = f"""
            ^XA
            ^CW1,E:SIMSUN.FNT
            ^PW{label_w}
            ^LL{label_h}
            ^CI28
            ^FO0,{y_pos}
            ^A1N,{calc_font_h},{calc_font_w}
            ^FB{label_w},1,0,C,0
            ^FD{text_content}^FS
            ^XZ
            """

        # --- 5. 发送打印 ---
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(hPrinter, 1, ("Auto Print", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, zpl.encode('utf-8'))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

            return R.ok(msg="打印成功")
    except Exception as e:
        return R.failed(f"打印失败: {str(e)}")
