// Javascript file for hours.html. Allows for hiding items when scrolling and calls to 
// database for athlete hours.

  var $table = $('#table')
  var firstTime = 1

  function getLastWeek() {
    var today = new Date();
    var lastWeek = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 7);
    var lastWeekMonth = lastWeek.getMonth() + 1;
    var lastWeekDay = lastWeek.getDate();
    var lastWeekYear = lastWeek.getFullYear();
    var lastWeekDisplayPadded = ("00" + lastWeekMonth.toString()).slice(-2) + "/" + ("00" + lastWeekDay.toString()).slice(-2) + "/" + ("0000" + lastWeekYear.toString()).slice(-4);
    return lastWeekDisplayPadded
    }
  function getToday() {
    var today = new Date();
    var todayMonth = today.getMonth()+1
    var todayDate = today.getDate()
    var todayYear = today.getFullYear()
    var lastWeek = getLastWeek();
    var todayDisplayPadded = ("00" + todayMonth.toString()).slice(-2) + "/" + ("00" + todayDate.toString()).slice(-2) + "/" + ("0000" + todayYear.toString()).slice(-4);
    return todayDisplayPadded
  }

  function rowAttributes(row, index) {
    return {
      'data-toggle': 'popover',
      'data-placement': 'bottom',
      'data-trigger': 'hover',
      'data-content': [
        'Rank: ' + row.rank,
        'Name: ' + row.name,
        'Hours: ' + row.rounded_hours
      ].join(', ')
    }
  }


  function ajaxRequest(params) {
    // previous code that worked
    // var url = '/hours/getData'
    // $.get(url + '?' + $.param(params.data)).then(function (response) {
    //   params.success(response)
    // })
    $.ajax({
           url: '/hours/getData',
           type: "get",
           dataType: 'json',
           data: getData(), 
           success: function(response) {
               // alert('done');
               params.success(response)
           },
           error: function(e) {
              // alert('failure')
              console.log(e.responseText);
           }
        });
  }

    $(function() {
    $('#dataSubmitButton').click(function () {
      alert("refresh")
      firstTime = 0
      $('#table').bootstrapTable('refresh')
    })
  })

  function getData() {
    var on_load_start = getToday()
    var on_load_end = getLastWeek()
    // alert(firstTime)
    var data = {
                    'start_date': on_load_start,
                    'end_date': on_load_end
                }
    if (!firstTime) {
      alert($("#to").val())
      data = {
                'start_date': $("#to").val(),
                'end_date': $("#from").val()
              }
    }

    return data
  }

// DateRange
$(function() {
    var start = moment().subtract(29, 'days');
    var end = moment();

    function cb(start, end) {
        // alert("Callback has been called!");
        $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        $('#to').val(start.format('MM/DD/YYYY'));
        $('#from').val(end.format('MM/DD/YYYY'));
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
           'Last 7 Days': [moment().subtract(6, 'days'), moment()],
           'Last 30 Days': [moment().subtract(29, 'days'), moment()],
           'This Month': [moment().startOf('month'), moment().endOf('month')],
           'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, cb);

    cb(start, end);

});

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

        $(function() {
    $('#table').on('post-body.bs.table', function (e) {
      $('[data-toggle="popover"]').popover()
    })
  })



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

