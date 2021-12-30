(function($) {
    $('#load_stories').on('click', function() {
      let link = $(this);
      let page = link.data('page');
      $.ajax({
        type: 'POST',
        url: '/load_stories/',
        data: {
          'page': page,
          'csrfmiddlewaretoken': window.CSRF_TOKEN // from index.html
        },
        success: function(data) {
          // if there are still more pages to load,
          // add 1 to the "Load More Posts" link's page data attribute
          // else hide the link
          if (data.has_next) {
              link.data('page', page+1);
          } else {
            link.hide();
          }
          // append html to the posts div
          $('#div').append(data.posts_html);
        },
        error: function(xhr, status, error) {
          // shit happens friends!
        }
      });
    });
  }(jQuery));