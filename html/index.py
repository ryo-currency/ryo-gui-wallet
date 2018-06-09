#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
Main UI html
'''

html ="""
<!DOCTYPE html>
<html>
    <head>
        <link href="./css/bootstrap.min.css" rel="stylesheet">
        <link href="./css/structure.css" rel="stylesheet">
        <link href="./css/light-theme.css" rel="stylesheet">
        <link href="./css/dark-theme.css" rel="stylesheet">
        <link href="./css/font-awesome.min.css" rel="stylesheet">
        
        <script src="./scripts/jquery-1.9.1.min.js"></script>
        <script src="./scripts/bootstrap.min.js"></script>
        <script src="./scripts/mustache.min.js"></script>
        <script src="./scripts/jquery.qrcode.min.js"></script>
        <script src="./scripts/utils.js"></script>
        <script src="./scripts/main.js"></script>

    </head>
    <body>
        <div class="container">
            <ul class="nav nav-tabs">
              <li><a data-toggle="tab" href="#receive_tab"><i class="fa fa-arrow-circle-o-down"></i> Receive</a></li>
              <li class="active"><a data-toggle="tab" href="#balance_tab"><i class="fa fa-money"></i> Wallet</a></li>
              <li><a data-toggle="tab" href="#send_tab"><i class="fa fa-send-o"></i> Send</a></li>
              <li><a data-toggle="tab" href="#tx_history_tab"><i class="fa fa-history"></i> TX History</a></li>
              <li><a data-toggle="tab" href="#settings_tab"><i class="fa fa-cogs"></i> Settings</a></li>
            </ul>
            <div class="tab-content">
                <div id="receive_tab" class="tab-pane fade">
                    <h3>RECEIVE</h3>
                    <form id="form_receive" class="form-horizontal">
                        <div class="form-group">
                            <div class="col-sm-12">
                                <label for="receive_address" class="col-label control-label">Main Address</label>
                                <div class="col-field input-group">
                                    <input id="receive_address" type="text" class="form-control" style="font-weight: bold" maxlength="64" readonly />
                                    <span class="input-group-btn">
                                        <button id="btn_copy_address" class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="copy_address()" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                                        <button id="btn_qr_address" class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="qr_address()" title="Show QR code"><i class="fa fa-qrcode"></i></button>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </form>
                    <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true" style="margin-left: 15px; margin-right: 15px;">
                        <div class="panel panel-default">
                          <div class="panel-heading" role="tab" id="headingOne">
                            <h4 class="panel-title">
                            <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
                              Used Addresses
                            </a>
                          </h4>
                          </div>
                          <div id="collapseOne" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingOne">
                            <div class="panel-body">
                                <div class="table-responsive">
                                    <table id="table_used_subaddresses" class="table table-hover table-striped table-condensed" style="table-layout: fixed;">
                                        <thead>
                                            <tr>
                                                <th>Address</th>
                                                <th style="text-align: right; width: 100px">Balance</th>
                                                <th style="text-align: right; width: 100px">Unlocked</th>
                                                <th style="text-align: right; width: 50px">Index</th>
                                                <th style="width: 80px">&nbsp;</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                          </div>
                        </div>
                        <div class="panel panel-default">
                          <div class="panel-heading" role="tab" id="headingTwo">
                            <h4 class="panel-title">
                            <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">
                              New (Ghost) Addresses
                            </a>
                          </h4>
                          </div>
                          <div id="collapseTwo" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingTwo">
                            <div class="panel-body" style="overflow: auto">
                                <div class="table-responsive">
                                    <table id="table_new_subaddresses" class="table table-hover table-striped table-condensed" style="table-layout: fixed">
                                        <thead>
                                            <tr>
                                                <th>Address</th>
                                                <th style="text-align: right; width: 50px;">Index</th>
                                                <th style="width: 80px;">&nbsp;</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                          </div>
                        </div>
                    </div>
                </div>
                <div id="balance_tab" class="tab-pane fade in active">
                    <h3>BALANCE</h3>
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="col-xs-6">
                                <h5><i class="fa fa-fw fa-balance-scale"></i> Balance:</h5>
                                <h5><i class="fa fa-fw fa-unlock"></i> Unlocked Balance:</h5>
                            </div>
                            <div class="col-xs-6" style="text-align:right">
                                <h5><span id="balance">0.000000000</span> <small>RYO</small> <span class="syncing"> (syncing)</span></h5>
                                <h5><span id="unlocked_balance">0.000000000</span> <small>RYO</small> <span class="syncing"> (syncing)</span></h5>
                            </div>
                            <div class="col-xs-12" style="margin-top: 10px">
                                <button id="btn_rescan_spent" type="button" class="btn btn-primary" onclick="rescan_spent()" disabled><i class="fa fa-sort-amount-desc"></i> Rescan Spent</button>
                                <button id="btn_rescan_bc" type="button" class="btn btn-primary" style="margin-left: 20px;" onclick="rescan_bc()" disabled><i class="fa fa-repeat"></i> Rescan Blockchain</button>
                            </div>
                        </div>
                    </div>
                    <hr style="margin-top:20px;margin-bottom:10px;">
                    <h3>RECENT TRANSACTIONS</h3>
                    <div class="row" id="recent_txs">
                       <h4 class="tx-none-found">NO TRANSACTIONS FOUND</h4>
                    </div>
                </div>
                <div id="send_tab" class="tab-pane fade">
                    <h3>SEND</h3>
                    <form id="form_send_tx" class="form-horizontal">
                        <fieldset>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_amount" class="col-label control-label">Amount</label>
                                    <div class="col-field input-group">
                                        <input id="send_amount" type="text" class="form-control" placeholder="0.0" maxlength="255"/>
                                        <span class="input-group-btn">
                                            <button id="btn_fill_all_money" class="btn btn-primary btn-sm"  style="text-transform: none" type="button" tabindex="-1" onclick="fill_all_money()" disabled>All coins</button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_address" class="col-label control-label">Address</label>
                                    <div class="col-field input-group">
                                        <input id="send_address" type="text" class="form-control"  placeholder="Paste receiving address here (Ctrl+V)..." maxlength="110"/>
                                        <span class="input-group-btn">
                                            <button class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="show_address_book()">
                                                <i class="fa fa-address-book"></i> Address book...
                                            </button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_payment_id" class="col-label control-label">Payment ID</label>
                                    <div class="col-field">
                                        <input id="send_payment_id" type="text" class="form-control"  placeholder="Paste payment ID here (Ctrl+V, optional)..." maxlength="64"/>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_tx_desc" class="col-label control-label">Description</label>
                                    <div class="col-field">
                                        <input id="send_tx_desc" type="text" class="form-control"  placeholder="Tx description, saved to local wallet history (optional)..." maxlength="255"/>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group max-width">
                                <div class="col-sm-6">
                                    <label for="send_mixins" class="col-label control-label">Privacy <sup>1</sup></label>
                                    <div class="col-field col-xs-8">
                                        <select id="send_mixins" class="form-control">
                                          <option value="12" selected>12 mixins (default)</option>
                                          <option value="15">15 mixins</option>
                                          <option value="18">18 mixins</option>
                                          <option value="24">24 mixins</option>
                                          <option value="36">36 mixins</option>
                                          <option value="48">48 mixins</option>
                                          <option value="60">60 mixins</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <label for="send_priority" class="col-xs-4 control-label">Priority <sup>2</sup></label>
                                    <div class="col-xs-8">
                                        <select id="send_priority" class="form-control">
                                          <option value="1" selected>Normal (x1 fee)</option>
                                          <option value="2">High (x2 fee)</option>
                                          <option value="4">Higher (x4 fee)</option>
                                          <option value="20">Elevated (x20 fee)</option>
                                          <option value="166">Forceful (x166 fee)</option>
                                        </select>
                                       <!--<input id="send_fee_level_slider" type="text"/>--> 
                                    </div>
                                </div>
                            </div>
                             <div class="form-group max-width">
                                <div class="col-sm-12">
                                    <label class="col-label control-label sr-only">&nbsp;</label>
                                    <div class="col-field col-xs-10">
                                        <input id="checkbox_save_address" type="checkbox" /> <label for="checkbox_save_address">Save address (with payment id) to address book</label>
                                        <label><small>1. Higher mixin (ringsize) means higher transaction cost, using default mixin# (12) is recommended</small></label>
                                        <label><small>2. Only choose higher priority when there are many transactions in tx pool or "Normal" works just fine</small></label>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12 text-center">
                                    <button id="btn_send_tx" type="button" class="btn btn-success" onclick="send_tx()" disabled><i class="fa fa-send"></i> Send</button>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                </div>
                <div id="tx_history_tab" class="tab-pane fade">
                    <div class="table-responsive">
                        <table id="table_tx_history" style="table-layout:fixed" class="table table-hover table-striped table-condensed">
                            <thead>
                                <tr>
                                    <th style="width:30px;" align="center">?</th>
                                    <th style="width:30px;" align="center">I/O</th>
                                    <th style="width:150px;">Date/Time</th>
                                    <th style="width:99%;">Tx ID</th>
                                    <th style="width:140px;">Payment ID</th>
                                    <th style="width:90px;">Amount</th>
                                    <th style="width:80px;">&nbsp;</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="7" style="text-align: center">
                                        <nav aria-label="Page navigation">
                                            <ul id="tx_history_pages" class="pagination pagination-sm" style="margin: 5px 0;">
                                            </ul>
                                        </nav>
                                    <td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
                <div id="settings_tab" class="tab-pane fade">
                    <h3>WALLET</h3>
                    <div class="row">
                        <div class="col-sm-12 wallet-settings">
                            <button id="btn_new_wallet" type="button" class="btn btn-primary" onclick="open_new_wallet()"><i class="fa fa-file"></i> New Wallet...</button>
                            <button id="btn_view_seed" type="button" class="btn btn-primary" onclick="view_wallet_key('mnemonic')"><i class="fa fa-eye"></i> Mnemonic Seed...</button>
                            <button id="btn_view_viewkey" type="button" class="btn btn-primary" onclick="view_wallet_key('view_key')"><i class="fa fa-key"></i> Viewkey...</button>
                            <button id="btn_view_spendkey" type="button" class="btn btn-primary" onclick="view_wallet_key('spend_key')"><i class="fa fa-key"></i> Spendkey...</button>
                        </div>
                    </div>
                    <hr style="margin-top:20px;margin-bottom:10px;">
                    <h3>DAEMON</h3>
                    <div class="row">
                        <div class="max-width col-centered">
                            <div class="col-sm-5">
                                <form class="form-horizontal">
                                    <div class="form-group">
                                        <label class="col-xs-4 control-label">Log level:</label>
                                        <div class="col-xs-8">
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_0" value="0" onclick="set_daemon_log_level(0)" checked="">
                                                Level 0 (default)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_1" value="1" onclick="set_daemon_log_level(1)">
                                                Level 1
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_2" value="2" onclick="set_daemon_log_level(2)">
                                                Level 2
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_3" value="3" onclick="set_daemon_log_level(3)">
                                                Level 3
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_4" value="4" onclick="set_daemon_log_level(4)">
                                                Level 4
                                              </label>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="col-sm-7">
                                <form class="form-horizontal">
                                    <div class="form-group">
                                        <label class="col-xs-4 control-label">Block sync size:</label>
                                        <div class="col-xs-8">
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_10" value="10" onclick="set_block_sync_size(10)" checked="">
                                                10 (default, for slow network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_20" value="20" onclick="set_block_sync_size(20)">
                                                20 (for normal network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_50" value="50" onclick="set_block_sync_size(50)">
                                                50 (for good network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_100" value="100" onclick="set_block_sync_size(100)">
                                                100 (for better network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_200" value="200" onclick="set_block_sync_size(200)">
                                                200 (for great network)
                                              </label>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="col-sm-12 wallet-settings" style="margin-top: 10px; text-align:center;">
                                <button id="btn_pop_blocks" type="button" class="btn btn-primary" onclick="pop_blocks()"><i class="fa fa-square"></i> Pop Blocks</button>
                                <button id="btn_restart_daemon" type="button" class="btn btn-primary" onclick="restart_daemon()"><i class="fa fa-refresh"></i> Restart Daemon</button>
                                <button id="btn_view_log" type="button" class="btn btn-primary" onclick="app_hub.view_daemon_log()"><i class="fa fa-file"></i> View Log...</button>
                            </div>
                        </div>
                    </div>
                    <hr style="margin-top:10px;margin-bottom:10px;">
                    <div class="row">
                        <div class="col-sm-12 wallet-settings" style="margin-top: 10px;text-align: center">
                            <button id="btn_about" type="button" class="btn btn-primary" onclick="about_app()"><i class="fa fa-user"></i> About</button>
                            <button id="btn_dark_mode" type="button" class="btn btn-primary" onclick="toggle_dark_mode()">
                                <i class="fa fa-adjust"></i>
                                <span class="show-on-dark-mode">Light Mode</span>
                                <span class="show-on-light-mode">Dark Mode</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="progress" role="application">
                <div id="progress_bar" class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width:1%;">
                    <span id="progress_bar_text_high"></span>
                </div>
                <span id="progress_bar_text_low"><i class="fa fa-flash"></i>&nbsp;&nbsp;Connecting to network...</span>
            </div>
        </div>
        
        <div class="modal" id="app_modal_dialog" style="z-index: 100000;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body" id="app_model_body"></div>
                    <div class="modal-footer">
                        <button id="btn_copy" type="button" class="btn btn-primary" onclick="copy_dialog_content()">Copy</button>
                        <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal" id="sending_modal_progress" style="z-index: 100001;" data-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <p><i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i><span id="sending_modal_progress_text" class="modal-progress-text"></span></p>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal" id="app_modal_progress" style="z-index: 100002;" data-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <p><span id="app_modal_progress_text" class="modal-progress-text"></span><p>
                        <!--<p style="text-align: center"><img src="./images/ajax-loader2.gif"/></p>-->
                        <p style="text-align: center"><i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i></p>
                        <div id="app_modal_progress_subtext" class="modal-progress-subtext"> </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal" id="qrcode_dialog" style="z-index: 100003;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" style="text-align:center" id="qrcode_dialog_body"></div>
                    <div class="modal-footer">
                        
                    </div>
                </div>
            </div>
        </div>
        
        <script id="recent_tx_row_templ" type="x-tmpl-mustache">
            <div class="col-sm-12">
                <div class="col-xs-10" style="padding-right:0">
                    <p class="tx-list tx-{{cls_in_out}}"><i class="fa fa-{{ tx_fa_icon }}"></i> ({{tx_direction}}) <span class="tx-list txid"><a href="javascript:open_link('http://explorer.ryo-currency.com/tx/{{ tx_id }}')" title="View on blockchain explorer">{{ tx_id }}</a></span></p>
                    Payment ID: <span class="tx-list tx-payment-id">{{ tx_payment_id }}</span><br/>
                    Height: <span class="tx-list tx-height">{{ tx_height }}</span>  Date: <span class="tx-list tx-date">{{ tx_date }}</span> Time: <span class="tx-list tx-time">{{ tx_time }}</span> Status: <span class="tx-list tx-status">{{ tx_status }}</span><br/>
                    <p style="font-size:140%">Amount: <span class="tx-list tx-{{cls_in_out}} tx-amount {{tx_lock_cls}}">{{{tx_lock_icon}}}{{ tx_amount }}</span> <span class="{{ tx_fee_hide }}">Fee:</span> <span class="tx-list tx-{{cls_in_out}} tx-fee {{ tx_fee_hide }}">{{ tx_fee }}</span></p> 
                </div>
                <div class="col-xs-2">
                    <button class="btn btn-warning" onclick="view_tx_detail('{{ tx_height }}', '{{ tx_id }}')">Details</button>
                </div>
                <br clear="both"/>
            </div>
        </script>
        
        <script id="tx_detail_templ" type="x-tmpl-mustache">
            <p class="tx-list tx-{{cls_in_out}}" style="font-size: 90%"><i class="fa fa-{{ tx_fa_icon }}"></i> {{tx_direction}}<br>
                <span class="tx-list txid"><a href="javascript:open_link('http://explorer.ryo-currency.com/tx/{{ tx_id }}')" title="View on blockchain explorer">{{ tx_id }}</a></span>
            </p>
            <ul style="font-size: 90%">
                <li>Payment ID: <span class="tx-list tx-payment-id">{{ tx_payment_id }}</span></li>
                <li>Height: <span class="tx-list tx-height">{{ tx_height }}</span>  Date: <span class="tx-list tx-date">{{ tx_date }}</span> Time: <span class="tx-list tx-time">{{ tx_time }}</span></li>
                <li>Status: <span class="tx-list tx-status">{{ tx_status }}</span></li>
                <li>Amount: <span class="tx-list tx-{{cls_in_out}} tx-amount {{tx_lock_cls}}">{{{tx_lock_icon}}}{{ tx_amount }}</span> <span class="{{ tx_fee_hide }}">Fee:</span> <span class="tx-list tx-{{cls_in_out}} tx-fee {{ tx_fee_hide }}">{{ tx_fee }}</span></li>
                <li class="{{ tx_note_hide }}">Tx Note: <span class="tx-list tx-note">{{ tx_note }}</span></li>
            </ul>
            <div class="tx-destinations {{ tx_destinations_hide }}">
                <span style="margin-left:10px;">Destination(s):</span>
                <ul>
                    {{{ tx_destinations }}}
                </ul>
            </div>
        </script>
        
        <script id="address_book_row_templ" type="x-tmpl-mustache">
            <tr>
                <td class="address-book-row ellipsis monospace" data-address="{{ address }}" data-payment-id="{{ payment_id }}"><a href="#" title="{{ address }}">{{ address }}</a></td>
                <td class="address-book-row ellipsis monospace" data-address="{{ address }}" data-payment-id="{{ payment_id }}">{{ payment_id_short }}</a></td>
                <td class="address-book-row ellipsis monospace" data-address="{{ address }}" data-payment-id="{{ payment_id }}">{{ desc_short }}</a></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="delete_address({{ index }})" title="Delete from address book"><i class="fa fa-trash"></i></button>
                    <button class="btn btn-primary btn-sm address-book-row" tabindex="-1" data-address="{{ address }}" data-payment-id="{{ payment_id }}" title="Send to this address"><i class="fa fa-copy"></i></button>
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="show_qrcode('{{ address }}')" title="Show QR code"><i class="fa fa-qrcode"></i></button>    
                </td>
            </tr>
        </script>
        
        <script id="tx_history_row" type="x-tmpl-mustache">
            <tr class="tx-list tx-{{ cls_in_out }}" style="font-weight: normal;">
                <td>{{{ tx_status }}}</td>
                <td>{{{ tx_direction }}}</td>
                <td class="ellipsis monospace">{{ tx_date_time }}</td>
                <td class="ellipsis monospace">{{ tx_id }}</td>
                <td class="ellipsis monospace">{{ tx_payment_id }}</td>
                <td class="ellipsis monospace">{{ tx_amount }}</td>
                <td><button class="btn btn-default btn-sm" onclick="view_tx_detail('{{ tx_height }}', '{{ tx_id }}')">Details</button></td>
            </tr>
        </script>
        
        <script id="tx_history_page_tmpl" type="x-tmpl-mustache">
            <li class="{{ page_prev_disabled }}">
                <a href="javascript:load_tx_history({{ prev_page }})" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
            {{{ page_html }}}
            <li class="{{ page_next_disabled }}">
                <a href="javascript:load_tx_history({{ next_page }})" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        </script>
        
        <script id="new_subaddress_row_tmpl" type="x-tmpl-mustache">
            <tr class="" style="font-weight: normal;">
                <td class="ellipsis monospace">{{ address }}</td>
                <td align="right">{{ address_index }}</td>
                <td align="right">
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="copy_subaddress(this, '{{ address }}')" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="show_qrcode('{{ address }}')" title="Show QR code"><i class="fa fa-qrcode"></i></button>    
                </td>
            </tr>
        </script>
        
        <script id="used_subaddress_row_tmpl" type="x-tmpl-mustache">
            <tr class="" style="font-weight:{{ row_font_weight }};">
                <td class="ellipsis monospace">{{ address }}</td>
                <td align="right">{{ balance }}</td>
                <td align="right">{{ unlocked_balance }}</td>
                <td align="right">{{ address_index }}</td>
                <td align="right">
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="copy_subaddress(this, '{{ address }}')" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="show_qrcode('{{ address }}')" title="Show QR code"><i class="fa fa-qrcode"></i></button>    
                </td>
            </tr>
        </script>
    </body>
</html>
"""
