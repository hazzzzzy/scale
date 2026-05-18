# -*- coding: utf-8 -*-
import win32print
from utils import R


def zebra_printer_custom_code(code, width_mm=50, height_mm=30):
    """
    自定义编码标签打印：左侧编码文字 + 右侧二维码，整体垂直居中

    布局原则：
    - 文字和二维码都按各自高度做 (label_h - 自身高度) / 2 居中
    - 字号根据"文本区宽度 / 编码长度"自适应，单行显示
    - 二维码放大倍数根据标签高度自适应（净尺寸约占标签高度 65%）

    :param code:      编码字符串（长度可变，常见 13-15 位）
    :param width_mm:  标签宽度（默认 50mm）
    :param height_mm: 标签高度（默认 30mm）
    """
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 1. 单位换算 (300dpi 下 1mm ≈ 11.81 dots) ---
    dots_per_mm = 11.81
    label_w = int(width_mm * dots_per_mm)   # 50mm ≈ 590 dots
    label_h = int(height_mm * dots_per_mm)  # 30mm ≈ 354 dots

    # --- 2. 整体安全边距（约 1.2mm，避免贴边） ---
    margin = max(int(label_w * 0.025), 12)

    # --- 3. 二维码：右侧，垂直居中 ---
    # 模型 2 Version 2 矩阵为 25×25 模块；按 ~65% 标签高度反推放大倍数
    qr_magnification = max(2, min(10, int(label_h * 0.65) // 25))
    qr_size = 25 * qr_magnification

    qr_x = label_w - margin - qr_size
    qr_y = (label_h - qr_size) // 2

    # --- 4. 文字：左侧，单行显示，字号自适应，垂直居中 ---
    code_len = max(len(code), 1)
    text_left = margin
    text_right = qr_x - margin  # 与二维码之间留一个 margin 的间距
    text_area_w = max(text_right - text_left, 1)

    # ^A0 字体高宽比约 1.6:1；按"字符总宽 ≤ 文本区宽度"反推字号，
    # 0.85 系数预留约 15% 字间距，避免溢出
    char_slot = text_area_w / code_len
    font_w = max(int(char_slot * 0.85), 8)
    font_h = int(font_w * 1.6)

    # 字体高度不超过标签高度的 50%，留足上下空间
    max_font_h = int(label_h * 0.5)
    if font_h > max_font_h:
        font_h = max_font_h
        font_w = max(int(font_h / 1.6), 8)

    text_y = (label_h - font_h) // 2

    # --- 5. 生成 ZPL ---
    # 关于原代码的几处修正（与渲染异常直接相关）：
    # 1) 移除 `# xxx` 行：ZPL 不支持 `#` 注释，会被当作未知命令干扰后续字段
    # 2) 移除 `^CW1,E:SIMSUN.FNT`：编码为英数字，无需中文字体；
    #    打印机未必内置宋体，强行替换反而触发字体回退
    # 3) 移除 `^FB ... 2 行` 文本块：实际单行就够，强制双行会让定位偏移
    zpl = (
        "^XA"
        f"^PW{label_w}^LL{label_h}^CI28"
        f"^FO{text_left},{text_y}^A0N,{font_h},{font_w}^FD{code}^FS"
        f"^FO{qr_x},{qr_y}^BQN,2,{qr_magnification}^FDQA,{code}^FS"
        "^XZ"
    )

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
