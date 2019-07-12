// Javascript file for hours.html. Allows for hiding items when scrolling and calls to 
// database for athlete hours.

$(document).ready(function () {

    $(window).scroll(function () {
    if ($(this).scrollTop() > 25) {
      $('#datetimepickerStart').fadeOut('fast');
      $('#datetimepickerEnd').fadeOut('fast');
      $('#dataSubmitButton').fadeOut('fast');
      $('#main-text').fadeOut('fast');
    } else {
      $('#datetimepickerStart').fadeIn('fast');
      $('#datetimepickerEnd').fadeIn('fast');
      $('#dataSubmitButton').fadeIn('fast');
      $('#main-text').fadeIn('fast');
      
    }
  });

    $('#spinner').hide();
    $(document).on({
        ajaxStart: function () {
            $('#submitLabel').html("Loading...");
            $('#spinner').show();
        },
        ajaxStop: function () {
            $('#submitLabel').html("Get Hours");
            $('#spinner').hide();
            // $('#datetimepickerStart').hide();
            // $('#datetimepickerEnd').hide();
            // $('#dataSubmitButton').hide();
        }
    });

    // Ajax makes a call to go to hours/getData (a function in our routes.py)
    // getData then calls getHoursForAllAthletes from  hours_helper with start data and end date
    // This returns len of athletes and the athletes which getData renders into a template data.html
    // If it is a success ajax returns this data.html template. 
    $("#dataSubmitButton").click(function (e) {
        e.preventDefault();
        $.ajax({
            url: "/hours/getData",
            type: "get",
            data: {
                'start_date': $("#startDateInput").val(),
                'end_date': $("#endDateInput").val()
            },
            success: function (response) { 
                $("#hours-table-div").html(response);
            },
            error: function (xhr) {
                //handle error
            }
        });
    });
    

    $(function () {
        $('#datetimepickerStart').datetimepicker({
            format: 'L'
        });
        $('#datetimepickerEnd').datetimepicker({
            format: 'L',
            useCurrent: false
        });
        $("#datetimepickerStart").on("change.datetimepicker", function (e) {
            $('#datetimepickerEnd').datetimepicker('minDate', e.date);
        });
        $("#datetimepickerEnd").on("change.datetimepicker", function (e) {
            $('#datetimepickerStart').datetimepicker('maxDate', e.date);
        });
    });
});

