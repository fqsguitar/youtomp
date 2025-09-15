# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['YouToMP3.py'],
    pathex=[],
    binaries=[('yt-dlp.exe', '.'), ('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin'), ('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin')],
    datas=[('yt_mp3_converter_multi_res.ico', '.'), ('Flags\\br.png', 'Flags'), ('Flags\\us.png', 'Flags')],
    hiddenimports=[],
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
    name='YouToMP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['yt_mp3_converter_multi_res.ico'],
)
