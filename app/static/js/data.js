// Javascript file for data.html. Allows for hiding items when scrolling and calls to 
// database for athlete hours.

  var $table = $('#table')
  var firstTime = 1
  var total = 0

  // Date Functions

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

  function getData() {
    var on_load_start = getToday()
    var on_load_end = getLastWeek()
    // alert(firstTime)
    var data = {
                    'start_date': on_load_start,
                    'end_date': on_load_end
                }
    if (!firstTime) {
      data = {
                'start_date': $("#to").val(),
                'end_date': $("#from").val()
              }
        }
    return data
  }

  // DateRange
$(function() {
    var start = moment().subtract(6, 'days');
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
           'This Month to Now': [moment().startOf('month'), moment()],
           'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
           '2018/19 Season to Now': [new Date(2018, 8, 6), moment().endOf('month')],
           '2017/18 Season': [new Date(2017, 8, 6), new Date(2018, 5, 12)]
        }
    }, cb);

    cb(start, end);

});

// Bootstrap Table Functions

// Enables hover for detail in Bootstrap table
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

// Formatters for the footer row in table
  function rankFormatter() {
    return 'Total'
  }

  function nameFormatter(data) {
    return '# of Athletes: '+String(data.length)
  }

  function hoursFormatter() {
    return total
    }

// GET requests for to /data/getData which returns a json object called "response".
// On success this gets passed into the table along with the total hours 
// On error it logs the failure to the console
  function ajaxRequest(params) {
    $.ajax({
           url: '/data/getData',
           type: "get",
           dataType: 'json',
           data: getData(),
           success: function(response) {
               total = response['total_hours']
               params.success(response['athlete_list'], response['total_hours']);
           },
           error: function(e) {
              // alert('failure')
              console.log(e.responseText);
           }
        });
  }

// Every time you press the submit button it refreshes the table
// TODO: Build in a constraint as failsafe of user pressing repeatedly
    $(function() {
    $('#dataSubmitButton').click(function () {
      alert("refresh")
      firstTime = 0
      $('#table').bootstrapTable('refresh')
    })
  })


$(document).ready(function () {

    $('#spinner').hide();
    $(document).on({
        ajaxStart: function () {
            $('#submitLabel').html("Loading...");
            $('#spinner').show();
        },
        ajaxStop: function () {
            $('#submitLabel').html("Get Data!");
            $('#spinner').hide();
        }
    });

    // Additional function to enable table hover functionality
    $(function() {
        $('#table').on('post-body.bs.table', function (e) {
            $('[data-toggle="popover"]').popover()
        })
    })

});

