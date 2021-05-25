$('.expand-button').on('click', function (evt) {
  let ideaText = evt.currentTarget.parentNode.parentNode.querySelector('p');
  ideaText.classList.toggle('expand');
  $(this).classList.toggle('expand-btn');
  //console.log($(evt.currentTarget).parent().parent());
});

$(window).scroll(function(){
if($(window).scrollTop() >= $('.main-header').outerHeight()) {
  var scroll = $(window).outerWidth() - $('body').outerWidth();
  $('.phase-filter').addClass('fixed');
  $('.phase-filter').css("width", $(window).outerWidth() - scroll);
}else{
  $('.phase-filter').removeClass('fixed');
  $('.phase-filter').css("width", "100%");
}
});


$(document).mouseup(function (e)
{
    var container = $(".idea-options");

    if (!container.is(e.target) && container.has(e.target).length === 0){
        $( ".idea-options input" ).prop( "checked", false ); //to uncheck
    }
});


function openModal (url){
  $.ajax({
    url: url,
    type: 'get',
    dataType: 'json',
    beforeSend: function (){
      $("#modal-idea").modal("show");
    },
    success: function (data){
      $("#modal-idea .modal-content").html(data.html_form);
    }
  });
}

function vote(url, idLike, idDislike, aLike, aDislike){
  $.ajax({
    url: url,
    type: 'get',
    dataType: 'json',
    success: function (data){
      $(idLike).html(data.qtde_votes_likes);
      $(idDislike).html(data.qtde_votes_dislikes);

      if (data.class == null){
        $(aLike).removeClass("fas").addClass("far");
        $(aDislike).removeClass("fas").addClass("far");
      } else if (data.class == true){
        $(aLike).addClass("fas");
        $(aDislike).removeClass("fas").addClass("far");
      }else {
        $(aLike).removeClass("fas").addClass("far");
        $(aDislike).addClass("fas");
      }
    }
  });
}

function getUserTerm(idDivTerm, urlTerm){
  var term;
  $.ajax({
    url: urlTerm,
    type: 'get',
    dataType: 'json',
    success: function (data){
      term = data.term;
      $(idDivTerm).html(term);
    }
  });
  return term;
}

