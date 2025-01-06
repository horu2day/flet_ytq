# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

# Flet 관련 모든 데이터 수집
flet_datas, flet_binaries, flet_hiddenimports = collect_all('flet')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=flet_binaries,  # Flet 바이너리 추가
    datas=[
        ('client_secrets.json', '.'),
        ('config.json', '.'),
        ('assets/*', 'assets'),
    ] + flet_datas,  # Flet 데이터 파일 추가
    hiddenimports=[
        'google.auth',
        'google_auth_oauthlib',
        'google.generativeai',
        'youtube_transcript_api'
    ] + flet_hiddenimports,  # Flet hidden imports 추가
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube_Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None
)