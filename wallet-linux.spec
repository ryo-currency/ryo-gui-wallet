# -*- mode: python -*-

block_cipher = None


a = Analysis(['wallet.py'],
             pathex=['/home/mosu/release/ryo-gui-wallet'],
             binaries=[ ('/usr/lib/x86_64-linux-gnu/qt4/plugins/systemtrayicon/libsni-qt.so', 'qt4_plugins/systemtrayicon') ],
             datas=[ ('/home/mosu/release/ryo-gui-wallet/Resources', 'Resources') ],
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
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='wallet')
