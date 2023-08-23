$(document).ready(function () {
    $('.add_hour').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value

        console.log(day, from_hour, to_hour, is_closed, csrf_token)
        if(is_closed){
            is_closed ='True'
            condition = "day != ''"
        }else{
            is_closed = 'False'
            condition = "day != '' && from_hour != '' && to_hour != ''"

        }
        if(eval(condition)){
            $.ajax({
                type:'POST',
                url:url,
                data:{
                    'day':day,
                    'from_hour':from_hour,
                    'to_hour':to_hour,
                    'is_closed':is_closed,
                    'csrfmiddlewaretoken':csrf_token,


                },
                success:function(response){
                    if(response.status =='success'){
                        if(response.is_closed == 'Closed'){
                            html =   '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>' 
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hour +' - '+response.to_hour+'</td><td><a href="" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>' 

                        }
                       
                        $(".opening_hours").append(html)
                        document.getElementById('opening_hours').reset();

                    }else{
                        console.log(response.error)
                        swal(response.message,'','error')
                    }
                }
            })
        }else{
           swal('please fill the details','','info')
        }

    });

    //REMOVE OPENING HOUR 


    $(document).on('click','.remove_hour',function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        console.log(url)
        $.ajax({
            type:'GET',
            url:url,
            success:function(response){
                if(response.status=='success'){
                    document.getElementById('hour-'+response.id).remove()
                }

            }

        })
    })

});