/* ------------------------------------------------------------------------------
*
*  # edit variant scripts
*
*  Specific JS code additions for ps254 backend pages
*
*  Version: 1.0
*  Latest update: Sept 15, 2017
*
* ---------------------------------------------------------------------------- */

$(function(){
  var editStockRefreshDiv = $('#div-edit-stock');  
  var editStockBtn = $('#editStockBtn');
  var cancelStockBtn = $('#cancelStockBtn');
  var url = '#';
  var editArea = $('#edit-area');
  var editForm  = editArea.find('form');
  var invoice_number = editForm.find("#id_invoice_number");
  var variant = editForm.find('#id_variant');
  var status = editForm.find('#status');
  var cost_price = editForm.find('#id_cost_price');
  var price_override = editForm.find('#id_price_override');
  var wholesale_override = editForm.find('#id_wholesale_override');
  var minimum_price = editForm.find('#id_minimum_price');
  var location = editForm.find('#id_location');
  var quantity = editForm.find('#id_quantity');
  var editStockAmountPaid = editForm.find('#id_amount_paid');
  var editStockTotalCost  = editForm.find('#id_total_cost');
  var editStockPaymentOption = editForm.find('#id_payment_options');
  var low_stock_threshold = editForm.find('#reorder-threshold');
  var settlePayment = editForm.find('#settle_payment');
  var balance = editForm.find('#balance_e');

  cancelStockBtn.on('click', function(){
    $('html, body').find('#div-edit-stock').html('');
  });

  editStockBtn.on('click',function(){
    var url = $(this).data('contenturl');
    var refreshUrl = $(this).data('refreshstockurl')+"?tab=stock";
    
    dynamicData = {};
    dynamicData['status'] = status.val();
    if(editStockAmountPaid.val()){
      dynamicData['amount_paid'] = editStockAmountPaid.val();
    }
    if(settlePayment.val()){
      dynamicData['settle_payment'] = settlePayment.val();
    }
    if(balance.val()){
      dynamicData['balance'] = balance.val();
    }

    if(editStockPaymentOption.val()){
      dynamicData['payment_options'] = editStockPaymentOption.val();
    }
    if(editStockTotalCost.val()){
      dynamicData['total_cost'] = editStockTotalCost.val();
    }
    dynamicData['location'] = location.val();

    if(cost_price.val()){
      dynamicData['cost_price'] = cost_price.val();
    }
    if(price_override.val()){
      dynamicData['price_override'] = price_override.val();
    }
    if(wholesale_override.val()){
      dynamicData['wholesale_override'] = wholesale_override.val();
    }
    if(minimum_price.val()){
      dynamicData['minimum_price'] = minimum_price.val();
    }
    if(!variant.val()){
      alertUser('Variant field required','bg-warning','Variant required!');
      return false;
    }else{
      dynamicData['variant'] = variant.val();
    }
    if(!quantity.val()){
      alertUser('quantity field required','bg-warning','Quantity required!');
      return false;
    }else{
      dynamicData['quantity'] = quantity.val();
    }       
    if(low_stock_threshold.val()){
      dynamicData['low_stock_threshold'] = low_stock_threshold.val();
    }   
      
    
    dynamicData['template'] = 'edit_stock';    

    addProductDetails(dynamicData,url,'post')
    .done(function(data){
      alertUser('Product Stock updated successfully');
      $('#div-edit-variant').slideUp();      
      window.location.href = refreshUrl;
    })
    .fail(function(data){
      alertUser('update failed','bg-danger','Ooops!');
    });    
  
  });

});

