# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import jieba
import os
from pathlib import Path

block_cipher = None

# 正确获取项目根目录
project_root = Path(os.getcwd())

# 自动获取 jieba 路径
try:
    jieba_base = Path(jieba.__file__).parent
except AttributeError:
    jieba_base = project_root / "venv" / "Lib" / "site-packages" / "jieba"

# 数据文件配置
added_files = [
    (str(jieba_base / 'dict.txt'), 'jieba'),
    (str(jieba_base / 'analyse/idf.txt'), 'jieba/analyse')
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    upx_dir='./upx'
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TextProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)