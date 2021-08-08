function addField(selected_form) {
    var formFilter = 'div[id^="' + selected_form + '_product_index"]'
    var formFields = $(formFilter);
    var hiddenFields = $(formFilter + ":hidden").length;
    var visibleFields = $(formFilter + ":visible").length;

    if (hiddenFields == 0) {
        alert('Você já adicionou o seu máximo de campos');
        return false;
    }

    formFields.each(function () {
        if ($(this).hasClass('disabled')) {
            $(this).removeClass('disabled');
            $(formFilter + " button.btn.btn-red." + selected_form).removeClass('disabled');
            return false;
        }
    });

    // if it is the last field visible, just 
    if (visibleFields >= 1 && !$(formFields[0]).hasClass('removable')) {
        $("button[id$='00']").removeClass('disabled');
        $(formFields[0]).addClass('removable');
        console.log(formFields[0]);
    }
}


function removeField(selected_form, idx) {
    
    var formFilter = 'div[id^="' + selected_form + '_product_index"]'
    var formFields = $(formFilter);
    
    let current_field = 'div#' + selected_form + '_product_index_0' + idx;

    $(current_field).addClass('disabled');
    $(current_field + ' select option[value="__None"]').prop('selected', true);
    $(current_field + ' input[id$="amount"]').val('0');
    $(current_field + ' input[id$="price"]').val('0.00');

    if ($(formFilter + ":visible").length == 1) {
        $("button.btn.btn-red." + selected_form + ":visible").addClass('disabled');
    }
}