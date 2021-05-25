function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function cloneMore(selector, prefix) {
    
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    
    newElement.find(':input').each(function() {
        var name = $(this).attr('name')
        if(name){
            name = name.replace('-' + (total-1) + '-', '-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        }
    });
    newElement.removeAttr('hidden');
    total++;

    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);

    var conditionRow = $('.table-row:not(:last)');
    conditionRow.find('.btn.add-table-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-table-row').addClass('remove-table-row')
    .html('-');
    
    $('.remove-table-row').prop('disabled', false);

    return false;
}

function deleteForm(prefix, btn) {
    var total = $('.table-row:not([hidden])').length;

    if (total > 1){
        row = btn.closest('.table-row');
        row[0].setAttribute('hidden', 'True');

        input_delete = row[0].children[0].cloneNode(true);                
        input_delete.setAttribute('name', input_delete.getAttribute('name').replace('id', 'DELETE'));
        input_delete.setAttribute('id', input_delete.getAttribute('id').replace('-id', '-DELETE'));
        input_delete.setAttribute('value', 'on');
        
        row[0].children[0].after(input_delete);

        if(total==2){
            $('.remove-table-row').prop('disabled', true );
        }
    }
    return false;
}

$(document).on('click', '.add-table-row', function(e){
    e.preventDefault();
    cloneMore('.table-row:last', 'form');
    return false;
});

$(document).on('click', '.remove-table-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
});

$(document).ready(function(){
    let total = parseInt($('#id_form-TOTAL_FORMS').val());
    if(total > 1){
        $('.remove-table-row').prop('disabled', false );
    }
});
