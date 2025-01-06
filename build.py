import PyInstaller.__main__

PyInstaller.__main__.run([
   'app.py',
   '--name=YouTube_Analyzer',
   '--onefile',
   '--collect-all=flet',
   '--hidden-import=fastapi',
   '--hidden-import=uvicorn',
   '--add-data=client_secrets.json;.',
   '--add-data=config.json;.'
])