$(function () {
  var loadForm = function(){
    var btn = $(this);
    var idModal = btn.attr("data-modal");
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function (){
          $(idModal).modal("show");
      },
      success: function (data){
        var idModalContent = idModal + " .modal-content";
        $(idModalContent).html(data.html_form);
      }
    });
  };

  var saveForm = function(){
    var form = $(this);
    var idModal = form.attr("data-modal");
    var idDivList = form.attr("data-list-div");
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data){
        if(data.form_is_valid){
           $(idDivList).html(data.html_list);
            console.log("Teste")
            console.log(data.change)
            console.log(data.id_list)


           $(idModal).modal("hide");
        }else{
          var idModalContent = idModal + " .modal-content";
          $(idModalContent).html(data.html_form);
        }
      }
    });
    return false;
  };

  // When the user clicks on the button, scroll to the top of the document
  function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
  }

  var modalSubmitTotalEvaluation = function () {
    var form = $("#evaluation_form");
    var button = $("input[type=submit][clicked=true]");

    $.ajax({
      url: button.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data){
        var score = data.score_value;
        $("#score").removeClass("hide");
        $("#score_value").html(score.toFixed(2));
        var progressBarWidth = Math.round((score.toFixed(2)/5 * 100)*100) / 100;
        $("#score_progress_bar").css({width: progressBarWidth.toFixed(0)+'%'})
        if(data.msg_type == "warning"){
          showMessage("#evaluation-message", data.msg, "alert-warning");
        } else {
          showMessage("#evaluation-message", data.msg, "alert-info");
        }

        if(data.idea_evaluated == 2){
          $('#salvar-parcial').attr('disabled', true);
          $('#salvar-total').attr('disabled', true);
          $('textarea').attr('disabled', 'true');
          $('select').attr('disabled', 'true');
        }

        topFunction();
      },
      error: function(xhr, status, error){
        showMessage("#evaluation-message", xhr.responseJSON.msg , "alert-danger");
      }
    });
  }

  var modalSubmitEvaluation = function(event){
    event.preventDefault()
    var button = $("input[type=submit][clicked=true]");
    if(button.attr("confirmation")=="true"){
      $("#mi-modal-save").modal('show');
      $("#LabelModalSave").html(button.data('string'));
      $("#modal-btn-yes").data('id', 1);
    }else{
      modalSubmitTotalEvaluation();
    }

    return false;
  };

  var markClickedSubmitEvaluationButton = function(event) {
    $("input[type=submit]").removeAttr("clicked");
    $(this).attr("clicked", "true");
  }

  //$(".js-create-idea").click(loadForm);
  //$("#modal-idea-crud").on("submit", ".js-idea-create-form", saveForm);

  //$(document).on("click", ".js-update-idea", loadForm);
  //$("#modal-idea-crud").on("submit", ".js-idea-update-form", saveForm);

  $(document).on("click", ".js-remove-idea", loadForm);
  $("#modal-idea-crud").on("submit", ".js-idea-remove-form", saveForm);

  $(".js-create-category").click(loadForm);
  $("#modal-category-crud").on("submit", ".js-category-create-form", saveForm);

  $(document).on("click", ".js-update-category", loadForm);
  $("#modal-category-crud").on("submit", ".js-category-update-form", saveForm);

  $(document).on("click", ".js-remove-category", loadForm);
  $("#modal-category-crud").on("submit", ".js-category-remove-form", saveForm);

  $(document).on("submit", "#evaluation_form", modalSubmitEvaluation);
  $(document).on("click",  "#salvar-total", markClickedSubmitEvaluationButton);
  $(document).on("click",  "#salvar-parcial", markClickedSubmitEvaluationButton);
  $(document).on("click",  "#modal-btn-yes-evaluation", modalSubmitTotalEvaluation);
  $(document).on("click", "#modal-btn-yes-evaluation", function(){
    $("#mi-modal-save").modal('hide');
  });

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

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $(document).on("click", 'button[name="following"]', function(){

    var $star = $(this).children()[0];
    var $label = $(this).children()[1];
    var data_prefix = $star.getAttribute("data-prefix");
    var idea_id = $label.getAttribute("idea-id");
    var action = data_prefix == "far" ? "follow" : "unfollow";

    console.log(idea_id)

    $.ajax({
      url: '/idea/ideafollow/',
      type: 'POST',
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      contentType: "application/json",
      data: JSON.stringify({action: action,"idea_id": idea_id}),
      success: function(result) {
        if(result["msg"] == "success"){
          if (action == "follow"){
            $star.setAttribute("data-prefix", "fas");
            $label.innerText = $label.getAttribute("following");
          } else {
            $star.setAttribute("data-prefix", "far");
            $label.innerText = $label.getAttribute("follow");
          }
        }
      }
    });
  });

  function submitEvent(event, form) {
    event.preventDefault();
    var $form = form;
    var data = $form.data();
    url = $form.attr("action");
    commentContent = $form.find("textarea#commentContent").val();

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
    });

    var doPost = $.post(url, {
        ideiaId : data.ideaId,
        parentId: data.parentId,
        commentContent: commentContent
    });

    doPost.done(function (response) {
        if (response.msg) {
            showMessage("#comment-message", response.msg, "alert-info");
        }
        $("#commentContent").val("");
        refreshCommentList(event, form)
    });

    doPost.fail(function (response){
      if (response.responseJSON.msg) {
          showMessage("#comment-message", response.responseJSON.msg, "alert-danger");
      }
    });
  }

  function searchIdea(event, form) {
    event.preventDefault();
    var $form = form;
    var data = $form.data();
    url = $form.attr("action");
    seach_filter = $form.find("input#search_part").val();

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
    });

    var doPost = $.post(url, {
      seach_filter: seach_filter
    });

    doPost.done(function (response) {

        $("#idea-list-group").empty();
        $(".empty-filter").empty();

        if(response.empty == 0){
          $(".empty-filter").empty();
          $("#idea-list-group").html(response.html_idea_list);
        }
        else{
          $(".empty-filter").empty();
          $(".empty-filter").html(response.html_idea_list);
        }
        ideaView(localStorage.getItem("ideaView"));
    });

    doPost.fail(function (response){

    });
  }

  function showMessage(idDivMessage, message, classMessage){
    $(idDivMessage).html(message);
    $(idDivMessage).css("display","");
    $(idDivMessage).removeClass("alert-danger").removeClass("alert-warning").addClass(classMessage);
  }

  function refreshCommentList(event, form){
    var urlRequest = '/idea/comments/' + form.data().ideaId;
    $.ajax({
      url: urlRequest,
      dataType: 'json',
      success: function (data){
        $("#comments-list").html(data.html_list);
        handleCommentsPermission();
      }
    });
  }

  $(document).on("submit", "#commentForm", function (event) {
    submitEvent(event, $(this));
  });

  $(document).on("submit", "#searchIdea", function (event) {
    searchIdea(event, $(this));
  });

  $(document).on("reset", "#searchIdea", function (event) {
    document.getElementById("search_part").value = "";
    searchIdea(event, $(this));
  });

  var newCommentForm = `
    <form id="commentFormReply" class="form-horizontal" action="/post/comment/">
      <div class="form-group">
        <label for="commentContent">Reply Comment</label>
        <textarea class="form-control" id="commentContent" rows="3"></textarea>
        <span id="postResponse" class="text-success" style="display: none"></span>
      </div>
      <div class="form-group">
        <button type="submit" class="btn btn-primary">Post Reply</button>
      </div>
    </form>
  `;
  // var newCommentForm = '<form id="commentFormReply" class="form-horizontal" \
  //                             action="/post/comment/"\
  //                             >\
  //                             <fieldset>\
  //                             <div class="form-group comment-group">\
  //                                 <label for="commentContent" class="col-lg-2 control-label">Reply</label>\
  //                                 <div class="col-lg-10">\
  //                                     <textarea class="form-control" rows="3" id="commentContent"></textarea>\
  //                                     <span id="postResponse" class="text-success" style="display: none"></span>\
  //                                 </div>\
  //                             </div>\
  //                             <div class="form-group">\
  //                                 <div class="col-lg-10 col-lg-offset-2">\
  //                                     <button type="submit" class="btn btn-primary">Comentar</button>\
  //                                 </div>\
  //                             </div>\
  //                         </fieldset>\
  //                     </form>';

  $(document).on("click", 'a[name="replyButton"]', function () {
    var $mediaBody = $(this).parent();
    if ($mediaBody.find('#commentFormReply').length == 0) {
        $mediaBody.parent().find(".reply-container:first").append(newCommentForm);
        var $form = $mediaBody.find('#commentFormReply');
        $form.data('idea-id', $(this).attr("data-idea-id"));
        $form.data('parent-id', $(this).attr("data-parent-id"));
        /*$form.on("submit", function (event) {
            submitEvent(event, $(this));
            refleshCommentList(event, $(this))

        });*/
    } else {
        $commentForm = $mediaBody.find('#commentFormReply:first');
        if ($commentForm.attr('style') == null) {
            $commentForm.css('display', 'none')
        } else {
            $commentForm.removeAttr('style')
        }
    }

  });

  $(document).on("click", "#modal-btn-no-comment", function(){
    $("#mi-modal").modal('hide');
  });

  $(document).on("click", '#modal-btn-yes-comment', function () {
    var $bottonDelete = $('a[data-parent-id='+ $(this).attr("data-parent-id") + '][name=replyDelete]');
    var $media_body = $bottonDelete.closest(".media-body");
    var $media = $media_body.parent();

    $.ajax({
      url: '/delete/comments/' + $bottonDelete.attr("data-parent-id") + '/',
      type: 'DELETE',
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function(result) {
        $media.remove();
        $("#mi-modal").modal('hide');
      }
    });


  });

  $(document).on("click", 'a[name="replyEdit"]', function () {
    var $card = $(this).closest(".card-body");
    var $textval = $card.children(".textval");
    var $textedit = $card.children(".textedit");
    var $textbuttons = $card.children(".textbuttons");
    var $editbuttons = $card.children(".editbuttons");
    var $rawtext = $textval.children("div").children("p");
    $textedit.children("textarea").val($rawtext[0].innerText);
    $textval.attr("hidden", true);
    $textedit.attr("hidden", false);
    $textbuttons.attr("hidden", true);
    $editbuttons.attr("hidden", false);
  });

  $(document).on("click", 'a[name="cancelEdit"]', function(){
    var $card = $(this).closest(".card-body");
    var $textval = $card.children(".textval");
    var $textedit = $card.children(".textedit");
    var $textbuttons = $card.children(".textbuttons");
    var $editbuttons = $card.children(".editbuttons");
    $textval.attr("hidden", false);
    $textedit.attr("hidden", true);
    $textbuttons.attr("hidden", false);
    $editbuttons.attr("hidden", true);
  });

  $(document).on("click", 'a[name="saveEdit"]', function(){
    var $card_body = $(this).closest(".card-body");
    var $card = $card_body.closest(".card");
    var $card_header = $card.find(".card-header");
    var $textval = $card_body.children(".textval");
    var $textedit = $card_body.children(".textedit");
    var $textbuttons = $card_body.children(".textbuttons");
    var $editbuttons = $card_body.children(".editbuttons");
    var $rawtext = $textedit.children("textarea");

    $.ajax({
      url: '/put/comments/' + $(this).attr("data-parent-id") + '/',
      type: 'PUT',
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      contentType: "application/json",
      data: JSON.stringify({text: $rawtext.val()}),
      success: function(result) {
        $textval.children("div").children("p").text($rawtext.val());
        $textval.attr("hidden", false);
        $textedit.attr("hidden", true);
        $textbuttons.attr("hidden", false);
        $editbuttons.attr("hidden", true);
        $card_header.find('h6').removeClass('hide');
      }
    });
  });

  $(document).on("submit", "#commentFormReply", function (event) {
    submitEvent(event, $(this));
  });

 $('iframe').load( function() {
    console.log("iframe css");
      $('iframe').contents().find("head").append($("<style type='text/css'>  .b-agent-demo .b-agent-demo_header{min-height:50px!important;height:50px!important}.b-agent-demo .b-agent-demo_header-icon{top:4px!important}.b-agent-demo .b-agent-demo_header-description{padding-top:0!important}  </style>"));
  });

});

