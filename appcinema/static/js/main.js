'use strict';

var myApplication = {
    selectNumSeats: function () {
        $("#step3").show();
        $("#num-seats").text($(this).val());
        myApplication.selectedNumSeats = parseInt($(this).val());
        return true;
    },

    selectSeats: function () {
        var seatId = parseInt($(this).attr("data-seat-num"));
        if (seatId + myApplication.selectedNumSeats <= myApplication.auditorium.total_num_seats) {
            if (myApplication.currentReservationId == null) {
                // TODO(jakub): report error, something went wrong.
            }
            var valid = true;
            // Check if the seats that we would like to reserve are not blocked already
            for (var s = seatId; (s < seatId + myApplication.selectedNumSeats) && valid; s++) {
                valid = valid && !myApplication.blockedSeatsList.has(s);
            }
            if (!valid)
                return false;

            // Seat block should be continuous in a single row.
            var row1 = Math.floor(seatId / myApplication.auditorium.cols);
            var row2 = Math.floor((seatId + myApplication.selectedNumSeats - 1) / myApplication.auditorium.cols);
            if (row1 != row2)
                return false;

            var params = {
                id: myApplication.currentReservationId,
                start_seat_block: seatId,
                seat_block_size: myApplication.selectedNumSeats,
                screening: myApplication.screening_id
            };
            // we have reservation block, only update it
            var action = ["reservation", "update"];
            myApplication.client.action(schema, action, params).then(function (result) {
                myApplication.currentReservationSeatBlockId = result.id;

                $("td.seats").removeClass('clicked');  // clear all selected cells.
                for (var s = seatId; s < seatId + myApplication.selectedNumSeats; s++) {
                    $("td#seat-" + s).addClass('clicked');
                }
            }).catch(function (error) {
                console.log(error);
                //TODO(jakub): report or do something, should not happen.
            });
        }
    },

    blockSeats: function(data) {
        Object.keys(data).forEach(function(key) {
            var seat_data = data[key];
            for (var s = seat_data.start_seat_block; s < seat_data.start_seat_block + seat_data.seat_block_size; s++) {
                $("td#seat-" + s).addClass('blocked').unbind("click");
                myApplication.blockedSeatsList.add(s);
            }
        });
    },

    drawAuditorium: function (auditorium_data) {
        if (auditorium_data) {
            myApplication.auditorium.id = auditorium_data.auditorium_id;
            myApplication.auditorium.total_num_seats = auditorium_data.total_num_seats;
            myApplication.screening_id = auditorium_data.id;

            $("#auditorium-name").text(auditorium_data.auditorium_name);
            $("#movie-name").text(auditorium_data.title);
            $("#movie-time").text(auditorium_data.movie_time);
            var auditorium_grid = $("#auditorium-grid");
            auditorium_grid.empty();

            // Draw grid (using table, but maybe canvas will be better...)
            var nRows = auditorium_data.rows;
            var nCols = Math.ceil(auditorium_data.total_num_seats / nRows);
            myApplication.auditorium.rows = nRows;
            myApplication.auditorium.cols = nCols;

            nCols++;  // one more column for row name
            nRows++;  // one more row for column name
            var tab = $("<table class='grid'>");
            tab.append($('<tr><td class="empty"></td><td class="grid-screen" colspan="' + nCols + '">SCREEN</td>'))
            var seatNumber = 0;
            for (var ni = 0; ni < nRows; ni++) {
                var row = $("<tr>");
                for (var nj = 0; nj < nCols; nj++) {
                    if (nj === 0 && ni < nRows - 1) {
                        var td = $('<td class="row-name empty">' + String.fromCharCode(65 + ni) + '</td>');
                    } else if (ni === nRows - 1 && nj > 0) {
                        var td = $('<td class="row-name empty">' + (nj) + '</td>');
                    } else if ((nj === 0 && ni === nRows - 1) || (seatNumber >= myApplication.auditorium.total_num_seats)) {
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
            auditorium_grid.append(tab);
            myApplication.blockSeats(auditorium_data.blocked_seats);
        }
    },
    selectScreening: function () {
        // Create reservation object.
        var screeing_id = $(this).find('option:selected').attr("data-screening-id");
        var action = ["reservation", "create"];
        var params = {screening: screeing_id, confirmed: false};
        myApplication.client.action(schema, action, params).then(function (result) {
            myApplication.currentReservationId = result.id;
            $.get("/get_screening/" + screeing_id, function (data) {
                myApplication.drawAuditorium(data);
            });
            $("select#screening").prop('disabled', true);
            $("#step2").show();
        }).catch(function(error){
            //TODO(jakub): handle exception when reservation cannot be started.
        });

        return true;
    },

    init: function () {
        myApplication.currentReservationId = null;
        myApplication.blockedSeatsList = new Set();
        myApplication.auditorium = {
            id: null,
            rows: null,
            cols: null,
            total_num_seats: null
        };
        myApplication.screening_id = null;

        Pusher.logToConsole = true;
        myApplication.pusher = new Pusher('c6c88f0bd9523ee60c3e', {
            cluster: 'eu',
            encrypted: true
        });

        // Subscribe for the updates.
        var channel = myApplication.pusher.subscribe('appcinema-reservation');

        channel.bind('seats-selected', function (data) {
            consle.log(data.message);
        });

        // handle events
        $("select#screening").click(myApplication.selectScreening);
        $("select#num_seats").click(myApplication.selectNumSeats);

        // CoreAPI REST requests
        var auth = new coreapi.auth.SessionAuthentication({
            csrfCookieName: 'csrftoken',
            csrfHeaderName: 'X-CSRFToken'
        });
        myApplication.client = new coreapi.Client({auth: auth})
    }
};

$(document).ready(function () {
    myApplication.init();
});