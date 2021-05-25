function deleteCard(id){
  $("div[card-id="+ id + "]").remove();
}

function createCard(id, title, summary){

  var detail_url = $('div[class="card-columns"]').attr("url");
  var detail_text = $('div[class="card-columns"]').attr("detail_text");
  var div_card = document.createElement("div");
  var div_body = document.createElement("div");
  var h5 = document.createElement("h5");
  var span = document.createElement("span");
  var div_card_text = document.createElement("div");
  var div_text_left = document.createElement("div");
  var a_detail = document.createElement("a");
  var p_summary = document.createElement("p");
  
  div_card.setAttribute("class", "card mb-2 col-x-4");
  div_card.setAttribute("card-id", id);
  
  div_body.setAttribute("class", "card-body");
  h5.setAttribute("class", "card-title");
  h5.innerHTML = title;
  div_body.appendChild(h5);

  span.setAttribute("class", "creation-order d-none");
  span.innerHTML = id;
  div_body.appendChild(span);

  div_card_text.setAttribute("class", "card-text");
  p_summary.innerHTML = summary;
  div_card_text.appendChild(p_summary);
  div_body.appendChild(div_card_text);

  div_text_left.setAttribute("class", "text-left");
  a_detail.setAttribute("id", "idea_detail_"+id);
  a_detail.setAttribute("href", "/" + detail_url.split("/")[1]+"/" + id + "/");
  a_detail.innerHTML = detail_text;

  div_text_left.appendChild(a_detail);
  div_body.appendChild(div_text_left);
  div_card.appendChild(div_body);

  return div_card;
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function updateCounter(increment){

  var count =  $('div[name="counter"]').attr("count");
  if(increment == true){
      count = parseInt(count) + 1;
  }else{
      count = parseInt(count) - 1;
  }
  $('div[name="counter"]').attr("count", count);
  $('div[name="counter"]').children().last().text(count);
}

function createTR (idea) {

  var tr = document.createElement("tr");
  tr.setAttribute("class", "table-row");
  tr.setAttribute("tr-id", idea.id);

  tr.appendChild(createTD(idea.id, "5%", "table-row-description"));
  tr.appendChild(createTD(idea.title, "30%", "table-row-description"));
  tr.appendChild(createTD(idea.summary, "30%", "table-row-value"));
  tr.appendChild(createTD(idea.author, "10%", "table-row-description"));
  tr.appendChild(generateButton());

  return tr;
}

function generateButtonTrash(idea_id){

  var td = document.createElement("td");
  var button = document.createElement("button");
  var i = document.createElement("i");

  td.setAttribute("width", "10%");
  td.setAttribute("class", "text-center");

  button.setAttribute("type", "button");
  button.setAttribute("class", "btn del-relation");

  i.setAttribute("class", "fa fa-trash");

  button.appendChild(i);
  td.appendChild(button);

  return td;
}

function createTRTrash (idea) {

  var tr = document.createElement("tr");
  tr.setAttribute("class", "table-row");
  tr.setAttribute("tr-id", idea.id);

  tr.appendChild(createTD(idea.id, "5%", "table-row-description"));
  tr.appendChild(createTD(idea.title, "30%", "table-row-description"));
  tr.appendChild(createTD(idea.summary, "30%", "table-row-value"));
  tr.appendChild(createTD(idea.author, "10%", "table-row-description"));
  tr.appendChild(generateButtonTrash());

  return tr;
}

function createTD(value, width, class_value){

  var td = document.createElement("td");
  td.setAttribute("width", width);
  td.setAttribute("class", class_value);

  td.innerHTML = value;

  return td;
}

function generateButton(idea_id){

  var td = document.createElement("td");
  var button = document.createElement("button");
  var i = document.createElement("i");

  td.setAttribute("width", "10%");
  td.setAttribute("class", "text-center");

  button.setAttribute("type", "button");
  button.setAttribute("class", "btn add-relation");

  i.setAttribute("class", "fa fa-plus");

  button.appendChild(i);
  td.appendChild(button);

  return td;
}

function showMessage(message, classMessage){
  $("#comment-message-association").html(message);
  $("#comment-message-association").css("display","");
  $("#comment-message-association").removeClass("alert-danger").removeClass("alert-warning").addClass(classMessage);
}

function hiddeMessage(){
  $("#comment-message-association").css("display","none");
}

$(document).on("click", 'button[name="clean-search"]', function(){
  $("#comment-message-association").css("display","none");
  $('#search_part').val("");

  if($('table[name="tbl-unrelated-ideas"]').children('tbody').children().length > 0){
      table = $('table[name="tbl-unrelated-ideas"]').DataTable();
      table.destroy();
      $('table[name="tbl-unrelated-ideas"]').children('tbody').children().remove();
  }
})

function updateUnrelatedIdea(ideas){
  var $tbody = $('table[name="tbl-unrelated-ideas"]').children('tbody');
  destroyDataTable('table[name="tbl-unrelated-ideas"]');
  ideas.forEach(function(ideia){
      var tr = createTR(ideia);
      $tbody.append(tr);
  }); 
  createDataTable('table[name="tbl-unrelated-ideas"]');
}

function updateRalatedIdea(ref, relations){
  var tbody_related = $('table[name="tbl-related-ideas"]').find('tbody');
  
  destroyDataTable('table[name="tbl-related-ideas"]');
  relations.forEach(function(idea){
      $(tbody_related).append(createTRTrash (idea));
  })
  $(ref).remove();
  createDataTable('table[name="tbl-related-ideas"]');
  
  updateCounter(false)
}

function dellRelation(ref, idea_id_related){

  var tbl_unrelated = $('table[name="tbl-unrelated-ideas"]');
  var tbl_related = $('table[name="tbl-related-ideas"]'); 
  var idea_id = $('table[name="tbl-unrelated-ideas"]').attr('idea_id');
  
  $.ajax({
      url: '/idea/relationship/',
      type: 'POST',
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      contentType: "application/json",
      data: JSON.stringify({"idea_id": idea_id, "idea_id_related": idea_id_related, "action":"unrelation"}),
      success: function(result) {
         
          if($('table[name="tbl-unrelated-ideas"]').children('tbody').children().length > 0){

              table = $('table[name="tbl-unrelated-ideas"]').DataTable();
              table.destroy();
              tbl_unrelated.children('tbody').children("tr[tr-id=" + idea_id_related + "]").children().last().children("svg").remove(); 
              tbl_unrelated.children('tbody').children("tr[tr-id=" + idea_id_related + "]").children().last().remove();
              tbl_unrelated.children('tbody').children("tr[tr-id=" + idea_id_related + "]").append(generateButton(idea_id_related));
  
              createDataTable('table[name="tbl-unrelated-ideas"]');
          } else {
              table = $('table[name="tbl-related-ideas"]').DataTable();
              table.destroy();
              tbl_related.children('tbody').children("tr[tr-id=" + idea_id_related + "]").remove();

              createDataTable('table[name="tbl-related-ideas"]');
          }
          
          deleteCard(idea_id_related);
          showMessage(result.msg, "alert-success");
          updateRalatedIdea(ref, result['relations']);
      }
  });

}

$(document).on("click", "#modal-btn-no-relationship", function () {
  $("#comment-message-association").css("display","none");
  $('#modalRelationShip').modal("hide");
})

$(document).on("click", "#modal-btn-yes-relationship", function () {
  $("#comment-message-association").css("display","none");
  var tr_id = $(this).attr("tr-id");
  var tbl_unrelated = $('table[name="tbl-related-ideas"]').children('tbody');
  var ref = $(tbl_unrelated).children("tr[tr-id="+ tr_id +"]")[0]; 
  dellRelation(ref, tr_id);
  $('#modalRelationShip').modal("hide");
})


$(document).on("click", 'button[class="btn del-relation"]', function () {
  $("#comment-message-association").css("display","none");
  var tr_id = $(this).closest("tr").attr("tr-id");
  $('#modalRelationShip').modal("show");
  $('#modalRelationShip').
      children(".modal-dialog").
      children(".modal-content").
      children(".modal-footer").
      children("#modal-btn-yes-relationship").attr("tr-id", tr_id);
});

function addRelationShip(ref){
  var button = document.createElement("button");
  var $tr = $(ref).closest("tr"); 
  var $td = $(ref).closest("td"); 
  $(ref).remove();

  var i = document.createElement("i");
  i.setAttribute("class", "fa fa-check");
  i.setAttribute("aria-hidden", "true");
  $td.append(i);
  
  var i_trash = document.createElement("i");
  i_trash.setAttribute("class","fa fa-trash");
  button.setAttribute("type", "button");  
  button.setAttribute("class", "btn del-relation");
  button.append(i_trash);

  var $tr_clone = $($tr).clone(true);
  $tr_clone.children().last().children().remove();
  $tr_clone.children().last().append(button);
  $(".tbl-related-ideas").find("tbody").append($tr_clone);
  
  var id = $tr.children()[0].innerText
  var title = $tr.children()[1].innerText
  var summary = $tr.children()[2].innerText

  var card = createCard(id, title, summary);

  $('div[class="card-columns"]').append(card);

  updateCounter(true);
}

$(document).on("click", 'button[class="btn add-relation"]', function () {
  $("#comment-message-association").css("display","none");
  var idea_id = $('table[name="tbl-unrelated-ideas"]').attr('idea_id');
  var idea_id_related = $(this).closest('tr').children().first()[0].innerHTML;
  var ref = this;
  $.ajax({
      url: '/idea/relationship/',
      type: 'POST',
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      contentType: "application/json",
      data: JSON.stringify({"idea_id": idea_id, "idea_id_related": idea_id_related, "action":"relation"}),
      success: function(result) {
          if(result["process_result"] == "success"){
              table = $('table[name="tbl-related-ideas"]').DataTable();
              table.destroy();
              addRelationShip(ref); 
              createDataTable('table[name="tbl-related-ideas"]');
              showMessage(result.msg, "alert-success");
          } 
      }
  });

})

function destroyDataTable(query){
  if ( $.fn.dataTable.isDataTable(query) ) {
      var $tbody = $(query).children('tbody');
      table = $(query).DataTable();
      table.destroy();
      $tbody.children().remove()
  } 
}

function updateLable(){

  $('.previous').text('Anterior');
  $('.next').text('Próximo');

  var $empty_search = $('.dataTables_empty')
  if($empty_search.length == 1){
    $empty_search.text("Nenhuma ocorrência encontrada.");
  }
  
}

function createDataTable(query){
  $(query).DataTable({
      "ordering": false,
      "searching": false,
      "pageLength": 3
  }); 

  $("#DataTables_Table_0_length").attr("hidden","true");
  $("#DataTables_Table_1_length").attr("hidden","true");
  $("#DataTables_Table_0_info").attr("hidden","true");
  $("#DataTables_Table_1_info").attr("hidden","true");
  $("#DataTables_Table_0_wrapper").attr("style","width:100%");
  $("#DataTables_Table_1_wrapper").attr("style","width:100%");

  updateLable();
}

$(document).on("click", 'a[class="paginate_button "]', function(){
  updateLable();   
})

$(document).on("click", 'a[class="paginate_button previous"]', function(){
  updateLable();   
})

$(document).on("click", 'a[class="paginate_button next"]', function(){
  updateLable();   
})

$(document).on("click", 'button[name="search-related"]', function () {
  $("#comment-message-association").css("display","none");
  var idea_id = $('table[name="tbl-unrelated-ideas"]').attr('idea_id');
  
  $.ajax({
      url: '/idea/related/',
      type: 'POST',
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      contentType: "application/json",
      data: JSON.stringify({"search_part": $('#search_part').val(), "idea_id": idea_id}),
      success: function(result) {
          if(result["process_result"] == "success"){
              updateUnrelatedIdea(result['ideas']);
              hiddeMessage();
          } else {
              showMessage(result.msg, "alert-warning");
          }


      }
  });
})

$(document).ready(function() {
  if($('table[name="tbl-related-ideas"]').children("tbody").children().length > 0){
      createDataTable('table[name="tbl-related-ideas"]');
  }
});