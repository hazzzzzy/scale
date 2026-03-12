import win32print
from utils import R


def zebra_printer_frame(
    vehicle_type,
    specification,
    scan_code,
    material_code,
    print_date,
    width_mm=80,
    height_mm=60,
):
    """
    车架扫描系统专用斑马打印函数
    左侧：二维码 (内容为这5个字段的换行组合)
    右侧：五行文本 (车种代码、规格、料号、时间、15位编码)
    :param vehicle_type: 车种代码
    :param specification: 规格
    :param scan_code: 15位编码
    :param material_code: 料号
    :param print_date: 打印日期
    :param width_mm: 标签宽度 (默认 80)
    :param height_mm: 标签高度 (默认 60)
    """
    printer_name = "ZDesigner ZD888-300dpi ZPL"

    # --- 1. 自动单位换算 (mm -> dots) ---
    # 300 dpi 设备：1mm ≈ 11.81 dots
    dots_per_mm = 11.81

    label_w = int(width_mm * dots_per_mm)
    label_h = int(height_mm * dots_per_mm)

    # --- 2. 构造打印数据 ---
    # 为保证二维码内中文及回车符合规解析，采用 ^FH 转义特殊字符及换行 (_0D_0A)
    def _zpl_esc(t):
        if t is None:
            return ""
        # 转义自带的 _, ^, ~ 符号，防止被 ZPL 错认为指令吞掉造成乱码
        s = str(t).replace("_", "_5F").replace("^", "_5E").replace("~", "_7E")
        return s

    # 处理日期格式 26/01/01 -> 2026.01.01
    formatted_date = str(print_date).replace("/", ".")
    if len(formatted_date) == 8 and formatted_date.count(".") == 2:
        formatted_date = "20" + formatted_date

    qr_content = f"车种:{_zpl_esc(vehicle_type)}_0D_0A编码:{_zpl_esc(scan_code)}_0D_0A规格:{_zpl_esc(specification)}_0D_0A料号:{_zpl_esc(material_code)}_0D_0A日期:{_zpl_esc(formatted_date)}"

    # 左右布局坐标设定
    # 左侧二维码位置:
    qr_x = 30
    qr_y = 220
    qr_magnification = 6  # 二维码放大倍数

    # 右侧文本整体位置:
    text_x = 335
    start_y = 200
    line_spacing = 80

    # 文本字号
    font_h = 45
    font_w = 45

    # 处理15位编码换行 (单行超过12个字符则拆为两行展示)
    scan_code_str = str(scan_code)

    # 绘制外框坐标和长宽 (框住整个打印纸)
    box_x = 10
    box_y = 30
    box_w = label_w - 20
    box_h = label_h - 40

    # 模拟加粗效果宏：通过在 x, y 偏移微小像素后打印第二次实现伪加粗
    def _bold_text(x, y, text):
        return f"""^FO{x},{y}^A1N,{font_h},{font_w}^FD{text}^FS
^FO{x+2},{y}^A1N,{font_h},{font_w}^FD{text}^FS"""

    # --- 3. 生成 ZPL (支持中文版) ---
    zpl = f"""
    ^XA
    ^CW1,E:SIMSUN.FNT
    ^PW{label_w}
    ^LL{label_h}
    ^CI28
    
    ^FO0,60
    ^FB{label_w},1,0,C
    ^A1N,70,70
    ^FD广东众晟新材料^FS
    ^FO2,60
    ^FB{label_w},1,0,C
    ^A1N,70,70
    ^FD广东众晟新材料^FS
    ^FO0,62
    ^FB{label_w},1,0,C
    ^A1N,70,70
    ^FD广东众晟新材料^FS
    ^FO2,62
    ^FB{label_w},1,0,C
    ^A1N,70,70
    ^FD广东众晟新材料^FS
    
    ^FO{qr_x},{qr_y}
    ^BQN,2,{qr_magnification}
    ^FH^FDQA,{qr_content}^FS
    
    ^FO{box_x},{box_y}^GB{box_w},{box_h},3^FS
    
    {_bold_text(text_x, start_y + line_spacing * 0, "车种类型:")}
    ^FO{text_x + 230},{start_y + line_spacing * 0}^A1N,{font_h},{font_w}^FD{vehicle_type}^FS
    
    {_bold_text(text_x, start_y + line_spacing * 1, "规格:")}
    ^FO{text_x + 140},{start_y + line_spacing * 1}^A1N,{font_h},{font_w}^FD{specification}^FS
    
    {_bold_text(text_x, start_y + line_spacing * 2, "料号:")}
    ^FO{text_x + 140},{start_y + line_spacing * 2}^A1N,{font_h},{font_w}^FD{material_code}^FS
    
    {_bold_text(text_x, start_y + line_spacing * 3, "打印日期:")}
    ^FO{text_x + 230},{start_y + line_spacing * 3}^A1N,{font_h},{font_w}^FD{formatted_date}^FS
    
    {_bold_text(text_x, start_y + line_spacing * 4, "15位编码:")}
    ^FO{text_x + 230},{start_y + line_spacing * 4}^A1N,{font_h},{font_w}^FD{scan_code_str}^FS
    
    ^XZ
    """

    try:
        # --- 4. 发送打印 ---
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            # 检查打印机真实状态
            printer_info = win32print.GetPrinter(hPrinter, 2)
            status = printer_info["Status"]
            attributes = printer_info["Attributes"]

            # 检查状态码位 (离线、错误、缺纸、不可用等)
            error_masks = (
                win32print.PRINTER_STATUS_OFFLINE
                | win32print.PRINTER_STATUS_ERROR
                | win32print.PRINTER_STATUS_PAPER_OUT
                | win32print.PRINTER_STATUS_NOT_AVAILABLE
            )
            if status & error_masks:
                return R.failed("打印机未就绪或处于异常状态，请检查电源、连接或纸张！")

            # 检查属性：是否被系统标记为“脱机使用” (电源关闭时长期拔掉 USB 经常会触发这个)
            if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
                return R.failed("打印机处于脱机状态，请确认其已开机并插入主机！")

            win32print.StartDocPrinter(hPrinter, 1, ("Frame Auto Print", None, "RAW"))
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
