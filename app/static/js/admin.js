// Javascript file for admin page. Allows for calls to database
// to put workouts in database.

$(document).ready(function() {
    $('#spinner').hide();
    $(document).on({
        ajaxStart: function() {
            $('#submitLabel').html("Loading...");
            $('#spinner').show();
        },
        ajaxStop: function() {
            $('#submitLabel').html("Insert Workouts!");
            $('#spinner').hide();
        }
    });

    $("#insertAllWorkoutsButton").click(function(e) {
        e.preventDefault();
        $.ajax({
            url: "/admin/insertAllWorkouts",
            type: "get",
            data: {
                'start_date': $("#start_date").val(),
                'end_date': $("#end_date").val()
            },
            success: function(response) {
                $("alert-div").html(response)
            },
            error: function(xhr) {
                //handle error
            }
        });
    });

    $("#insertWhoopAthlete").click(function(e) {
        e.preventDefault();
        $.ajax({
            url: "/admin/insertWhoopAthlete",
            type: "get",
            data: {
                'username': $("#whoop_username").val(),
                'password': $("#whoop_password").val()
            },
            success: function(response) {
                $("alert-div").html(response)
            },
            error: function(xhr) {
                //handle error
            }
        });
    });
});