function filterChallenges(url){
    $.ajax({
      url: url,
      type: 'get',
      dataType: 'json',
      success: function (data){
        $("#challenge-list-group").empty();
        $(".empty-filter").empty();

        if(data.empty == 0){
          $(".empty-filter").empty();
          $("#challenge-list-group").html(data.html_challenge_list);
        }
        else{
          $(".empty-filter").empty();
          $(".empty-filter").html(data.html_challenge_list);
        }
        ideaView(localStorage.getItem("ideaView"));
      }
    });
  };


function filterIdeas(url){
  $.ajax({
    url: url,
    type: 'get',
    dataType: 'json',
    success: function (data){
      $("#idea-list-group").empty();
      $(".empty-filter").empty();

      if(data.empty == 0){
        $(".empty-filter").empty();
        $("#idea-list-group").html(data.html_idea_list);
      }
      else{
        $(".empty-filter").empty();
        $(".empty-filter").html(data.html_idea_list);
      }
      $('#dropdownMenuButton span.default').removeClass('hide');
      $('#dropdownMenuButton span.option').addClass('hide');
      ideaView(localStorage.getItem("ideaView"));
    }
  });
};

$('body').on('click', 'li', function(ev) {
      $('li.active').removeClass('active');
      $('a.active').removeClass('active');
      ev.target.classList.add("active");
      $(this).addClass('active');
});

