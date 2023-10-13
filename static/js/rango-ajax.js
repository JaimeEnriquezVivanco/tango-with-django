$(document).ready(function(){
  $("#like_button").on("click", function(){
    // when like button is clicked
    // increases like count and hides like button
    var category_id = $(this).attr('data-categoryId');
    var r = {'category_id': category_id};
    
    function success_handler(server_response){
      $('#number_of_likes').html(server_response);
      $('#like_button').hide();
    }
    
    $.get(
      '/rango/like_category/', //url. view to call to do logic
      r, //data. key-value pairs that make up the GET request/query
      success_handler, //handler. is called and passed 'server_response' at some moment
    )
  });
  
  $("#search-input").on("keyup", function(){
    var typed_query = $(this).val();
    var query_dic = {'suggestion_query': typed_query};

    function populate_sidebar(response){
      $('#categories-list').html(response)
    }

    $.get('/rango/suggest/', query_dic, populate_sidebar)
  });

  $(".add-result-button").on('click', function(){
    var category_name = $('#category').text();
    var wanted_result = $(this).parent();
    var result_title = wanted_result.children('a').text();
    var result_url = wanted_result.children('a').attr('href');
    
    request_dic = {
      'category_name': category_name,
      'title': result_title,
      'url': result_url
    };

    function update_category_pages(response){
      $('#category-pages').html(response)
    };

    $.get('/rango/add_search_result/', request_dic, update_category_pages);
  });
});

