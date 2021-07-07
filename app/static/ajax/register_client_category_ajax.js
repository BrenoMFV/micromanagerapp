$(document).ready(function () {
    $('#registerClientCategoryForm').on('submit', function (event) {

        event.preventDefault();
        console.log('aqui');
        let data = {};

        $.each($(this).serializeArray(), function (index, item) {
            data[item.name] = item.value;
        });

        $.ajax({
            url: 'http://127.0.0.1:5000{{ url_for(".register_client_category") }}', 
            contentType: 'application/json',
            type='post',
            data: data, 
            success: function(response) {
                console.log(response);
            },
            error: function(err){
                console.error(err);
            }
        });

    });
});
