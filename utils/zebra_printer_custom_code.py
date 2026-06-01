# -*- coding: utf-8 -*-
import win32print
from utils import R


def zebra_printer_custom_code(code, width_mm=50, height_mm=30):
    """
    自定义编码系统专用斑马打印函数
    布局：编码文字在左（分两行显示），二维码在右，垂直居中
    二维码内容 = 编码字符串本身（扫描即得编码）

    :param code:      15位编码字符串（网页一为原始含X编码，网页三为解析后编码）
    :param width_mm:  标签宽度（默认70mm）
    :param height_mm: 标签高度（默认20mm）
    """
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 1. 单位换算 (mm -> dots, 300dpi: 1mm ≈ 11.81 dots) ---
    dots_per_mm = 11.81
    label_w = int(width_mm * dots_per_mm)  # 70mm ≈ 827 dots
    label_h = int(height_mm * dots_per_mm)  # 20mm ≈ 236 dots

    # --- 2. 布局计算（左大号文字右二维码，同一水平线对齐，整体两端分散） ---
    # 标签高度 236 dots (20mm)
    # 字体设置 (优化后的“大号”：确保 15 位编码不重叠)
    font_h = 80  # 字体高度 (约 6.8mm)
    font_w = 40  # 字体宽度 (15位 x 40 = 600 dots)

    # 二维码 Version 2 矩阵 25x25
    qr_magnification = 6
    qr_matrix_size = 25 * qr_magnification  # 150 dots

    # 水平间距设定 (Space-between 加大间距)
    # 极左极右页边距
    side_margin = 20  # 约 1.7mm

    # 统一垂直居中计算 (同一条水平线上)
    # 文字垂直偏移：(236 - 80) / 2 = 78
    text_y = int((label_h - font_h) / 2)
    # 二维码垂直偏移：(236 - 150) / 2 = 43
    qr_y = int((label_h - qr_matrix_size) / 2)

    # 文字位置 (左边)
    text_x = side_margin

    # 二维码位置 (右边)
    # 极右：(827 - 20 - 150) = 657
    qr_x = label_w - side_margin - qr_matrix_size

    # --- 3. 生成 ZPL ---
    # 使用 QA (Quality Q) 确保 15 位字符使用 Version 2
    zpl = f"""^XA
^CW1,E:SIMSUN.FNT
^PW{label_w}
^LL{label_h}
^CI28

# 左侧编码文字 (大号字体)
^FO{text_x},{text_y}
^A0N,{font_h},{font_w}
^FD{code}^FS

# 右侧二维码
^FO{qr_x},{qr_y}
^BQN,2,{qr_magnification}
^FDQA,{code}^FS

^XZ
"""

    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            printer_info = win32print.GetPrinter(hPrinter, 2)
            status = printer_info["Status"]
            attributes = printer_info["Attributes"]

            error_masks = (
                win32print.PRINTER_STATUS_OFFLINE
                | win32print.PRINTER_STATUS_ERROR
                | win32print.PRINTER_STATUS_PAPER_OUT
                | win32print.PRINTER_STATUS_NOT_AVAILABLE
            )
            if status & error_masks:
                return R.failed("打印机未就绪或处于异常状态，请检查电源、连接或纸张！")

            if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
                return R.failed("打印机处于脱机状态，请确认其已开机并插入主机！")

            win32print.StartDocPrinter(hPrinter, 1, ("Custom Code Print", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, zpl.encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

        return R.ok(msg="打印成功")
    except Exception as e:
        return R.failed(f"打印失败: {str(e)}")
