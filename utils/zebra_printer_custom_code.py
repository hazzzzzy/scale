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

    # --- 2. 布局计算（左文字右二维码，垂直居中） ---
    # 根据标签高度调整二维码放大倍数，避免超出边界
    # 标签高度236点，留上下边距各10点，可用高度约216点
    # 二维码Version 2矩阵25x25，静区+8格=33x33
    # 选择放大倍数6：矩阵150点，静区198点，矩阵高度在可用范围内
    qr_magnification = 6
    qr_matrix_size = 25 * qr_magnification  # 矩阵尺寸：150点
    qr_total_size = 33 * qr_magnification   # 含静区：198点

    # 左右分区：左侧文字区域占40%，右侧二维码区域占60%
    text_area_width = int(label_w * 0.4)  # 左侧文字区域宽度
    qr_area_width = label_w - text_area_width  # 右侧二维码区域宽度

    # 计算垂直居中位置
    # 二维码垂直居中
    qr_y = int((label_h - qr_matrix_size) / 2)

    # 文字边距和文本框尺寸
    text_margin = int(text_area_width * 0.1)  # 左侧留10%边距
    text_fb_width = int(text_area_width * 0.8)  # 文本框宽度为区域宽度的80%

    # 字体尺寸：根据文本框宽度计算，确保15位编码分两行可显示
    # 文本框宽度 text_fb_width，需要显示15个字符，分两行（8+7）
    # 每行最大字符数：8个，每个字符需要的宽度 = text_fb_width / 8
    max_char_width = int(text_fb_width / 8)
    # 字体高度设为标签高度的18%，但不超过最大字符宽度
    font_h = min(int(label_h * 0.18), max_char_width)
    font_w = int(font_h * 0.8)  # 宽度为高度的80%

    # 如果计算出的字体宽度仍然大于最大字符宽度，按比例缩小
    if font_w > max_char_width:
        scale = max_char_width / font_w
        font_w = max_char_width
        font_h = int(font_h * scale)

    # 计算文字垂直位置：使用文本框，顶部与二维码顶部对齐
    text_y = qr_y
    # 文本框行数：2行（15位编码分两行显示）
    text_lines = 2
    line_spacing = int(font_h * 0.2)  # 行间距为字体高度的20%

    # 二维码位置：在右侧区域水平居中
    qr_x = text_area_width + int((qr_area_width - qr_matrix_size) / 2)

    # --- 3. 生成 ZPL ---
    # 使用 QA (Quality Q) 确保 15 位字符使用 Version 2
    zpl = f"""^XA
^CW1,E:SIMSUN.FNT
^PW{label_w}
^LL{label_h}
^CI28

# 左侧编码文字（使用文本框分两行显示）
^FO{text_margin},{text_y}
^FB{text_fb_width},{text_lines},{line_spacing},L
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
