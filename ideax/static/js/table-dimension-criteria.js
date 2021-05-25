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
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.table-row').remove();
        var forms = $('.table-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
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
    console.log("Teste")
    let total = parseInt($('#id_form-TOTAL_FORMS').val());
    if(total > 1){
        $('.remove-table-row').prop('disabled', false );
    }
});
