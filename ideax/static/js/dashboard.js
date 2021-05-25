//sort dashboard

$('a#dashboardSort').click(function () {

     var $divs = $(".staff-item");
     if(this.name == 'thumbsUp'){
         var mostLikesOrderedDivs = $divs.sort(function (a, b) {
             return $(a).data('like') < $(b).data('like');
         });
         $("#innovator-container").html(mostLikesOrderedDivs);
         $(".staff-item").wrapAll($("<section id='innovator-container'class='staff-card'></section>"));
    }
     else if(this.name == 'thumbsDown'){
         var mostDislikesOrderedDivs = $divs.sort(function (a, b) {
             return $(a).data('dislike') < $(b).data('dislike');
         });
         $("#innovator-container").html(mostDislikesOrderedDivs);
         $(".staff-item").wrapAll($("<section id='innovator-container'class='staff-card'></section>"));
    }

      else if(this.name == 'collaborators'){
          var maisIdeasOrderedDivs = $divs.sort(function (a, b) {
              return $(a).find('.qtdIdeas').text() < $(b).find('.qtdIdeas').text()
          });
          $("#innovator-container").html(maisIdeasOrderedDivs);
          $(".staff-item").wrapAll($("<section id='innovator-container'class='staff-card'></section>"));
     }

     $('#dropdownMenuButton span.option').text($(this).text());
});
