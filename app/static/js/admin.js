$(document).ready(function () {
    $('#spinner').hide();
    $(document).on({
        ajaxStart: function () {
            $('#submitLabel').html("Loading...");
            $('#spinner').show();
        },
        ajaxStop: function () {
            $('#submitLabel').html("Insert all workouts!");
            $('#spinner').hide();
        }
    });

    $("#insertAllWorkoutsButton").click(function (e) {
        e.preventDefault();
        $.ajax({
            url: "/admin/insertAllWorkouts",
            type: "get",
            data: {
                'start_date': $("#startDateInput").val(),
                'end_date': $("#endDateInput").val()
            },
            success: function (response) {
                $("#alert-div").html(response)
            },
            error: function (xhr) {
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