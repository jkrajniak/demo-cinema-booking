'use strict';

var myApplication = {
    selectNumSeats: function() {
        $("#step3").show();
        $("#num-seats").text($(this).val());
        myApplication.selectedNumSeats = parseInt($(this).val());
        return true;
    },

    selectSeats: function() {
        var seatId = parseInt($(this).attr("data-seat-num"));
        if (seatId + myApplication.selectedNumSeats <= myApplication.total_num_seats) {
            $("td.seats").removeClass('clicked');  // clear all selected cells.
            for (var s = seatId; s < seatId + myApplication.selectedNumSeats; s++) {
                $("td#seat-" + s).addClass('clicked');
            }
        }
    },

    drawAuditorium: function(auditorium_data) {
        if (auditorium_data) {
            myApplication.auditorium_id = auditorium_data.auditorium_id;
            myApplication.total_num_seats = auditorium_data.total_num_seats;

            $("#auditorium-name").text(auditorium_data.auditorium_name);
            $("#movie-name").text(auditorium_data.title);
            $("#movie-time").text(auditorium_data.movie_time);
            $("#auditorium-grid").empty();

            // Draw grid (using table, but maybe canvas will be better...)
            var nRows = auditorium_data.rows;
            var nCols = Math.ceil(auditorium_data.total_num_seats / nRows);
            nCols++;  // one more column for row name
            nRows++;  // one more row for column name
            var tab = $("<table class='grid'>");
            tab.append($('<tr><td class="empty"></td><td class="grid-screen" colspan="' + nCols + '">SCREEN</td>'))
            var seatNumber = 0;
            for (var ni = 0; ni < nRows; ni++) {
                var row = $("<tr>");
                for (var nj = 0; nj < nCols; nj++) {
                    if (nj === 0) {
                        var td = $('<td class="row-name empty">' + String.fromCharCode(65 + ni) + '</td>');
                    } else if (ni == nRows - 1) {
                        var td = $('<td class="row-name empty">' + (nj) + '</td>');
                    } else if (seatNumber >= myApplication.total_num_seats) {
                        var td = $('<td class="empty"></td>');
                    } else {
                        var td = $("<td id='seat-" + seatNumber + "' class='seats' data-seat-num='" + seatNumber + "'></td>");
                        td.click(myApplication.selectSeats);
                        seatNumber++;
                    }
                    row.append(td);
                }
                tab.append(row)
            }
            $("#auditorium-grid").append(tab);
        }
    },
    selectScreening: function() {
        var screeing_id = $(this).find('option:selected').attr("data-screening-id");
        $.get("/get_screening/" + screeing_id, function (data) {
            myApplication.drawAuditorium(data);
        });
        $("select#screening").prop('disabled', true);
        $("#step2").show();
        return true;
    }
};

$(document).ready(function(){
    $("select#screening").click(myApplication.selectScreening);
    $("select#num_seats").click(myApplication.selectNumSeats);
});