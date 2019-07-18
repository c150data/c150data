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

});