$('#idea-tab a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
})

$('#idea-pills-tab a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
})

//modal challenge
//var modalConfirmDeletion = function(callback){

    $(document).on("click", "#btn-confirm-deletion", function(){
        $("#mi-modal").modal('show');
    });

    $(document).on("click", "#modal-btn-yes", function(){
        //callback(true)
        $("#mi-modal").modal('hide');
    });

    $(document).on("click", "#modal-btn-no", function(){
        //callback(false)
        $("#mi-modal").modal('hide');
    });
//}

// tooltip functions

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

$(function () {
  $('[data-toggle="tooltip"]').tooltip({ trigger: 'click' });
});

// end of tooltip functions

$("#evaluation_form button").click(function(){
  if($(window).scrollTop() > $("#idea-tab").offset().top){
       $('html, body').animate({
          scrollTop: $("#idea-tab").offset().top
      }, 500);
    }
    console.log($("#evaluation-message").offset().top);
  $("#evaluation").animate({
          scrollTop: 0
      }, 500);
});

$(window).scroll(function() {
    if ($(this).scrollTop() > 50 ) {
        $('.scrolltop:hidden').stop(true, true).fadeIn();
    } else {
        $('.scrolltop').stop(true, true).fadeOut();
    }
});
$(function(){$(".scroll").click(function(){$("html,body").animate({scrollTop:$(".thetop").offset().top},"1000");return false})})


