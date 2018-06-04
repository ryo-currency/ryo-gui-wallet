# -*- mode: python -*-

block_cipher = None


a = Analysis(['wallet.py'],
             pathex=[ 'C:\\Users\\mosu\\Desktop\\ryo-gui-wallet' ],
             binaries=[],
             datas=[ ('C:\\Users\\mosu\\Desktop\\ryo-gui-wallet\\Resources', 'Resources') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='RyoGUIWallet',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='Resources\\icons\\ryo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='wallet')
