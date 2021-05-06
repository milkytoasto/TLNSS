# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['TLNSS.py'],
             pathex=['C:\\Users\\MILKIE\\AppData\\Local\\touhou_luna_nights\\TLNSS'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('./icons/logo.png', './icons/logo.png', 'DATA')]
a.datas += [('./icons/folder-closed.png', './icons/folder-closed.png', 'DATA')]
a.datas += [('./icons/folder-expanded.png', './icons/folder-expanded.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TLNSS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
	  icon='icons/logo.ico' )
