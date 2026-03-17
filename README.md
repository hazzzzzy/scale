# 虚拟环境配置说明

已在当前目录下成功创建并配置Python虚拟环境。

## 虚拟环境详情

- **虚拟环境路径**: `venv/`
- **Python版本**: 3.9.10
- **依赖包**: 已安装所有必需依赖（Flask, waitress, pymodbus, pywin32）

## 使用方法

### 1. 激活虚拟环境

在Git Bash中运行：
```bash
source venv/Scripts/activate
```

激活后，命令行提示符前会出现 `(venv)` 标识。

### 2. 验证虚拟环境

检查Python解释器位置：
```bash
which python
# 应该显示: /c/OTHERS/项目文件/scale/venv/Scripts/python
```

### 3. 运行应用

在虚拟环境激活状态下，运行主应用：
```bash
python app.py
```

应用将在 `127.0.0.1:10672` 启动。

### 4. 退出虚拟环境

```bash
deactivate
```

## 已安装的依赖

- Flask==2.3.3
- waitress==2.1.2
- pymodbus==3.6.7
- pywin32==306

完整的依赖列表请查看 `requirements.txt`。

## 注意事项

1. 每次打开新的终端窗口都需要重新激活虚拟环境。
2. 确保在运行应用前已激活虚拟环境。
3. 如果遇到权限问题，请确保以管理员身份运行终端（如果需要访问串口设备）。

## 故障排除

如果遇到导入错误：
- 确保虚拟环境已正确激活
- 检查依赖是否安装：`pip list`
- 重新安装依赖：`pip install -r requirements.txt`

## 项目结构

```
.
├── app.py              # 主应用文件
├── config.ini          # 配置文件
├── env.py              # 环境配置
├── requirements.txt    # 依赖列表
├── venv/               # 虚拟环境目录
└── utils/              # 工具模块
    ├── R.py                    # 响应工具
    ├── parse_data.py          # 数据解析
    ├── use_modbus.py          # Modbus通信
    ├── zebra_printer.py       # 斑马打印机
    ├── zebra_printer_frame.py # 车架打印机
    └── zebra_printer_custom_code.py # 自定义编码打印
```

现在可以开始使用项目了！