# -*- coding: utf-8 -*-
import win32print
from utils import R


def zebra_printer_warehouse_label(labels):
    """
    入库出库系统 - 打印品检物料点检表
    布局：80x60mm，包含二维码和六行六列的表格。

    :param labels: 标签数据数组 (包含 material_name, material_spec, quantity, box_no, print_date, label_code 等)
    """
    printer_name = "ZDesigner GT800-300dpi ZPL"

    # --- 单位换算 (mm -> dots, 300dpi: 1mm ≈ 11.81 dots) ---
    # label_w = int(80 * 11.81) = 944
    # label_h = int(60 * 11.81) = 708
    label_w = 944
    label_h = 708

    zpl_commands = [
        "^XA",
        "^CW1,E:SIMSUN.FNT",
        f"^PW{label_w}",
        f"^LL{label_h}",
        "^CI28",
    ]

    # 尺寸参数定义
    margin_x = 24
    margin_y = 24
    table_w = label_w - margin_x * 2  # 896
    table_h = label_h - margin_y * 2  # 660

    row_h_header = 160
    row_h_data = 70
    row_h_item = 60
    row_h_footer = (
        table_h - row_h_header - row_h_data * 2 - row_h_item * 5
    )  # 660 - 160 - 140 - 300 = 60

    # 尺寸计算
    # col1 容"型号"/"箱号"2 字标签(45)；col2 放型号值(40)；
    # col3 放"数量""日期"2 字标签(45)；col4 加宽以容纳日期值(半角)避免溢出。
    col1_w = int(table_w * 0.134)  # ≈120，45 字体"型号"/"箱号"2 字 + 边距
    col2_w = int(table_w * 0.543)  # ≈486，型号值 40 字体（含较长料号）
    col3_w = int(table_w * 0.123)  # ≈110，45 字体"数量""日期"2 字
    col4_w = table_w - col1_w - col2_w - col3_w  # ≈180，数量/日期值留足防溢出

    c1 = int(table_w / 6)
    c2 = int(table_w / 6 * 2)
    c3 = int(table_w / 6 * 3)
    c4 = int(table_w / 6 * 4)
    c5 = int(table_w / 6 * 5)

    # 详细项目名称 (固定文本)
    items_list = ["内径通规", "内径止规", "外径通规", "外径止规"]
    middle_list = ["产品外观", "镭雕印记", "包装点数", "检具"]
    right_list = ["检具", "检具", "检具", "检具"]

    # 构建所有标签的打印内容
    final_zpl_str = ""
    for label in labels:
        label_code = label.get("label_code", "")
        material_name = label.get("material_name", "")
        quantity = str(label.get("quantity", ""))
        box_no = str(label.get("box_no", "") or "")
        print_date = label.get("print_date", "")

        zpl = ["^XA", "^CW1,E:SIMSUN.FNT", f"^PW{label_w}", f"^LL{label_h}", "^CI28"]

        qr_size = 5
        qr_y = margin_y + 2
        # 二维码内容改为物料名称（原为 label_code 标签唯一码）；
        # 注意：此标签二维码已不再用于 sep4 扫码入库/出库定位
        zpl.append(f"^FO{margin_x + 5},{qr_y}^BQN,2,{qr_size}^FDQA,{material_name}^FS")

        # 框线
        zpl.append(f"^FO{margin_x},{margin_y}^GB{table_w},0,3^FS")
        zpl.append(f"^FO{margin_x},{margin_y + table_h}^GB{table_w},0,3^FS")
        zpl.append(f"^FO{margin_x},{margin_y}^GB0,{table_h},3^FS")
        zpl.append(f"^FO{margin_x + table_w},{margin_y}^GB0,{table_h},3^FS")

        y = margin_y
        y += row_h_header
        zpl.append(f"^FO{margin_x},{y}^GB{table_w},0,2^FS")
        y += row_h_data
        zpl.append(f"^FO{margin_x},{y}^GB{table_w},0,2^FS")
        y += row_h_data
        zpl.append(f"^FO{margin_x},{y}^GB{table_w},0,2^FS")
        for i in range(5):
            y += row_h_item
            zpl.append(f"^FO{margin_x},{y}^GB{table_w},0,2^FS")

        x1 = margin_x + col1_w
        x2 = x1 + col2_w
        x3 = x2 + col3_w
        start_y = margin_y + row_h_header
        zpl.append(f"^FO{x1},{start_y}^GB0,{row_h_data*2},2^FS")
        zpl.append(f"^FO{x2},{start_y}^GB0,{row_h_data*2},2^FS")
        zpl.append(f"^FO{x3},{start_y}^GB0,{row_h_data*2},2^FS")

        item_start_y = margin_y + row_h_header + row_h_data * 2
        zpl.append(f"^FO{margin_x+c1},{item_start_y}^GB0,{row_h_item*5},2^FS")
        zpl.append(f"^FO{margin_x+c2},{item_start_y}^GB0,{row_h_item*5},2^FS")
        zpl.append(f"^FO{margin_x+c3},{item_start_y}^GB0,{row_h_item*5},2^FS")
        zpl.append(f"^FO{margin_x+c4},{item_start_y}^GB0,{row_h_item*5},2^FS")
        zpl.append(f"^FO{margin_x+c5},{item_start_y}^GB0,{row_h_item*5},2^FS")

        footer_y = margin_y + table_h - row_h_footer
        zpl.append(f"^FO{margin_x+c1},{footer_y}^GB0,{row_h_footer},2^FS")

        # 文本 (加粗)
        header_y_pos = margin_y + (row_h_header - 60) // 2 + 5
        x_pos = margin_x + table_w // 2 - 200
        zpl.append(f"^FO{x_pos},{header_y_pos}^A1N,60,60^FD品检物料点检表^FS")
        zpl.append(f"^FO{x_pos+2},{header_y_pos}^A1N,60,60^FD品检物料点检表^FS")
        zpl.append(f"^FO{x_pos},{header_y_pos+2}^A1N,60,60^FD品检物料点检表^FS")
        zpl.append(f"^FO{x_pos+2},{header_y_pos+2}^A1N,60,60^FD品检物料点检表^FS")

        # 标签字恢复 45；型号/箱号/数量值恢复 40；各值按自身字号在格内垂直居中
        row1_top = start_y
        row2_top = start_y + row_h_data
        ly1 = row1_top + (row_h_data - 45) // 2   # 标签(45)第一行居中
        ly2 = row2_top + (row_h_data - 45) // 2   # 标签(45)第二行居中
        zpl.append(f"^FO{margin_x + 15},{ly1}^A1N,45,45^FD型号^FS")
        zpl.append(f"^FO{margin_x + 15},{ly2}^A1N,45,45^FD箱号^FS")
        zpl.append(f"^FO{x1 + 10},{row1_top + (row_h_data - 40) // 2}^A1N,40,40^FD{material_name}^FS")
        zpl.append(f"^FO{x1 + 10},{row2_top + (row_h_data - 40) // 2}^A1N,40,40^FD{box_no}^FS")
        zpl.append(f"^FO{x2 + 15},{ly1}^A1N,45,45^FD数量^FS")
        zpl.append(f"^FO{x2 + 15},{ly2}^A1N,45,45^FD日期^FS")
        zpl.append(f"^FO{x3 + 10},{row1_top + (row_h_data - 40) // 2}^A1N,40,40^FD{quantity}^FS")
        # 日期值用半角字体 ^A0、字号 32：避免中文全角下 10 字符日期溢出表格
        zpl.append(f"^FO{x3 + 10},{row2_top + (row_h_data - 32) // 2}^A0N,32,32^FD{print_date}^FS")

        item_y1 = item_start_y + (row_h_item - 35) // 2
        for i in range(3):
            zpl.append(f"^FO{margin_x + i*c2 + 10},{item_y1}^A1N,35,35^FD检验项目^FS")
            zpl.append(
                f"^FO{margin_x + i*c2 + c1 + 10},{item_y1}^A1N,35,35^FD检验人^FS"
            )

        for i in range(4):
            y_pos = item_start_y + row_h_item * (i + 1) + (row_h_item - 35) // 2
            zpl.append(f"^FO{margin_x + 10},{y_pos}^A1N,35,35^FD{items_list[i]}^FS")
            zpl.append(
                f"^FO{margin_x + c2 + 10},{y_pos}^A1N,35,35^FD{middle_list[i]}^FS"
            )
            zpl.append(
                f"^FO{margin_x + c4 + 10},{y_pos}^A1N,35,35^FD{right_list[i]}^FS"
            )

        footer_text_y = footer_y + (row_h_footer - 45) // 2
        zpl.append(f"^FO{margin_x + 10},{footer_text_y}^A1N,45,45^FD抽检人^FS")

        zpl.append("^PQ1")
        zpl.append("^XZ")

        final_zpl_str += "\n".join(zpl) + "\n"

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

            win32print.StartDocPrinter(
                hPrinter, 1, ("Warehouse Label Print", None, "RAW")
            )
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, final_zpl_str.encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

        return R.ok(msg=f"成功推送 {len(labels)} 张标签到打印机")
    except Exception as e:
        return R.failed(f"打印失败: {str(e)}")
