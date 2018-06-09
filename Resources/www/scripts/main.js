function app_ready(){

    $(document).ready(function(){
        /* 
         * To not make the UI show light when preference is set to dark mode, we are going
         * to load the app settings without a timeout. Because the 2000ms delay is there
         * for a reason, we will also re-apply any settings in the below callback as well
         */
        app_hub.on_quick_load_ui_settings_completed_event.connect(function(app_settings_json){
            var app_settings = $.parseJSON(app_settings_json);
            var is_dark_mode = app_settings['gui']['dark_mode'];
            if(is_dark_mode) {
                $('body').addClass('dark-theme');
            }
        });
        app_hub.quick_load_ui_settings()
    });

    setTimeout(app_hub.load_app_settings, 2000);
    app_hub.on_load_app_settings_completed_event.connect(function(app_settings_json){
        var app_settings = $.parseJSON(app_settings_json);
        var log_level = app_settings['daemon']['log_level'];
        $('#daemon_log_level_' + log_level).prop('checked', true);
        var block_sync_size = app_settings['daemon']['block_sync_size'];
        $('#block_sync_size_' + block_sync_size).prop('checked', true);
        var is_dark_mode = app_settings['gui']['dark_mode'];
        if(is_dark_mode) {
            $('body').addClass('dark-theme');
        }
    });
    
    app_hub.on_main_wallet_ui_reset_event.connect(function(){
        setTimeout(function(){
            location.reload();
        }, 5000);
    });
    
    app_hub.on_daemon_update_status_event.connect(update_daemon_status);
    app_hub.on_wallet_update_info_event.connect(update_wallet_info);
    app_hub.on_wallet_rescan_spent_completed_event.connect(function(){
        rescan_spent_btn.disable(false);
        rescan_bc_btn.disable(false);
        hide_progress();
    });
    
    app_hub.on_wallet_rescan_bc_completed_event.connect(function(){
        rescan_spent_btn.disable(false);
        rescan_bc_btn.disable(false);
        hide_progress();
    });
    
    app_hub.on_wallet_send_tx_completed_event.connect(function(status_json){
        var status = $.parseJSON(status_json);
        if(status['status'] == "OK"){
            $("#form_send_tx")[0].reset();
        }
        else{
            if(status['message'].search("Invalid address format") >= 0){
                $('#send_address').parent().addClass('has-error');
            }
            else if(status['message'].search("Payment id has invalid format") >= 0){
                $('#send_payment_id').parent().addClass('has-error');
            }
            else if(status['message'].search("not enough money") >= 0){
                $('#send_amount').parent().addClass('has-error');
            }
        }
        
        btn_send_tx.disable(false);
        hide_progress();
    });
    
    app_hub.on_generate_payment_id_event.connect(function(payment_id, integrated_address){
        $('#receive_payment_id').val(payment_id);
        receive_integrated_address.val(integrated_address);
        $('#receive_address_qrcode').html("");
        $('#receive_address_qrcode').qrcode({width: 220,height: 220, text: integrated_address});
        $('#btn_copy_integrated_address').disable(false);
        hide_progress();
    });
    
    app_hub.on_load_address_book_completed_event.connect(function(address_book){
        address_book = $.parseJSON(address_book);
        hide_progress();
        var html = "Address book empty!";
        if(address_book.length > 0){
            html = '<div id="address-book-box" class="table-responsive">'; 
            html += '<table class="table table-condensed" style="table-layout:fixed;"><thead><tr><th style="border:none">Address</th><th style="border:none;min-width:120px;width:15%;">Payment ID</th><th style="border:none;min-width:120px;width:20%">Description</th><th style="border:none;width:110px;">&nbsp;</th></tr></thead><tbody>';
            var row_tmpl = $('#address_book_row_templ').html();
            for(var i=0; i<address_book.length; i++){
                var entry = address_book[i];
                var address = entry['address'];
                var payment_id = entry['payment_id'];
                if(payment_id.substring(16) == "000000000000000000000000000000000000000000000000"){
                    payment_id = payment_id.substring(0, 16);
                }
                if(payment_id == "0000000000000000"){
                    payment_id = "";
                }
                
                var payment_id_short = payment_id.length > 16 ? payment_id.substring(0,18) + '...' : payment_id;
                var address_short = address.substring(0,18) + '...';
                var desc_short = entry['description'].length > 50 ? entry['description'].substring(0, 50) + '...' : entry['description'];
                
                var row_html = Mustache.render(row_tmpl, 
                                               {   
                                                   'address': address,
                                                   'payment_id': payment_id,
                                                   'address_short': address_short,
                                                   'payment_id_short': payment_id_short,
                                                   'desc_short': desc_short,
                                                   'index': entry['index']
                                               });
                
                html += row_html;
            }
            html += "</tbody></table></div>";
        }
        
        show_app_dialog(html);
        
        $(".address-book-row").click(function() {
            $("#send_address").val( $(this).data("address") );
            $("#send_payment_id").val( $(this).data("payment-id") );
            hide_app_dialog();
            return false;
        });
    });
    
    app_hub.on_tx_detail_found_event.connect(function(tx_detail_json){
        var tx = $.parseJSON(tx_detail_json);
        if(tx['status'] == "ERROR"){
            hide_progress();
            return;
        }
        
        var tx_status_text = tx['status'] == "in" || tx['status'] == "out" ? "Completed" :  (tx['status'] == "pending" ? "Pending" : "In Pool");
        if(tx['confirmation'] < 10){
            if(tx_status_text == "Completed") tx_status_text = "Locked";
            tx_status_text += " (+" + tx['confirmation'] + " confirms)";                
        }
        
        var dest_html = "";
        if(tx.hasOwnProperty('destinations')){
            var destinations = tx['destinations'];
            for(var i=0; i < destinations.length; i++ ){
                dest_html += '<li>Amount: <span class="tx-list tx-amount tx-' + tx['status'] + '">' + printMoney(destinations[i]['amount']/1000000000) + "</span>Address: <strong>" + destinations[i]['address'] + "</strong></li>";
            }
        }
        
        
        var tx_row_tmpl = $('#tx_detail_templ').html();
        var tx_rendered = Mustache.render(tx_row_tmpl, 
                                          {   'cls_in_out': tx['status'],
                                              'tx_direction': tx['direction'] == "in" ? "Incoming Tx:" : "Outgoing Tx:",
                                              'tx_status': tx_status_text,
                                              'tx_fa_icon': tx['direction'] == "in" ? "mail-forward" : "reply",
                                              'tx_id': tx['txid'],
                                              'tx_payment_id': tx['payment_id'], 
                                              'tx_amount': printMoney(tx['amount']/1000000000.),
                                              'tx_fee': printMoney(tx['fee']/1000000000.),
                                              'tx_fee_hide': tx['fee'] > 0 ? '' : 'tx-fee-hide',
                                              'tx_date': dateConverter(tx['timestamp']),
                                              'tx_time': timeConverter(tx['timestamp']),
                                              'tx_height': tx['height'] > 0 ? tx['height'] : "?" ,
                                              'tx_confirmation': tx['confirmation'],
                                              'tx_lock_icon': tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i> ' : '',
                                              'tx_lock_cls': tx['confirmation'] < 10 ? "tx-lock" : "",
                                              'tx_note': tx['note'],
                                              'tx_note_hide': tx['note'].length > 0 ? "" : "tx-note-hide",
                                              'tx_destinations' : dest_html,
                                              'tx_destinations_hide': tx.hasOwnProperty('destinations') ? "" : "tx-destinations-hide"
                                          });
        
        hide_progress();
        show_app_dialog('<div class="copied">' + tx_rendered + '</div>');
    });
    
    app_hub.on_load_tx_history_completed_event.connect(function(ret_json){
        var ret = $.parseJSON(ret_json);
        var txs = ret["txs"];
        var current_page = ret["current_page"];
        var num_of_pages = ret["num_of_pages"];
        var start_page = ret["start_page"];
        var end_page = ret["end_page"];
        
        var tx_history_row_tmpl = $('#tx_history_row').html();
        var table_tx_history_body = $('#table_tx_history tbody');
        table_tx_history_body.html("");
        for(var i=0; i<txs.length; i++){
            var tx = txs[i];
            var row = Mustache.render(tx_history_row_tmpl, {
                'tx_status': tx['confirmation'] == 0 ? '<i class="fa fa-clock-o"></i>' : ( tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i>' : '<i class="fa fa-unlock"></i>' ),
                'tx_direction': tx['direction'] == "in" ? '<i class="fa fa-mail-forward"></i>' : '<i class="fa fa-reply"></i>',
                'tx_date_time': dateConverter(tx['timestamp']) + ' ' + timeConverter(tx['timestamp']),
                'tx_id': tx['txid'],
                'tx_id_short': tx['txid'].substring(0, 26) + "...",
                'tx_payment_id': tx['payment_id'].substring(0, 16),
                'tx_amount': printMoney(tx['amount']/1000000000.),
                'tx_height': tx['height'],
                'cls_in_out': tx['status']
            });
            
            table_tx_history_body.append(row);
        }
        
        if(num_of_pages > 1){
            var page_html = "";
            for(var i=start_page; i<=end_page; i++){
                page_html += '<li class="' + (i == current_page ? 'active' : '') + '"><a href="javascript:load_tx_history(' + i + ')">' + i + '</a></li>';
            }
            
            var tx_history_page_tmpl = $('#tx_history_page_tmpl').html();
            var tx_history_page_html =  Mustache.render(tx_history_page_tmpl, {
                'page_prev_disabled': current_page == 1? 'disabled': '',
                'page_next_disabled': current_page == num_of_pages ? 'disabled' : '',
                'prev_page': current_page > 1 ? current_page - 1 : current_page,
                'next_page': current_page < num_of_pages ? current_page + 1 : current_page,
                'page_html': page_html
            });
            
            $('#tx_history_pages').html('');
            $('#tx_history_pages').append(tx_history_page_html);
        }
        
        current_tx_history_page = current_page;
    });
    
    app_hub.on_view_wallet_key_completed_event.connect(function(title, ret){
        if(ret){
            var html = '<h5>' + title + '</h5>';
            html += '<div class="form-group">';
            html +='<textarea class="form-control address-box copied" style="height:70px;font-size:95%;" readonly="readonly">' + ret + '</textarea>';
            html += '</div>';
            show_app_dialog(html);
        }
    });
    
    app_hub.on_restart_daemon_completed_event.connect(function(){
        hide_progress();
    });
    
    app_hub.on_pop_blocks_completed_event.connect(function(){
        hide_app_progress();
    });
    
    setInterval(function(){
        app_hub.update_wallet_loading_height();
    }, 1000);
    
    app_hub.on_update_wallet_loading_height_event.connect(function(height, target_height){
        //console.log(height);
        if(height < target_height){
            if($('#app_modal_progress').is(':visible')){
                msg = "Processing block# " + height;
                //if( target_height > 0 ) msg += "/" + target_height;
                $('#app_modal_progress_subtext').html(msg);
                $('#app_modal_progress_subtext').show();
            }
        }
        else{
            $('#app_modal_progress_subtext').hide();
        }
    });
}

function delete_address(index){
    hide_app_dialog();
    show_progress("Deleting address book entry...");
    app_hub.delete_address_book(index);
    return false;
}

function update_daemon_status(status_json){
    setTimeout(function(){
        var status = $.parseJSON(status_json);
        var daemon_status = status['status'];
        var current_height = status['current_height'];
        var wallet_height = status['wallet_height']
        is_ready = status['is_ready'] && current_height >= 137510 && wallet_height >= current_height -1;

        var status_text = "Network: " + daemon_status;
        if(daemon_status == "Connected"){
            if(is_ready){
                status_text = '<i class="fa fa-rss fa-flip-horizontal"></i>&nbsp;&nbsp;Network synchronized';
                status_text += " (Height: " + current_height + ")";
                progress_bar.addClass('progress-bar-success')
                    .removeClass('progress-bar-striped')
                    .removeClass('active')
                    .removeClass('progress-bar-warning')
                    .removeClass('progress-bar-danger');
                disable_buttons(false);
            }
            else {
                status_text = '<i class="fa fa-refresh"></i>&nbsp;&nbsp;Synchronizing...';
                status_text += " (Height: " + current_height + ")";
                progress_bar.addClass('progress-bar-striped')
                    .addClass('active')
                    .addClass('progress-bar-warning')
                    .removeClass('progress-bar-success')
                    .removeClass('progress-bar-danger');
                disable_buttons(true);
            }
            progress_bar.css("width", "100%");
            progress_bar.attr("aria-valuenow", 100);
            progress_bar_text_low.html('');
            progress_bar_text_high.html(status_text);
            progress_bar_text_low.hide();
            progress_bar_text_high.show();
        }
        else {
            status_text = '<i class="fa fa-flash"></i>&nbsp;&nbsp;Network: ' + daemon_status;

            progress_bar.addClass('progress-bar-striped')
                .addClass('active')
                .addClass('progress-bar-danger')
                .removeClass('progress-bar-success')
                .removeClass('progress-bar-warning');

            progress_bar.css("width", "1%");
            progress_bar.attr("aria-valuenow", 1);
            progress_bar_text_low.html(status_text);
            progress_bar_text_high.html('');
            progress_bar_text_low.show();
            progress_bar_text_high.hide();
        }
        
    }, 1);
    
}


function update_wallet_info(wallet_info_json){
    setTimeout(function(){
        var wallet_info = $.parseJSON(wallet_info_json);
        var recent_txs = wallet_info['recent_txs'];
        var recent_tx_row_tmpl = $('#recent_tx_row_templ').html();
        
        if(recent_txs.length > 0){
            recent_txs_div.html('');
            for(var i=0; i < recent_txs.length; i++){
                var tx = recent_txs[i];
                var tx_status_text = tx['status'] == "in" || tx['status'] == "out" ? "Completed" :  (tx['status'] == "pending" ? "Pending" : "In Pool");
                if(tx['confirmation'] < 10){
                    if(tx_status_text == "Completed") tx_status_text = "Locked";
                    tx_status_text += " (+" + tx['confirmation'] + " confirms)";                
                }
                
                var tx_rendered = Mustache.render(recent_tx_row_tmpl, 
                                                  {   'cls_in_out': tx['status'],
                                                      'tx_direction': tx['direction'],
                                                      'tx_status': tx_status_text,
                                                      'tx_fa_icon': tx['direction'] == "in" ? "mail-forward" : "reply",
                                                      'tx_id': tx['txid'],
                                                      'tx_payment_id': tx['payment_id'], 
                                                      'tx_amount': printMoney(tx['amount']/1000000000.),
                                                      'tx_fee': printMoney(tx['fee']/1000000000.),
                                                      'tx_fee_hide': tx['fee'] > 0 ? '' : 'tx-fee-hide',
                                                      'tx_date': dateConverter(tx['timestamp']),
                                                      'tx_time': timeConverter(tx['timestamp']),
                                                      'tx_height': tx['height'] > 0 ? tx['height'] : "?",
                                                      'tx_confirmation': tx['confirmation'],
                                                      'tx_lock_icon': tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i> ' : '',
                                                      'tx_lock_cls': tx['confirmation'] < 10 ? "tx-lock" : ""
                                                  });
                recent_txs_div.append(tx_rendered);
            }
        }
        
        disable_buttons(is_ready);
        
        if(current_balance != wallet_info['balance']){
            balance_span.delay(100).fadeOut(function(){
                balance_span.html( printMoney(wallet_info['balance']) );
            }).fadeIn('slow');
            current_balance = wallet_info['balance'];
        }
        
        if(current_unlocked_balance != wallet_info['unlocked_balance']){
            unlocked_balance_span.delay(100).fadeOut(function(){
                unlocked_balance_span.html( printMoney(wallet_info['unlocked_balance']) );
            }).fadeIn('slow');
            current_unlocked_balance = wallet_info['unlocked_balance'];
        }
        
        if(current_address != wallet_info['address']){
            current_address = wallet_info['address'];
            receive_address.val(current_address);
        }
        
        var table_body = $('#table_new_subaddresses tbody');
        var new_subaddress_row_tmpl = $('#new_subaddress_row_tmpl').html();
        var new_subaddresses = wallet_info['new_subaddresses'];
        
        table_body.html('');
        
        for(var i=0; i < new_subaddresses.length; i++){
            var subaddress = new_subaddresses[i];
            var row_rendered = Mustache.render(new_subaddress_row_tmpl, 
					       {   'address_index': subaddress['address_index'],
						   'address' : subaddress['address']
					       });
            
            
            table_body.append(row_rendered);
        }
        
        table_body = $('#table_used_subaddresses tbody');
        var used_subaddress_row_tmpl = $('#used_subaddress_row_tmpl').html();
        var used_subaddresses = wallet_info['used_subaddresses'];
        
        table_body.html('');
        
        for(var i=0; i < used_subaddresses.length; i++){
            var subaddress = used_subaddresses[i];
            var row_rendered = Mustache.render(used_subaddress_row_tmpl, 
					       {   'address_index': subaddress['address_index'],
						   'address' : subaddress['address'],
						   'balance': subaddress['balance'],
						   'unlocked_balance': subaddress['unlocked_balance'],
						   'row_font_weight': subaddress['address_index'] == 0 ? 'bold' : 'normal'
					       });
            
            
            table_body.append(row_rendered);
        }
        
        hide_app_progress();
        $('[data-toggle="tooltip"]').tooltip();
        
    }, 1);
}

function show_qrcode(text){
    $('#qrcode_dialog_body').html('');
    $('#qrcode_dialog_body').qrcode({width: 200,height: 200, text: text});
    $('#qrcode_dialog').modal('show');
    
}

function disable_buttons(s){
    rescan_spent_btn.disable(s);
    rescan_bc_btn.disable(s);
    btn_send_tx.disable(s);
    btn_fill_all_money.disable(s);
    
    syncing.each(function(index, value){
        s ? $(this).show() : $(this).hide();
    });
    
    balance_span.toggleClass('syncing', s);
    unlocked_balance_span.toggleClass('syncing', s);
}

function rescan_spent(){
    rescan_spent_btn.disable(true);
    rescan_bc_btn.disable(true);
    show_progress("Rescan spent...");
    app_hub.rescan_spent();
    return false;
}

function rescan_bc(){
    rescan_spent_btn.disable(true);
    rescan_bc_btn.disable(true);
    show_app_progress("Rescan blockchain...");
    app_hub.rescan_bc();
    return false;
}

function fill_all_money(){
    $('#send_amount').val(current_unlocked_balance);
    return false;
}

function send_tx(){
    var amount = $('#send_amount').val().trim();
    var sweep_all = false;
    var errors = [];
    amount = parseFloat(amount);
    
    if(!amount || amount < 0)
    {
        errors.push("Send amount must be a positive number!");
        $('#send_amount').parent().addClass('has-error');
    }
    else if(amount > current_unlocked_balance){
        errors.push("Send amount is more than unlocked balance!");
        $('#send_amount').parent().addClass('has-error');
    }
    else{
        if(amount == current_unlocked_balance){
            sweep_all = true;
        }
        $('#send_amount').parent().removeClass('has-error');
    }
    
    var address = $('#send_address').val();
    if(!address){
        errors.push("Address is required!");
        $('#send_address').parent().addClass('has-error');
    }
    else if(!((address.substr(0, 4) == "Sumo" && address.length == 99) || 
              (address.substr(0, 4) == "Sumi"  && address.length == 110) || 
              (address.substr(0, 4) == "Subo"  && address.length == 98) ||

              (address.substr(0, 4) == "Suto"  && address.length == 98) ||
              (address.substr(0, 4) == "Susu"  && address.length == 98)))
    {
        errors.push("Address is not valid!");
        $('#send_address').parent().addClass('has-error');
    }
    else{
        $('#send_address').parent().removeClass('has-error');
    }
    
    var payment_id = $('#send_payment_id').val().trim();
    if(payment_id && !(payment_id.length == 16 || payment_id.length == 64)){
        errors.push("Payment ID must be a 16 or 64 hexadecimal-characters string!");
        $('#send_payment_id').parent().addClass('has-error');
    }
    else{
        $('#send_payment_id').parent().removeClass('has-error');
    }
    
    if(errors.length > 0){
        var msg = "<ul>";
        for(var i=0; i<errors.length;i++){
            msg += "<li>" + errors[i] + "</li>";
        }
        msg += "</ul>";
        show_alert(msg);
        return false;
    }
    
    var tx_desc = $('#send_tx_desc').val().trim();
    var priority = $('#send_priority').val();
    var mixin = $('#send_mixins').val();
    
    btn_send_tx.disable(true);
    show_progress("Sending coins... This can take a while for big amount...");
    app_hub.send_tx(amount, address, payment_id, priority, mixin, tx_desc, $('#checkbox_save_address').is(":checked"), sweep_all);
    return false;
}

function generate_payment_id(){
    show_progress("Generating payment ID, integrated address...");
    app_hub.generate_payment_id(16);
    return false;
}

function copy_address(){
    $('#btn_copy_address').tooltip('show');
    //receive_address.select();
    app_hub.copy_text(receive_address.val());
    setTimeout(function(){
        $('#btn_copy_address').tooltip('hide');
    }, 1000);
    return false;
}

function qr_address(){
    show_qrcode(receive_address.val());
    return false;
}

function copy_subaddress(el, subaddress_text){
    $(el).tooltip('show');
    app_hub.copy_text(subaddress_text);
    setTimeout(function(){
        $(el).tooltip('hide');
    }, 1000);
    return false;
}


function copy_integrated_address(){
    $('#btn_copy_integrated_address').tooltip('show');
    receive_integrated_address.select();
    app_hub.copy_text(receive_integrated_address.val());
    setTimeout(function(){
        $('#btn_copy_integrated_address').tooltip('hide');
    }, 1000);
    return false; 
}

function view_tx_detail(height, tx_id){
    show_progress("Load tx details...");
    app_hub.view_tx_detail(height == "?" ? 0 : parseInt(height), tx_id);
    return false;
}

function load_tx_history(page){
    app_hub.load_tx_history(page);
    return false;
}


function show_address_book(){
    show_progress("Loading address book...");
    app_hub.load_address_book();
    return false;
}

function open_new_wallet(){
    app_hub.open_new_wallet();
    return false;
}

function view_wallet_key(key_type){
    app_hub.view_wallet_key(key_type);
    return false;
}

function set_daemon_log_level(level){
    console.log(level);
    app_hub.set_daemon_log_level(level);
}

function set_block_sync_size(sync_size){
    app_hub.set_block_sync_size(sync_size);
}

function about_app(){
    app_hub.about_app();
    return false;
}

function show_app_dialog(msg, title){
    $('#app_model_body').removeClass('alert');
    $('#app_model_body').html(msg);
    $('#btn_copy').text('Copy');
    $('#app_modal_dialog').modal('show');
}

function hide_app_dialog(){
    $('#app_modal_dialog').modal('hide');
}

function show_alert(msg, title){
    $('#app_model_body').addClass('alert');
    $('#app_model_body').html(msg);
    $('#app_modal_dialog').modal('show');
}

function show_app_progress(msg){
    $('#app_modal_progress_text').html(msg);
    $('#app_modal_progress').modal('show');
}

function hide_app_progress(){
    $('#app_modal_progress').modal('hide');
}

function show_progress(msg){
    $('#sending_modal_progress_text').html(msg);
    $('#sending_modal_progress').modal('show');
}

function hide_progress(){
    $('#sending_modal_progress').modal('hide');
}

function open_link(link){
    app_hub.open_link(link);
    return false;
}

function restart_daemon(){
    show_app_progress("Restarting daemon...");
    app_hub.restart_daemon();
    return false;
}

function pop_blocks(){
    show_app_progress("Popping blocks...");
    app_hub.pop_blocks();
    return false;
}

function copy_dialog_content(){
    app_hub.copy_text( $('#app_model_body .copied').text() );
    $('#btn_copy').text('Copied');
}

function toggle_dark_mode(){
    $('body').toggleClass('dark-theme');
    app_hub.set_dark_mode( $('body').hasClass('dark-theme') );
}

$(document).ready(function(){
    progress_bar_text_low = $('#progress_bar_text_low');
    progress_bar_text_high = $('#progress_bar_text_high');
    progress_bar = $('#progress_bar');
    balance_span = $('#balance');
    unlocked_balance_span = $('#unlocked_balance');
    rescan_spent_btn = $('#btn_rescan_spent');
    rescan_bc_btn = $('#btn_rescan_bc');
    syncing = $('.syncing');
    wallet_address = $('#wallet_address');
    btn_send_tx = $('#btn_send_tx');
    btn_fill_all_money = $('#btn_fill_all_money');
    recent_txs_div = $('#recent_txs');
    
    current_balance = null;
    current_unlocked_balance = null;
    current_address = null;
    
    current_tx_history_page = 1;

    is_ready = false;
    show_app_progress("Loading wallet...");
    
    receive_address = $('#receive_address');
    receive_integrated_address = $("#receive_integrated_address");
    
    receive_address.focus(function() {
        var $this = $(this);
        $this.select();
        $this.mouseup(function() {
            $this.unbind("mouseup");
            return false;
        });
    });
    
    receive_integrated_address.focus(function() {
        var $this = $(this);
        $this.select();
        $this.mouseup(function() {
            $this.unbind("mouseup");
            return false;
        });
    });
    
    $('[data-toggle="tooltip"]').tooltip();
    
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(this).attr('href');
        
        if(current_tx_history_page == 1 && target == "#tx_history_tab"){
            setTimeout(function(){
                load_tx_history(current_tx_history_page);
            }, 1);
        }
    });
});
