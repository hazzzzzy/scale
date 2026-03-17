# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# 获取当前目录路径
current_dir = os.path.dirname(os.path.abspath('.'))

a = Analysis(
    ['app.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('hazy.ico', '.'),
    ],
    hiddenimports=[
        'pymodbus',
        'pymodbus.client',
        'pymodbus.exceptions',
        'win32print',
        'waitress',
        'flask',
        'utils',
        'utils.R',
        'utils.parse_data',
        'utils.use_modbus',
        'utils.zebra_printer',
        'utils.zebra_printer_frame',
        'utils.zebra_printer_custom_code',
        'env',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='称与打印机v1.27',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='hazy.ico',
)
