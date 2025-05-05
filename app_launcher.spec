# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('main.py', '.'), ('moduli.py', '.'), ('crit_path.py', '.'), ('FAQ.py', '.'), ('gantt_module.py', '.'), ('modular_split_by_links.py', '.'), ('project_planner_module.py', '.'), ('resource_load_module.py', '.'), ('task_ordering.py', '.'), ('word_export.py', '.'), ('FAQ.txt', '.')],
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
    name='app_launcher',
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
)
