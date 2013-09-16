/**
 * Created with PyCharm.
 * User: aub3
 * Date: 9/16/13
 * Time: 3:35 PM
 * To change this template use File | Settings | File Templates.
 */
        var current_results = [];

        function submit(){
            q =$('#query');
                $.ajax({
                  dataType: "json",
                  url: '/Search/',
                  data: {'q':q.val(),'project_type':$('#project_type').val()},
                  success: function(response,status){current_results.push(response);}
                   });
            q.val("");
            return false;
        };
