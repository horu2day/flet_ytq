# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.venv/Lib/site-packages/fake_http_header/data', 'fake_http_header/data'),
        ('.venv/Lib/site-packages/playwright_stealth/js/*.js', 'playwright_stealth/js/'),
        ('client_secrets.json', '.'),
        ('config.json', '.')
    ],
    hiddenimports=[
        'fake_http_header',
        'fake_http_header.data',
        'playwright_stealth',
        'cryptography',
        'Cryptodome',
        'OpenSSL',
        'PIL',
        '_cffi_backend',
        'aiohttp._http_parser',
        'aiohttp._http_writer',
        'aiohttp._websocket.mask',
        'aiohttp._websocket.reader_c',
        'charset_normalizer.md',
        '_multiprocessing',
        '_hashlib',
        '_sqlite3',
        '_ssl',
        '_lzma',
        'frozenlist._frozenlist',
        'cffi._pycparser',
        'google._upb._message',
        'grpc._cython.cygrpc',
        'jiter.jiter',
        'pydantic._pydantic_core',
        'regex._regex',
        'rpds.rpds',
        'select',
        'sniffio._impl',
        'tqdm._monitor',
        'tqdm._tqdm_pandas',
        'win32evtlog',
        'win32pdh',
         'xxhash._xxhash',
         'yaml._yaml',
         'setuptools._distutils.spawn',
         'setuptools._vendor.backports.tarfile.compat.py38',
          'setuptools._vendor.platformdirs.api',
         'setuptools._vendor.platformdirs.android',
         'setuptools._vendor.platformdirs.macos',
        'setuptools._vendor.platformdirs.unix',
        'setuptools._vendor.platformdirs.windows',
        'setuptools._vendor.tomli._parser',
        'setuptools._vendor.tomli._re',
        'setuptools._vendor.tomli._types',
         'setuptools._vendor.more_itertools.more',
         'setuptools._vendor.more_itertools.recipes',
        'setuptools._vendor.jaraco.context',
       'setuptools._vendor.jaraco.functools',
       'setuptools._vendor.jaraco.text',
         'h11._abnf',
         'h11._connection',
         'h11._events',
         'h11._headers',
         'h11._readers',
         'h11._receivebuffer',
         'h11._state',
         'h11._util',
         'h11._version',
         'h11._writers',
        'httpcore._http11',
        'httpcore._http2',
        'httpcore._synchronization',
        'httpcore._async._connection',
        'httpcore._async._connection_pool',
        'httpcore._async._http11',
        'httpcore._async._http2',
        'httpcore._async._http_proxy',
         'httpcore._async._interfaces',
        'httpcore._sync._connection',
        'httpcore._sync._connection_pool',
        'httpcore._sync._http11',
        'httpcore._sync._http2',
        'httpcore._sync._http_proxy',
        'httpcore._sync._interfaces',
       'httptools.parser.parser',
       'httptools.parser.url_parser',
        'frozenlist._frozenlist',
         'charset_normalizer.md',
        'anyio._core._eventloop',
        'anyio._core._exceptions',
        'anyio._core._fileio',
        'anyio._core._resources',
        'anyio._core._signals',
        'anyio._core._sockets',
        'anyio._core._streams',
        'anyio._core._subprocesses',
        'anyio._core._synchronization',
        'anyio._core._tasks',
        'anyio._core._testing',
        'anyio._core._typedattr',
        'anyio.abc._eventloop',
        'anyio.abc._resources',
        'anyio.abc._sockets',
        'anyio.abc._streams',
         'anyio.abc._subprocesses',
         'anyio.abc._tasks',
        'anyio.abc._testing',
       'cffi._imp_emulation',
       'cffi._shimmed_dist_utils',
       'cffi.api',
       'cffi.cffi_opcode',
       'cffi.commontypes',
       'cffi.cparser',
       'cffi.error',
       'cffi.ffiplatform',
       'cffi.lock',
       'cffi.model',
       'cffi.pkgconfig',
       'cffi.recompiler',
        'cffi.vengine_cpy',
       'cffi.vengine_gen',
        'cffi.verifier',
        'chardet.big5freq',
        'chardet.big5prober',
        'chardet.chardistribution',
        'chardet.charsetgroupprober',
        'chardet.charsetprober',
        'chardet.codingstatemachine',
        'chardet.codingstatemachinedict',
        'chardet.cp949prober',
        'chardet.enums',
        'chardet.escprober',
        'chardet.escsm',
        'chardet.eucjpprober',
        'chardet.euckrfreq',
        'chardet.euckrprober',
        'chardet.euctwfreq',
        'chardet.euctwprober',
        'chardet.gb2312freq',
        'chardet.gb2312prober',
        'chardet.hebrewprober',
        'chardet.jisfreq',
        'chardet.johabfreq',
        'chardet.johabprober',
        'chardet.jpcntx',
        'chardet.langbulgarianmodel',
        'chardet.langgreekmodel',
        'chardet.langhebrewmodel',
        'chardet.langrussianmodel',
        'chardet.langthaimodel',
        'chardet.langturkishmodel',
        'chardet.latin1prober',
        'chardet.macromanprober',
        'chardet.mbcharsetprober',
        'chardet.mbcsgroupprober',
        'chardet.mbcssm',
        'chardet.resultdict',
        'chardet.sbcharsetprober',
        'chardet.sbcsgroupprober',
        'chardet.sjisprober',
        'chardet.universaldetector',
        'chardet.utf1632prober',
        'chardet.utf8prober',
        'chardet.version',
        'certifi.core',
        'click._compat',
        'click._termui_impl',
        'click._textwrap',
        'click._winconsole',
        'click.core',
        'click.decorators',
        'click.exceptions',
        'click.formatting',
        'click.globals',
        'click.parser',
        'click.shell_completion',
        'click.termui',
        'click.types',
        'click.utils',
       'colorama.ansi',
        'colorama.ansitowin32',
        'colorama.initialise',
        'colorama.win32',
        'colorama.winterm',
        'multidict._abc',
        'multidict._compat',
        'multidict._multidict',
         'multidict._multidict_py',
        'bs4.builder._html5lib',
        'bs4.builder._htmlparser',
        'bs4.builder._lxml',
        'bs4.css',
        'bs4.dammit',
        'bs4.element',
        'bs4.formatter',
        'cffi._pycparser',
         'charset_normalizer.api',
         'charset_normalizer.cd',
          'charset_normalizer.constant',
          'charset_normalizer.legacy',
         'charset_normalizer.md',
         'charset_normalizer.models',
         'charset_normalizer.utils',
         'charset_normalizer.version',
         'frozenlist._frozenlist',
         'cffi._imp_emulation',
         'cffi._shimmed_dist_utils',
        'cffi.api',
        'cffi.cffi_opcode',
        'cffi.commontypes',
        'cffi.cparser',
        'cffi.error',
        'cffi.ffiplatform',
        'cffi.lock',
        'cffi.model',
        'cffi.pkgconfig',
        'cffi.recompiler',
        'cffi.vengine_cpy',
        'cffi.vengine_gen',
        'cffi.verifier',
        'cachetools.keys',
        'aiosqlite.__version__',
        'aiosqlite.context',
        'aiosqlite.core',
        'aiosqlite.cursor',
       'aiofiles.base',
       'aiofiles.tempfile.temptypes',
       'aiofiles.threadpool.binary',
       'aiofiles.threadpool.text',
       'aiofiles.threadpool.utils',
       'aiohappyeyeballs._staggered',
        'aiohappyeyeballs.impl',
       'aiohappyeyeballs.types',
        'aiohappyeyeballs.utils',
         'backports.tarfile.compat.py38',
       'setuptools._vendor.backports.tarfile.compat.py38',
       'attr._cmp',
        'attr._compat',
        'attr._config',
        'attr._funcs',
        'attr._make',
        'attr._next_gen',
        'attr._version_info',
       'attr.converters',
        'attr.exceptions',
        'attr.filters',
        'attr.setters',
        'attr.validators',
        'attrs.converters',
        'attrs.exceptions',
        'attrs.filters',
        'attrs.setters',
        'attrs.validators',
        'crawl4ai.__version__',
        'crawl4ai.async_configs',
        'crawl4ai.async_crawler_strategy',
        'crawl4ai.async_database',
        'crawl4ai.async_logger',
        'crawl4ai.async_webcrawler',
        'crawl4ai.cache_context',
        'crawl4ai.chunking_strategy',
        'crawl4ai.config',
        'crawl4ai.content_filter_strategy',
        'crawl4ai.content_scraping_strategy',
        'crawl4ai.crawler_strategy',
        'crawl4ai.database',
        'crawl4ai.extraction_strategy',
        'crawl4ai.html2text._typing',
        'crawl4ai.html2text.config',
        'crawl4ai.html2text.elements',
        'crawl4ai.html2text.utils',
        'crawl4ai.markdown_generation_strategy',
         'crawl4ai.migrations',
         'crawl4ai.model_loader',
         'crawl4ai.models',
        'crawl4ai.prompts',
         'crawl4ai.ssl_certificate',
         'crawl4ai.user_agent_generator',
         'crawl4ai.utils',
         'crawl4ai.version_manager',
        'crawl4ai.web_crawler',
    ],
    excludes=[
        'matplotlib','pandas', 
        'scipy', 'PyQt5', 'PySide2', 'tkinter',
        'wx', 'pyside', 'IPython', 'pytest'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,        # 단일 파일에 필요
    a.zipfiles,        # 단일 파일에 필요
    a.datas,           # 단일 파일에 필요
    [],
    name='utuv',
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
    onefile=True
)