//sort ideas

$('a.ideaSort').click(function () {
    var $divs = $(".infinite-item");

    if(this.name == 'thumbsUp'){
        var thumbsUpOrderedDivs = $divs.sort(function (a, b) {
             return $(b).find('.liked_votes').text() - $(a).find('.liked_votes').text();
        });
        $("#idea-list-group").html(thumbsUpOrderedDivs);
    }

    else if(this.name == 'thumbsDown'){
        var thumbsDownOrderedDivs = $divs.sort(function (a, b) {
            return $(b).find('.disliked_votes').text() - $(a).find('.disliked_votes').text();
        });
        $("#idea-list-group").html(thumbsDownOrderedDivs);
    }

    else if(this.name=='comments'){
        var CommentsOrderedDivs = $divs.sort(function (a, b) {
            return $(b).find('.comments').text() - $(a).find('.comments').text();
        });
        $("#idea-list-group").html(CommentsOrderedDivs);
    }

    else if(this.name=='alphabetic'){
        var alphabeticOrderedDivs = $divs.sort(function (a, b) {
            a = $(a).find('.card-title').text() + '';
            b = $(b).find('.card-title').text();
            return (a).localeCompare(b);

        });
        $("#idea-list-group").html(alphabeticOrderedDivs);
    }
    else if(this.name=='creationOrder'){
        var creationDateOrderedDivs = $divs.sort(function (a, b) {
            return $(b).find('.creation-order').text() - $(a).find('.creation-order').text();
        });
        $("#idea-list-group").html(creationDateOrderedDivs);
    }
    $('#dropdownMenuButton span.option').text($(this).text());
    $('#dropdownMenuButton span.default').addClass('hide');
    $('#dropdownMenuButton span.option').removeClass('hide');
});

//end of sort ideas

//toggle grid/list view

$('a#list-view').click(function(){
    localStorage.setItem("ideaView", "1");
    ideaView(localStorage.getItem("ideaView"));
});

$('a#grid-view').click(function(){
    localStorage.setItem("ideaView", "0");
    ideaView(localStorage.getItem("ideaView"));
});


