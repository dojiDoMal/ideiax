//modal delete
$(document).ready(function () {

    $('body').on('click', '#modal-btn-yes', function (){
        var id = $(this).data('id');
        $("#mi-modal").modal('hide');
        location.href = urlDelete(id);
    });

    $("#modal-btn-no").on("click", function(){
        $("#mi-modal").modal('hide');
    });

    function urlDelete(id){
        return window.location.protocol + '//' +  window.location.host + '/' + location.pathname.split('/')[1] + '/' + id + '/' + "remove";
    }

});

$(document).on('click', '.btn-click-del-challenge', function(){
    $("#mi-modal").modal('show');
    title = $(this).parents('div.challenge-item').find('h5').text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', '.btn-click-del-use-term', function(){
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').eq(1).text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', '.btn-click-del-criterion', function () {
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').first().text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', '.btn-click-del-category-img', function () {
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').first().text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', '.btn-click-del-category', function () {
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').first().text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', '.btn-click-del-dimension', function () {
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').first().text();
    modalComponent($(this).data('string'), $(this).data('name'), title, $(this).data('id'));
});

$(document).on('click', 'a[name="replyDelete"]', function () {
    $("#mi-modal").modal('show');
    title = $(this).closest('tr').children('td').first().text();
    $("#LabelModalDelete").html($(this).data('string'));
    $("#modal-btn-yes-comment").attr('data-parent-id', $(this).attr("data-parent-id"));
});

function modalComponent(string, componentName, title, id){
    $("#LabelModalDelete").html(string + componentName +": " + title + "?");
    $("#modal-btn-yes").data('id', id);
}
