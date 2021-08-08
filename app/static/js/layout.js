function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + (d.getDate() + 1),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}


$('.date').mask('11-11-1111');
$('.cep').mask('00000-000');
$('.ddd').mask('(00)');
$('.phone').mask('00000-0000');
$('.cnpj').mask('00.000.000/0000-00');
$('.cpf').mask('000.000.000-00', {reverse: true});
$('.money').mask('000.000.000.000.000,00', {reverse: true});