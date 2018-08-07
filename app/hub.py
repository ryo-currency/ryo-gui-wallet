#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
Hub is a communication medium between Python codes and web UI
'''

from __future__ import print_function

import os, binascii
from time import sleep
import uuid
import json
import re
import hashlib
import webbrowser
from shutil import copy2


from PySide.QtGui import QApplication, QMessageBox, QFileDialog, \
            QInputDialog, QLineEdit
from PySide.QtCore import QObject, Slot, Signal

from utils.common import print_money, print_money2, readFile

from settings import APP_NAME, VERSION, DATA_DIR, COIN, makeDir, seed_languages
from utils.logger import log, LEVEL_ERROR, LEVEL_INFO
from utils.blockchain import pop_blocks

# from utils.notify import Notify
# from sys import stderr

tray_icon_tooltip = "%s v%d.%d" % (APP_NAME, VERSION[0], VERSION[1])

from manager.ProcessManager import WalletCliManager

wallet_dir_path = os.path.join(DATA_DIR, 'wallets')
makeDir(wallet_dir_path)

#password_regex = re.compile(r"^([a-zA-Z0-9_\-!@#\$%\^&\*]{0,256})$")

from webui import LogViewer

class Hub(QObject):
    current_block_height = 0

    def __init__(self, app):
        super(Hub, self).__init__()
        self.app = app


    def setUI(self, ui):
        self.ui = ui

    def setNewWalletUI(self, new_wallet_ui):
        self.new_wallet_ui = new_wallet_ui

    @Slot()
    def import_wallet(self):
        dlg = QFileDialog(self.new_wallet_ui, "Select Import Wallet File")
        dlg.setFileMode(QFileDialog.ExistingFile)
        wallet_filename = None
        if dlg.exec_():
            wallet_filename = dlg.selectedFiles()[0]
        else:
            return

        new_wallet_file = os.path.join(wallet_dir_path, str(uuid.uuid4().hex) + '.bin')
        if wallet_filename:
            wallet_key_filename = wallet_filename + '.keys'
            wallet_address_filename = wallet_filename + '.address.txt'

            if not os.path.exists(wallet_key_filename):
                QMessageBox.warning(self.new_wallet_ui, \
                    'Import Wallet',\
                     """Error: Key file does not exist!<br>
                     Are you sure to select correct wallet file?<br><br>
                     Hint: Wallet file often ends with .bin""")
                return False
            try:
                copy2(wallet_filename, os.path.join(wallet_dir_path, new_wallet_file))
                copy2(wallet_key_filename, os.path.join(wallet_dir_path, \
                                                           new_wallet_file + '.keys'))
                if os.path.exists(wallet_address_filename):
                    copy2(wallet_address_filename, os.path.join(wallet_dir_path, \
                                                                new_wallet_file + '.address.txt'))
            except IOError, err:
                self._detail_error_msg("Importing Wallet", "Error importing wallet!", str(err))
                self.ui.reset_wallet()
                return False

        if not os.path.exists(new_wallet_file):
            return False

        wallet_password = None
        while True:
            wallet_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                "Wallet Password", "Enter password of the imported wallet:", QLineEdit.Password)
            if result:
                if wallet_password is None:
                    QMessageBox.warning(self.new_wallet_ui, \
                            'Wallet Password',\
                             "You must provide password to open the imported wallet")
                else:
                    break
            else:
                return False

        self.on_new_wallet_show_progress_event.emit('Importing wallet...')
        self.app_process_events()

        wallet_address_filepath = new_wallet_file + ".address.txt"
        wallet_address = ''
        if os.path.exists(wallet_address_filepath):
            wallet_address = readFile(wallet_address_filepath)
        self.ui.wallet_info.wallet_filepath = new_wallet_file
        self.ui.wallet_info.wallet_address = wallet_address
        self.ui.wallet_info.is_loaded =True
        self.ui.wallet_info.save()
        self.ui.run_wallet_rpc(wallet_password, 1)

        counter = 0
        block_height = 0
        while not self.ui.wallet_rpc_manager.is_ready():
            self.app_process_events(0.5)
            h = int(self.ui.wallet_rpc_manager.block_height)
            if h >  block_height:
                self.on_new_wallet_update_processed_block_height_event.emit(h, self.ui.target_height)
                counter = 0
                block_height = h
            if self.ui.wallet_rpc_manager.is_invalid_password():
                QMessageBox.critical(self.new_wallet_ui, \
                        'Error Importing Wallet',\
                        "Error: Provided wallet password is not valid!")
                self.ui.reset_wallet()
                return False
            if not self.ui.wallet_rpc_manager.is_proc_running():
                error_detailed_text = self.ui.wallet_rpc_manager.last_error \
                    if self.ui.wallet_rpc_manager.last_error else "Unknown error"
                self._detail_error_msg("Error Importing Wallet", \
                                       "Error importing wallet!", \
                                       error_detailed_text)
                self.ui.reset_wallet()
                return False
            counter += 1
            if counter > 30:
                QMessageBox.critical(self.new_wallet_ui, \
                        'Error Importing Wallet',\
                        """Error: Unknown error.<br>
                        Imported wallet file may be corrupted.
                        Try to restore it with mnemonic seed instead.""")
                self.ui.reset_wallet()
                return False

        if wallet_address == '':
            wallet_address = self.ui.wallet_rpc_manager.rpc_request.get_address()
            self.ui.wallet_info.wallet_address = wallet_address["addresses"][0]["address"]
        else:
            self.ui.wallet_info.wallet_address = wallet_address

        self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
        self._show_wallet_info()
        self.ui.wallet_info.save()
        return True


    @Slot()
    def close_new_wallet_dialog(self):
        log("Closing new wallet dialog...", LEVEL_INFO)
        self.ui.new_wallet_ui.close();
        if self.ui.wallet_info.wallet_filepath \
                    and os.path.exists(self.ui.wallet_info.wallet_filepath):
            self.ui.show_wallet();


    @Slot(unicode, int)
    def create_new_wallet(self, mnemonic_seed=u'', restore_height=0):
        if mnemonic_seed and restore_height > 0:
            ret = QMessageBox.warning(self.new_wallet_ui, \
                    'Restore Wallet',\
                     """Are you sure to restore wallet from blockchain height# %d?<br><br>
                     WARNING: Inccorect height# will lead to incorrect balance and failed transactions!""" % restore_height, \
                     QMessageBox.Yes|QMessageBox.No, defaultButton = QMessageBox.No)
            if ret == QMessageBox.No:
                return

        wallet_password = None
        wallet_filepath = ""
        try:
            has_password = False
            while True:
                wallet_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        "Wallet Password", "Set wallet password:", QLineEdit.Password)
                if result:
                    if not all(ord(char) < 128 for char in wallet_password):
                        QMessageBox.warning(self.new_wallet_ui, \
                            'Wallet Password',\
                                        "Password must contain only ASCII characters")
                        continue

                    confirm_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        'Wallet Password', \
                        "Confirm wallet password:", QLineEdit.Password)
                    if result:
                        if confirm_password != wallet_password:
                            QMessageBox.warning(self.new_wallet_ui, \
                                'Wallet Password',\
                                 "Confirm password does not match password!\
                                                 <br>Please re-enter password")
                        else:
                            has_password = True
                            break
                else:
                    break

            if has_password:
                if not mnemonic_seed: # i.e. create new wallet
                    mnemonic_seed_language = "1" # english
                    seed_language_list = [sl[1] for sl in seed_languages]
                    lang, ok = QInputDialog.getItem(self.new_wallet_ui, "Mnemonic Seed Language",
                                "Select a language for wallet mnemonic seed:",
                                seed_language_list, 1, False)
                    if ok and lang:
                        for sl in seed_languages:
                            if sl[1] == lang:
                                mnemonic_seed_language = sl[0]
                                break
                    else:
                        QMessageBox.warning(self.new_wallet_ui, \
                                    'Mnemonic Seed Language',\
                                     "No language is selected!\
                                     <br>'English' will be used for mnemonic seed")

                self.on_new_wallet_show_progress_event.emit("Restoring wallet..." \
                                        if mnemonic_seed else "Creating wallet...")
                self.app_process_events()
                wallet_filepath = os.path.join(wallet_dir_path, str(uuid.uuid4().hex) + '.bin')
                wallet_log_path = os.path.join(wallet_dir_path, 'ryo-wallet-cli.log')
                resources_path = self.app.property("ResPath")
                if not mnemonic_seed: # i.e. create new wallet
                    self.wallet_cli_manager = WalletCliManager(resources_path, \
                                                wallet_filepath, wallet_log_path)
                    self.wallet_cli_manager.start()
                    self.app_process_events(1)
                    self.wallet_cli_manager.send_command('N')
                    self.app_process_events(0.5)
                    self.wallet_cli_manager.send_command(wallet_password)
                    self.app_process_events(0.5)
                    self.wallet_cli_manager.send_command(mnemonic_seed_language)
#                     self.app_process_events(0.5)
#                     self.wallet_cli_manager.send_command("exit")
                else: # restore wallet
                    self.wallet_cli_manager = WalletCliManager(resources_path, \
                                                               wallet_filepath, wallet_log_path, True, restore_height, mnemonic_seed)
                    self.wallet_cli_manager.start()
                    self.app_process_events(1)
                    self.wallet_cli_manager.send_command(wallet_filepath)
                    #self.app_process_events(0.5)
                    #self.wallet_cli_manager.send_command("Y")
                    #self.app_process_events(1)
                    #self.wallet_cli_manager.send_command(mnemonic_seed)
                    self.app_process_events(1)
                    self.wallet_cli_manager.send_command(wallet_password)
                    self.app_process_events(1)
                    self.wallet_cli_manager.send_command(wallet_password)
                    self.app_process_events(1)
                counter = 0
                while not self.wallet_cli_manager.is_ready():
                    self.app_process_events(1)
                    counter += 1
                    if counter > 10:
                        break
                self.wallet_cli_manager.stop()
        except Exception, err:
            log(str(err), LEVEL_ERROR)
            last_wallet_error = self.wallet_cli_manager.last_error
            error_detailed_text = last_wallet_error if last_wallet_error else str(err)
            self._detail_error_msg("Error Create/Restore Wallet", \
                                       "Error creating/restoring wallet!", \
                                       error_detailed_text)
            self.on_new_wallet_ui_reset_event.emit()
            return

        counter = 0
        while not self._is_wallet_files_existed(wallet_filepath):
            self.app_process_events(1)
            counter += 1
            if counter > 30:
                break

        if self._is_wallet_files_existed(wallet_filepath):
            wallet_address = ''
            if os.path.exists(wallet_filepath + ".address.txt"):
                wallet_address = readFile(wallet_filepath + ".address.txt")
            self.ui.wallet_info.wallet_filepath = wallet_filepath
            self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
            self.ui.wallet_info.wallet_address = wallet_address
            self.ui.wallet_info.is_loaded = True

            self.ui.wallet_info.save()

            self.ui.run_wallet_rpc(wallet_password, 1)
            counter = 0
            block_height = 0

            while not self.ui.wallet_rpc_manager.is_ready():
                self.app_process_events(1)
                h = int(self.ui.wallet_rpc_manager.block_height)
                if h >  block_height:
                    self.on_new_wallet_update_processed_block_height_event.emit(h, self.ui.target_height)
                    counter = 0
                    block_height = h
                if not self.ui.wallet_rpc_manager.is_proc_running():
                    error_detailed_text = self.ui.wallet_rpc_manager.last_error \
                            if self.ui.wallet_rpc_manager.last_error else "Unknown error"
                    self._detail_error_msg("Error Create/Restore Wallet", \
                                       "Error: Unknown error! Wallet RPC appears not to be responding.", \
                                       error_detailed_text)
                    self.ui.reset_wallet(delete_files=False)
                    return
                counter += 1
                if counter > 120:
                    QMessageBox.critical(self.new_wallet_ui, \
                            'Error Creating/Restoring Wallet',\
                            """Error: Unknown error! Wallet RPC appears not to be responding.""")
                    self.ui.reset_wallet(delete_files=False)
                    return

            if wallet_address == '':
                wallet_address = self.ui.wallet_rpc_manager.rpc_request.get_address()
                self.ui.wallet_info.wallet_address = wallet_address["addresses"][0]["address"]
            else:
                self.ui.wallet_info.wallet_address = wallet_address

            self._show_wallet_info()
            self.ui.wallet_info.save()
        else:
            QMessageBox.critical(self.new_wallet_ui, \
                            'Error Creating/Restoring Wallet',\
                            """Error: Wallet files not found!""")
            self.on_new_wallet_ui_reset_event.emit()

    def _is_wallet_files_existed(self, wallet_filepath):
        return os.path.exists(wallet_filepath) and os.path.exists(wallet_filepath + ".keys")

    @Slot()
    def rescan_spent(self):
        self.app_process_events()
        self.ui.wallet_rpc_manager.rpc_request.rescan_spent()

        # refresh wallet_info tx cache
        self.ui.wallet_info.top_tx_height = 0
        self.ui.wallet_info.bc_height = -1
        self.ui.wallet_info.wallet_transfers = []
        self.ui.update_wallet_info()

        self.on_wallet_rescan_spent_completed_event.emit()


    @Slot()
    def rescan_bc(self):
        result = QMessageBox.question(self.ui, "Rescan Blockchain", \
                                  "Rescanning blockchain can take a lot of time.<br><br>Are you sure to proceed?", \
                                   QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if result == QMessageBox.No:
            self.on_wallet_rescan_bc_completed_event.emit()
            return

        self.app_process_events()
        self.ui.wallet_rpc_manager.rpc_request.rescan_bc()

        # refresh wallet_info tx cache
        self.ui.wallet_info.top_tx_height = 0
        self.ui.wallet_info.bc_height = -1
        self.ui.wallet_info.wallet_transfers = []
        self.ui.update_wallet_info()

        self.on_wallet_rescan_bc_completed_event.emit()


    @Slot(float, str, str, int, int, str, bool, bool)
    def send_tx(self, amount, address, payment_id, priority, mixin, tx_desc, save_address, sweep_all):
        if not payment_id and not address.startswith("Sumi"):
            result = QMessageBox.question(self.ui, "Sending Coins Without Payment ID?", \
                                      "Are you sure to send coins without Payment ID?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
            if result == QMessageBox.No:
                self.on_wallet_send_tx_completed_event.emit('{"status": "CANCELLED", "message": "Sending coin cancelled"}')
                return

        if sweep_all:
            result = QMessageBox.question(self.ui, "Sending all your coins?", \
                                      "This will send all your coins to target address.<br><br>Are you sure you want to proceed?", \
                                      QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
            if result == QMessageBox.No:
                self.on_wallet_send_tx_completed_event.emit('{"status": "CANCELLED", "message": "Sending coin cancelled"}')
                return

        if self.ui.wallet_info.wallet_password:
            wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)
        else:
            wallet_password = ''
            result = True

        if not result:
            self.on_wallet_send_tx_completed_event.emit('{"status": "CANCELLED", "message": "Wrong wallet password"}');
            return

        if self.ui.wallet_info.wallet_password and hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            self.on_wallet_send_tx_completed_event.emit('{"status": "CANCELLED", "message": "Wrong wallet password"}');
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        amount = int(amount*COIN)

        if sweep_all:
            _, _, per_subaddress = self.ui.wallet_rpc_manager.rpc_request.get_balance()
            subaddr_indices = []
            for s in per_subaddress:
                if s['unlocked_balance'] > 0:
                    subaddr_indices.append(s['address_index'])
            ret = self.ui.wallet_rpc_manager.rpc_request.transfer_all(address, payment_id, priority, mixin, 0, subaddr_indices)
        else:
            ret = self.ui.wallet_rpc_manager.rpc_request.transfer_split(amount, \
                                                address, payment_id, priority, mixin)

        if ret['status'] == "ERROR":
            self.on_wallet_send_tx_completed_event.emit(json.dumps(ret));
            self.app_process_events()
            if ret['message'] == "tx not possible":
                msg = "Not possible to send coins. Probably, there is not enough money left for fee."
            else:
                msg = ret['message']

            QMessageBox.critical(self.ui, \
                            'Error Sending Coins',\
                            "<b>ERROR</b><br><br>" + msg)

        if ret['status'] == "OK":
            if tx_desc:
                # set the same note for all txs:
                notes = []
                for i in range(len(ret['tx_hash_list'])):
                    notes.append(tx_desc)
                self.ui.wallet_rpc_manager.rpc_request.set_tx_notes(ret['tx_hash_list'], notes)

            self.on_wallet_send_tx_completed_event.emit(json.dumps(ret));
            self.app_process_events()

            msg = "<b>Coins successfully sent in the following transaction(s):</b><br><br>"
            for i in range(len(ret['tx_hash_list'])):
                if sweep_all:
                    msg += "- Transaction ID: %s <br>" % (ret['tx_hash_list'][i])
                else:
                    msg += "- Transaction ID: %s <br>  - Amount: %s <br>  - Fee: %s <br><br>" % (ret['tx_hash_list'][i], \
                                                        print_money2(ret['amount_list'][i]), \
                                                        print_money2(ret['fee_list'][i]))
            QMessageBox.information(self.ui, 'Coins Sent', msg)
            self.ui.update_wallet_info()

            if save_address:
                desc, _ = self._custom_input_dialog(self.ui, \
                        'Saving Address...', \
                        "Address description/note (optional):")
                ret = self.ui.wallet_rpc_manager.rpc_request.add_address_book(address, \
                                                                              payment_id, desc)
                if ret['status'] == "OK":
                    if self.ui.wallet_info.wallet_address_book:
                        address_entry = {"address": address,
                                     "payment_id": payment_id,
                                     "description": desc[0:200],
                                     "index": ret["index"]
                                     }
                        self.ui.wallet_info.wallet_address_book.append(address_entry)

                    QMessageBox.information(self.ui, "Address Saved", \
                                            "Address (and payment ID) saved to address book.")


    @Slot(int)
    def generate_payment_id(self, hex_length=16):
        payment_id = binascii.b2a_hex(os.urandom(hex_length/2))
        integrated_address = self.ui.wallet_rpc_manager.rpc_request.make_integrated_address(payment_id)["integrated_address"]
        self.on_generate_payment_id_event.emit(payment_id, integrated_address);


    @Slot(str)
    def copy_text(self, text):
        QApplication.clipboard().setText(text)


    @Slot()
    def load_address_book(self):
        if not self.ui.wallet_info.wallet_address_book:
            address_book = []
            ret = self.ui.wallet_rpc_manager.rpc_request.get_address_book()
            if ret['status'] == "OK" and "entries" in ret:
                address_book = ret["entries"]
            self.ui.wallet_info.wallet_address_book = address_book

        self.on_load_address_book_completed_event.emit( json.dumps(self.ui.wallet_info.wallet_address_book) )

    @Slot(int)
    def delete_address_book(self, index):
        result = QMessageBox.question(self.ui, "Delete Address Book Entry", \
                                      "Are you sure to delete this address?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if result == QMessageBox.Yes:
            ret = self.ui.wallet_rpc_manager.rpc_request.delete_address_book(index)
            if ret['status'] == "OK":
                address_book = self.ui.wallet_info.wallet_address_book
                for i in range(len(address_book)):
                    if address_book[i]['index'] == index:
                        address_book.pop(i)
                        break
        self.load_address_book()


    def _find_tx(self, transfers, tx_id, bc_height):
        if transfers["status"] == "OK":
            if "out" in transfers:
                for tx in transfers["out"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "out"
                        tx["status"] = "out"
                        tx["confirmation"] = bc_height - tx["height"] if bc_height > tx["height"] else 0
                        return tx

            if "in" in transfers:
                for tx in transfers["in"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "in"
                        tx["status"] = "in"
                        tx["confirmation"] = bc_height - tx["height"] if bc_height > tx["height"] else 0
                        return tx

            if "pending" in transfers:
                for tx in transfers["pending"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "out"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        return tx

            if "pool" in transfers:
                for tx in transfers["pool"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "in"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        return tx
        return None

    @Slot(int, str)
    def view_tx_detail(self, height, tx_id):
        if height > 0:
            transfers = self.ui.wallet_rpc_manager.rpc_request.get_transfers(filter_by_height=True, min_height=height-1, max_height=height)
        else:
            transfers = self.ui.wallet_rpc_manager.rpc_request.get_transfers(tx_pending=True, tx_in_pool=True)

        tx = self._find_tx(transfers, tx_id, self.ui.target_height)
        if not tx:
            self.on_tx_detail_found_event.emit('{"status": "ERROR"}')
            QMessageBox.warning(self.ui, "Transaction Details", "Transaction id: %s <br><br>not found!" % tx_id)
            return

        self.on_tx_detail_found_event.emit( json.dumps(tx) )


    @Slot(int)
    def load_tx_history(self, current_page=0):
        if current_page <= 0: current_page = 1
        txs_per_page = 10
        tx_start_index = (current_page - 1)*txs_per_page
        all_txs = self.ui.wallet_info.wallet_pending_transfers + self.ui.wallet_info.wallet_transfers
        txs = all_txs[tx_start_index:tx_start_index + txs_per_page]
        for tx in txs:
            tx["confirmation"] = self.ui.target_height - tx["height"] \
                if self.ui.target_height > tx["height"] and tx["height"] > 0 else 0

        num_of_pages = int(len(all_txs) + txs_per_page - 1)/txs_per_page
        pagination_slots = 10
        start_page = (int(current_page - 1)/pagination_slots)*pagination_slots + 1
        end_page = start_page + (pagination_slots - 1) \
                if start_page + (pagination_slots - 1) < num_of_pages else num_of_pages
        ret = {"txs": txs,
               "current_page": current_page,
               "num_of_pages": num_of_pages,
               "start_page": start_page,
               "end_page": end_page}

        self.on_load_tx_history_completed_event.emit( json.dumps(ret) );


    @Slot()
    def open_new_wallet(self):
        result = QMessageBox.question(self.ui, "Open/Create New Wallet", \
                                      "<b>This will close current wallet and open/create new wallet!</b><br><br>Are you sure to continue?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if result == QMessageBox.No:
            return

        if self.ui.wallet_info.wallet_password:
            wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)
        else:
            wallet_password = ''
            result = True

        if not result:
            return

        if self.ui.wallet_info.wallet_password and hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        self.ui.show_new_wallet_ui()


    @Slot(str)
    def view_wallet_key(self, key_type):
        if self.ui.wallet_info.wallet_password:
            wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)
        else:
            wallet_password = ''
            result = True

        if not result:
            self.on_view_wallet_key_completed_event.emit("", "");
            return

        if self.ui.wallet_info.wallet_password and hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            self.on_view_wallet_key_completed_event.emit("", "");
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        ret = self.ui.wallet_rpc_manager.rpc_request.query_key(key_type)
        title = "Wallet Key"
        if key_type == "mnemonic":
            title = "Wallet mnemonic seed"
        if key_type == "view_key":
            title = "Wallet view-key"
        if key_type == "spend_key":
            title = "Wallet spend-key"

        self.on_view_wallet_key_completed_event.emit(title, ret)


    @Slot(int)
    def set_daemon_log_level(self, level):
        # save log level
        self.ui.app_settings.settings['daemon']['log_level'] = level
        self.ui.app_settings.save()


    @Slot(int)
    def set_block_sync_size(self, sync_size):
        self.ui.app_settings.settings['daemon']['block_sync_size'] = sync_size
        self.ui.app_settings.save()

    @Slot()
    def load_app_settings(self):
        self.on_load_app_settings_completed_event.emit( json.dumps(self.ui.app_settings.settings) )

    @Slot()
    def quick_load_ui_settings(self):
        self.on_quick_load_ui_settings_completed_event.emit( json.dumps(self.ui.app_settings.settings) )

    @Slot()
    def about_app(self):
        self.ui.about()

    @Slot(str)
    def open_link(self, link):
        webbrowser.open(link)

    @Slot()
    def restart_daemon(self):
        self.app_process_events(1)
        self.ui.sumokoind_daemon_manager.stop()
        self.ui.start_deamon()
        self.app_process_events(5)
        self.on_restart_daemon_completed_event.emit()

    @Slot()
    def pop_blocks(self):
        while True:
            no_blocks, result = self._custom_input_dialog(self.ui, \
                                "Pop Blocks", "Enter number of blocks to pop:",
                                QLineEdit.Normal, QInputDialog.TextInput, "1000")
            if result:
                if not no_blocks.isdigit():
                    QMessageBox.warning(self.ui, \
                            "Pop Blocks",\
                            "Value must contain numbers only")
                else:
                    break
            else:
                self.on_pop_blocks_completed_event.emit()
                return False

        self.app_process_events(1)
        self.ui.sumokoind_daemon_manager.stop()
        pop_blocks(no_blocks)
        self.ui.start_deamon()
        self.app_process_events(5)
        self.on_pop_blocks_completed_event.emit()


    @Slot()
    def view_daemon_log(self):
        log_file = os.path.join(DATA_DIR, 'logs', "ryod.log")
        log_dialog = LogViewer(parent=self.ui, log_file=log_file)
        log_dialog.load_log()


    @Slot(str)
    def copy_seed(self, seed):
        self.copy_text(seed)
        QMessageBox.information(self.new_wallet_ui, "Wallet Mnemonic Seed Copied", \
                            """Wallet mnemonic seed words have been copied!<br><br>
                            Please save them to a safe place for wallet restoration<br>
                            in case you forget wallet password or computer failure etc.""")

    @Slot()
    def paste_seed_words(self):
        text = QApplication.clipboard().text()
        self.on_paste_seed_words_event.emit(text)

    @Slot()
    def update_wallet_loading_height(self):
        if self.ui.wallet_rpc_manager is None:
            return

        h = int(self.ui.wallet_rpc_manager.block_height)
        if h > self.current_block_height:
            self.on_update_wallet_loading_height_event.emit(h, self.ui.target_height)
            self.current_block_height = h


    def update_daemon_status(self, status):
        self.on_daemon_update_status_event.emit(status)


    def app_process_events(self, seconds=1):
        for _ in range(int(seconds*10)):
            self.app.processEvents()
            sleep(.1)



    def _detail_error_msg(self, title, error_text, error_detailed_text):
        msg = QMessageBox(self.new_wallet_ui)
        msg.setWindowTitle(title)
        msg.setText(error_text)
        msg.setInformativeText("Detailed error information below:")
        msg.setDetailedText(error_detailed_text)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def _custom_input_dialog(self, ui, title, label,
                             text_echo_mode=QLineEdit.Normal,
                             input_mode=QInputDialog.TextInput,
                             default_value=''):
        dlg = QInputDialog(ui)
        dlg.setTextEchoMode(text_echo_mode)
        dlg.setInputMode(input_mode)
        dlg.setWindowTitle(title)
        dlg.setTextValue(default_value)
        dlg.setLabelText(label)
        dlg.resize(250, 100)
        result = dlg.exec_()
        text = dlg.textValue()
        return (text, result)


    def _show_wallet_info(self):
        wallet_rpc_request = self.ui.wallet_rpc_manager.rpc_request
        wallet_info = {}
        wallet_info['address'] = self.ui.wallet_info.wallet_address
        wallet_info['seed'] = wallet_rpc_request.query_key(key_type="mnemonic")
        wallet_info['view_key'] = wallet_rpc_request.query_key(key_type="view_key")
        balance, unlocked_balance, _ = wallet_rpc_request.get_balance()
        wallet_info['balance'] = print_money(balance)
        wallet_info['unlocked_balance'] = print_money(unlocked_balance)

        self.on_new_wallet_show_info_event.emit(json.dumps(wallet_info))


    @Slot(bool)
    def set_dark_mode(self, is_dark_mode):
        self.ui.app_settings.settings['gui']['dark_mode'] = is_dark_mode
        self.ui.app_settings.save()
        self.ui.toggleDarkQT()


    on_new_wallet_show_info_event = Signal(str)
    on_new_wallet_show_progress_event = Signal(str)
    on_new_wallet_ui_reset_event = Signal()
    on_new_wallet_update_processed_block_height_event = Signal(int, int)

    on_daemon_update_status_event = Signal(str)
    on_main_wallet_ui_reset_event = Signal()
    on_wallet_update_info_event = Signal(str)
    on_wallet_rescan_spent_completed_event = Signal()
    on_wallet_rescan_bc_completed_event = Signal()
    on_wallet_send_tx_completed_event = Signal(str)
    on_generate_payment_id_event = Signal(str, str)
    on_load_address_book_completed_event = Signal(str)
    on_tx_detail_found_event = Signal(str)
    on_load_tx_history_completed_event = Signal(str)
    on_view_wallet_key_completed_event = Signal(str, str)
    on_load_app_settings_completed_event = Signal(str)
    on_quick_load_ui_settings_completed_event = Signal(str)
    on_restart_daemon_completed_event = Signal()
    on_pop_blocks_completed_event = Signal()
    on_paste_seed_words_event = Signal(str)
    on_update_wallet_loading_height_event = Signal(int, int)
