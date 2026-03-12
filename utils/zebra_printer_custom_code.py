# -*- coding: utf-8 -*-
import win32print
from utils import R


def zebra_printer_custom_code(code, width_mm=80, height_mm=60):
    """
    自定义编码系统专用斑马打印函数
    布局：二维码居中（上方），编码文字居中（下方）
    二维码内容 = 编码字符串本身（扫描即得编码）

    :param code:      15位编码字符串（网页一为原始含X编码，网页三为解析后编码）
    :param width_mm:  标签宽度（默认80mm）
    :param height_mm: 标签高度（默认60mm）
    """
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 1. 单位换算 (mm -> dots, 300dpi: 1mm ≈ 11.81 dots) ---
    dots_per_mm = 11.81
    label_w = int(width_mm * dots_per_mm)  # ≈ 945
    label_h = int(height_mm * dots_per_mm)  # ≈ 709

    # --- 2. 布局计算（整体垂直居中） ---
    # ZPL 语法中 ^BQN 的第三个参数(放大倍数)官方设计上限就是 10
    qr_magnification = 10

    # 【精准计算各组件高度与宽度】：
    # 标题高度：约 70 dots
    title_h = 70

    # 二维码：15位字符在 QA (Quality Q) 下使用的是 Version 2 (25x25 矩阵)
    # 矩阵宽度 = 25格 * 10倍 = 250 dots (不含静区)
    # 总宽度（含静区）= 33格 * 10倍 = 330 dots
    # 注意：ZPL 的 ^FO 对于二维码通常是以矩阵左上角为基准，静区会向外延伸。
    qr_matrix_w = 250
    qr_total_w = 330

    # 底部文字高度：60 dots
    footer_text_h = 60

    # 设定间距
    gap_after_title = 50
    gap_after_qr = 30

    # 计算总高度：使用矩阵高度 250 以便间距调整更直观
    total_content_h = (
        title_h + gap_after_title + qr_matrix_w + gap_after_qr + footer_text_h
    )

    # 计算起始 Y 坐标，使整体垂直居中于 label_h (约 709 dots)
    start_y = int((label_h - total_content_h) / 2)

    # 计算各组件坐标
    title_y = start_y
    qr_y = title_y + title_h + gap_after_title
    # 使用 qr_matrix_w (250) 作为基准，这样 gap_after_qr=0 时文字就在二维码矩阵边缘
    text_y = qr_y + qr_matrix_w + gap_after_qr

    # 绘制外框坐标和长宽 (框住整个打印纸，上下左右边距均等为 20 dots)
    box_margin = 20
    box_x = box_margin
    box_y = box_margin
    box_w = label_w - (box_margin * 2)
    box_h = label_h - (box_margin * 2)

    # 水平居中坐标计算：
    # 为了让 QR 加上静区后整体居中，矩阵起始位置 qr_x 应为：
    # (标签总宽 - 矩阵宽度) / 2 = (945 - 250) / 2 = 347
    qr_x = int((label_w - qr_matrix_w) / 2)

    # 字体尺寸
    font_h = 60
    font_w = 55

    # --- 3. 生成 ZPL ---
    # 使用 QA (Quality Q) 确保 15 位字符使用 Version 2
    zpl = f"""^XA
^CW1,E:SIMSUN.FNT
^PW{label_w}
^LL{label_h}
^CI28

^FO0,{title_y}
^FB{label_w},1,0,C
^A1N,70,70
^FD广东众晟新材料^FS
^FO2,{title_y}
^FB{label_w},1,0,C
^A1N,70,70
^FD广东众晟新材料^FS
^FO0,{title_y + 2}
^FB{label_w},1,0,C
^A1N,70,70
^FD广东众晟新材料^FS
^FO2,{title_y + 2}
^FB{label_w},1,0,C
^A1N,70,70
^FD广东众晟新材料^FS

^FO{qr_x},{qr_y}
^BQN,2,{qr_magnification}
^FDQA,{code}^FS

^FO{box_x},{box_y}^GB{box_w},{box_h},3^FS

^FO0,{text_y}
^FB{label_w},1,0,C
^A0N,{font_h},{font_w}
^FD{code}^FS

^FO0,{text_y + 2}
^FB{label_w},1,0,C
^A0N,{font_h},{font_w}
^FD{code}^FS

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