function ideaView(ideaView){
     if (ideaView == 1) {
        $('.card').removeClass('grid-item');
        $('.idea-cards').css('flex-direction','row');
        $('.idea-cards').addClass('mb-2');
        $('.card-img-top').addClass('m-2');
        $('.card-body').addClass('w-50');
        $('.card-footer').addClass('card-footer-list');
        $('.card-text').css('height', '86px');
        $('.card-icons').css('position', 'relative');
        $('.card-icons').css('bottom', '12px');
    }else{
        $('.card').addClass('grid-item');
        $('.idea-cards').css('flex-direction','column');
        $('.idea-cards').removeClass('mb-2');
        $('.card-img-top').removeClass('m-2');
        $('.card-body').removeClass('w-50');
        $('.card-footer').removeClass('card-footer-list');
        $('.card-text').css('height', "")
        $('.card-icons').css('position', 'absolute');
        $('.card-icons').css('bottom', '40px');
     }
}

/* SCRIPT TO HANDLE COMMENTS PERMISSION */
var handleCommentsPermission = function(){
  if($('#commentsPermission').length){
    if($('#commentsPermission')[0].getAttribute('comments_edit_permision') == 'manager'){
      $.map($("a[name=replyEdit]"), function(val){
          val.removeAttribute("hidden");
      })
      $.map($("a[name=replyDelete]"), function(val){
        val.removeAttribute("hidden");
      })
    }

    if($('#commentsPermission')[0].getAttribute('comments_edit_permision') == 'partial'){
      var idList = $('#commentsPermission')[0].getAttribute('comments_id_list').split(",").map(Number)
      $.map(idList, function(val){
        $.map($("a[data-parent-id="+val+"]"), function(element){
          element.removeAttribute("hidden");
        })
      })
    }
  }
}

/* Button salvar-parcial disabled means evalution finished*/
$(document).ready(function(){
  if($('#salvar-parcial').is('[disabled]')){
    $('textarea').attr('disabled', 'true');
    $('select').attr('disabled', 'true');
  }
})

$(document).ready(function(){
  handleCommentsPermission();
})

/* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
$(document).ready(function (){
    $("#id_image").change(function () {
        if (this.files && this.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
        $("#image").attr("src", e.target.result);
        $("#modalCrop").modal("show");
        }
        reader.readAsDataURL(this.files[0]);
        }
    });

        /* SCRIPTS TO HANDLE THE CROPPER BOX */
        var $image = $("#image");
        var cropBoxData;
        var canvasData;
    $("#modalCrop").on("shown.bs.modal", function () {
        $image.cropper({
        viewMode: 1,
        movable: true,
        zoomable: true,
        rotatable: false,
        scalable: false,
        aspectRatio: 4.5/1,
        minCropBoxWidth: 50,
        minCropBoxHeight: 20,
        ready: function () {
        $image.cropper("setCanvasData", canvasData);
        $image.cropper("setCropBoxData", cropBoxData);
        }
        });
    }).on("hidden.bs.modal", function () {
        cropBoxData = $image.cropper("getCropBoxData");
        canvasData = $image.cropper("getCanvasData");
        $image.cropper("destroy");
        });

        $(".js-zoom-in").click(function (e) {
          e.preventDefault()
          $image.cropper("zoom", 0.1);
        });

        $(".js-zoom-out").click(function (e) {
          e.preventDefault()
          $image.cropper("zoom", -0.1);
        });

        $(".js-crop-and-upload").click(function (e) {
            e.preventDefault()
            var cropData = $image.cropper("getData");
            $("#id_x").val(cropData["x"]);
            $("#id_y").val(cropData["y"]);
            $("#id_height").val(cropData["height"]);
            $("#id_width").val(cropData["width"]);
            $("#modalCrop").modal('hide');
            //$("#formUpload").submit();
        });
});

function dismissAll(){
    console.log("dismissAll")
    $.ajax({
        url: '/notifications/dismiss/',
        dataType: 'json',
        success: function (data) {

        var notifHtml = '<ul style="padding: 5px;">No new notifications!</ul>'
        $('#notificationsDropdownMenu').html(notifHtml);
        $('#notificationCount').text("0");
        }
    });
}
//end of toggle grid/list view

//chatbot
