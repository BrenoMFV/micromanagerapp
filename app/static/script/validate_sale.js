
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

const editForm = document.getElementById('edit_sale');
const regForm = document.getElementById('reg_sale');

regForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (checkInputs('reg')) {
        e.target.submit();
    }
});

editForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (checkInputs('edit')) {
        e.target.submit();
    }
});


function checkInputs(id) {
    var currentForm = 'div[id^="' + id + '_"] div[class^="col"] ';
    var formLength = $('div[id^="' + id + '_"]').length;

    var status = true;
    for (let i = 0; i < formLength; i++) {
        var productForm = currentForm + 'select[id="products-' + i.toString() + '-product"]';
        var amountForm = currentForm + 'input[id="products-' + i.toString() + '-amount"]';
        var priceForm = currentForm + 'input[id="products-' + i.toString() + '-price"]'; 
        var dateForm = 'div.' + id + '_dates input#date';
        var amount = $(amountForm).val().replace(',', '.');
        var price = $(priceForm).val().replace(',', '.');

        if ($(productForm).val() == '__None' & (parseFloat(amount) != 0.00 | parseFloat(price) != 0.00)) {
            console.log(productForm + ' é o formulário');
            setErrorFor(currentForm + 'select#products-' + i.toString() + '-product', 'Não se esqueça de escolher seu produto');
            status = false;
        } else {
            setSuccessFor('select#products-' + i.toString() + '-product');
        }

        if ($(productForm).val() != '__None' & parseFloat(amount) == 0.00 ) {
            console.log('products-' + i.toString() + '-amount é o formulário');
            setErrorFor(currentForm + 'input#products-' + i.toString() + '-amount', 'Preencha a quantidade a ser vendida');            
            status = false;
        } else if ($(productForm).val() != '__None' & parseFloat(price) == 0.00) {
            console.log('products-' + i.toString() + '-price é o formulário');
            setErrorFor(currentForm + 'input#products-' + i.toString() + '-price', 'Preencha o valor unitário da venda');
            status = false;
        } else {
            setSuccessFor('input#products-' + i.toString() + '-amount');
            setSuccessFor('input#products-' + i.toString() + '-price');
        }

        if ($(dateForm).val() == '') {
            console.log(currentForm + 'data é o formulário')
            setErrorFor(currentForm + dateForm, 'A data de lançamento não pode ser deixada em branco');
            status = false;
        } else { 
            setSuccessFor(dateForm);
        }
    }

    if (isEmptySale(currentForm, formLength)) {
        console.log('empty form');
        setErrorFor('div.' + id + ' select#client', 'O formulário está em branco.');
        status = false;
    } else {
        setSuccessFor('select#client');
    }

    console.log(status);
    return status;
}

function isEmptySale(form, len){
    /* returns true if it's not an empty sale and false if it is */
    var counter = 0;
    for (let i = 0; i < len; i++){
        
        var product_field = $(form + ' select[id$="'+ i + '-product"]'); 
        var amount_field = $(form + ' input[id$="'+ i + '-amount"]');
        var price_field = $(form + ' input[id$="'+ i + '-price"]');
        var amount = amount_field.val().replace(',', '.');
        var price = price_field.val().replace(',', '.');

        if (product_field.val() == '__None' && parseFloat(amount) == 0.00 && parseFloat(price) == 0.00){
            counter++;    
            // console.log(counter)
        }
    }   
    if (counter === len){
        return true;
    }
    return false;
}

function setSuccessFor(input) {
    const formGroup = $(input); // .form-control
    const small = formGroup.next();
    small.removeClass('error');
}

function setErrorFor(input, message) {
    const formGroup = $(input); // .form-control
    const small = formGroup.next();

    // add error message inside small
    small.text(message);

    // add error class
    small.addClass('error');
}
