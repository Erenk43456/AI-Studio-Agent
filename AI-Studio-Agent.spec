# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app\\gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        "agents.planner_agent",
        "agents.tool_agent",
        "agents.chat_agent",
        "tools.calculator",
        "tools.file_tool",
        "tools.memory_tool",
        "tools.tool_registry",
        "memory.memory",
        "memory.conversation",
        "models.llm",
        "PySide6.QtWidgets",
        "PySide6.QtCore",
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
    name='AI-Studio-Agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
)