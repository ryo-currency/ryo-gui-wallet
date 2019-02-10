# This repo has been deprecated

[Ryo Wallet Atom](https://github.com/ryo-currency/ryo-wallet) has been designed from scratch to replace this project. This wallet will no longer work with the Ryo-currency network.

# Ryo GUI Wallet

Copyright (c) 2018, ryo-currency.com  
Copyright (c) 2017-2018, Sumokoin.org

**One of the most easy-to-use, intuitive GUI (full) wallets in crypto.**

![](https://ryo-currency.com/img/png/dark-wallet.png)


# Ubuntu 16.04

## Running from source

1. Clone the repo:
		
`git clone https://github.com/ryo-currency/ryo-gui-wallet`

2. Install dependencies (with Python 2.7):

```
cd ryo-gui-wallet
pip install -r requirements-no-pyside.txt
sudo apt install python-pyside
```

3. Build/download Ryo binaries

Download latest release from [Ryo-currency repo](https://github.com/ryo-currency/ryo-emergency) and place binaries in `Resources/bin` sub-directory.

4. Run the wallet (Python 2.7):
		
```
python wallet.py
```

## Packaging Wallet

1. Install pyinstaller:

`pip install pyinstaller`

2. Run pyinstaller

First edit `wallet-linux.spec` to point to the correct location, then run pyinstaller.

`pyinstaller wallet-linux.spec`

3. Run and distribute standalone package

Your package will be built to `dist/wallet`. Zip the entire folder and distribute.


# Windows

## Running from source

1. Install Python 2.7

Download and install Python 2.7: https://www.python.org/download/releases/2.7/

2. Download Repo

Either clone the repo, or download zip file from: https://github.com/ryo-currency/ryo-gui-wallet

Then, open a powershell window in source location

3. Install dependencies

`pip install -r requirements.txt`

4. Build/download Ryo binaries

Download latest release from [Ryo-currency repo](https://github.com/ryo-currency/ryo-emergency) and place binaries in `Resources/bin` sub-directory.

5. Run the wallet

`python wallet.py`

## Packaging Wallet

1. Install pyinstaller:

`pip install pyinstaller`

2. Run pyinstaller

First edit `wallet-windows.spec` to point to the correct location, then run pyinstaller.

`pyinstaller wallet-windows.spec`

3. Run and distribute standalone package

Your package will be built to `dist/wallet`. Zip the entire folder and distribute.
