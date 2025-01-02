import os

block_cipher = None

# Required additional files
added_files = [
    ('client_secrets.json', '.'),
    ('config.json', '.'),
    ('assets/*', 'assets'),
]

a = Analysis(
    ['app.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flet.web',
        'google.auth',
        'google_auth_oauthlib',
        'google.generativeai',
        'youtube_transcript_api'
    ],
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
    console=True,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None
)