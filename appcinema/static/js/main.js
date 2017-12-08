'use strict';

var myTools = {
    /**
     * Set timer.
     * @param duration Duration in seconds.
     * @param display jQuery element to update.
     * @param onFinish callback function to call after finished.
     */
    setTimer: function (duration, display, onFinish) {
        var start = Date.now();
        var interval = null;

        function timer() {
            var diff = duration - (((Date.now() - start) / 1000) | 0);
            var minutes = (diff / 60) | 0;
            var seconds = (diff % 60) | 0;

            // Finished
            if (minutes === 0 && seconds === 0) {
                clearInterval(interval);
                onFinish();
            }

            // padding with zeros
            if (minutes < 10)
                minutes = "0" + minutes;
            if (seconds < 10)
                seconds = "0" + seconds;

            display.text(minutes + ":" + seconds);
            if (diff <= 0)
                start = Date.now() + 1000;
        };
        timer();
        interval = setInterval(timer, 1000);
        return interval;
    }
};

var ReservationStatus = {
    CANCELED: -1,
    TENTATIVE: 0,
    CONFIRMED: 1,
    BOOKED: 2
};

var myApplication = {
    reserveSeats: function (seatId) {
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

        // Update local storage with selected seats.
        myApplication.selectedSeatsList.clear();
        for (var s = seatId; (s < seatId + myApplication.selectedNumSeats) && valid; s++) {
            myApplication.selectedSeatsList.add(s);
        }

        // Update the reservation with new values of seats.
        var params = {
            id: myApplication.currentReservationId,
            start_seat_block: seatId,
            seat_block_size: myApplication.selectedNumSeats,
            screening: myApplication.screening.id
        };
        // we have reservation block, only update it
        var action = ["reservation", "update"];
        myApplication.client.action(schema, action, params).then(function () {
            $("td.seats").removeClass("clicked");  // clear all selected cells.
            for (var s = seatId; s < seatId + myApplication.selectedNumSeats; s++) {
                $("td#seat-" + s).addClass("clicked");
            }
        }).catch(function (error) {
            console.log(error);
            //TODO(jakub): report or do something, should not happen.
        });
    },

    cancelReservation: function (callback, error) {
        // Cancel reservation when timer finished.
        var action = ["reservation", "update"];
        var params = {
            id: myApplication.currentReservationId,
            screening: myApplication.screening.id,
            status: ReservationStatus.CANCELED
        };
        myApplication.client.action(schema, action, params).then(callback).catch(error);
    },

    confirmReservation: function(callback, error) {
        var action = ["reservation", "update"];
        var params = {
            id: myApplication.currentReservationId,
            screening: myApplication.screening.id,
            status: ReservationStatus.CONFIRMED
        };
        myApplication.client.action(schema, action, params).then(callback).catch(error);
    },

    selectSeats: function () {
        var seatId = parseInt($(this).attr("data-seat-num"));
        if (seatId + myApplication.selectedNumSeats <= myApplication.auditorium.total_num_seats) {
            if (myApplication.currentReservationId == null) {
                // reservation not made, do it first time and start the clock
                var action = ["reservation", "create"];
                var params = {
                    screening: myApplication.screening.id,
                    status: ReservationStatus.TENTATIVE
                };
                myApplication.client.action(schema, action, params).then(function (result) {
                    myApplication.currentReservationId = result.id;
                    myApplication.timer = myTools.setTimer(2 * 60, $("span#timer"), function () {
                        // Cancel reservation when timer finished.
                        myApplication.cancelReservation(function (result) {
                            alert("Session expired. Reload");
                            myApplication.init();
                        });
                    });
                    myApplication.reserveSeats(seatId);
                }).catch(function (error) {
                    //TODO(jakub): handle exception when reservation cannot be started.
                });
            } else {
                myApplication.reserveSeats(seatId);
            }
        }
    },

    /**
     * Update grid with seats and marked the one that are blocked.
     * @param data
     */
    blockSeats: function (data) {
        myApplication.blockedSeatsList.clear();
        $("td.seats").removeClass("blocked");
        Object.keys(data).forEach(function (key) {
            var seat_data = data[key];
            for (var s = seat_data.start_seat_block; s < seat_data.start_seat_block + seat_data.seat_block_size; s++) {
                if (myApplication.selectedSeatsList.has(s))
                    continue;
                $("td#seat-" + s).addClass("blocked").unbind("click");
                myApplication.blockedSeatsList.add(s);
            }
        });
    },

    drawAuditorium: function (auditorium_data) {
        if (auditorium_data) {
            myApplication.auditorium.id = auditorium_data.auditorium_id;
            myApplication.auditorium.total_num_seats = parseInt(auditorium_data.total_num_seats);
            myApplication.auditorium.name = auditorium_data.auditorium_name;
            myApplication.screening.id = auditorium_data.id;
            myApplication.screening.title = auditorium_data.title;
            myApplication.screening.datetime = new Date(auditorium_data.movie_time);

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

    resetGUI: function() {
        $("#step2").hide();
        $("#step3").hide();
        var select_screening = $("select#screening");
        select_screening.prop('disabled', false);
        clearInterval(myApplication.timer);
        $("span#timer").text("2:00");
    },

    initGUI: function () {
        myApplication.resetGUI();
        // handle events
        var select_screening = $("select#screening");
        select_screening.click(function () {
            // Create reservation object.
            var screeing_id = $(this).find('option:selected').attr("data-screening-id");
            $.get("/get_screening/" + screeing_id, function (data) {
                myApplication.drawAuditorium(data);
            });
            // $("select#screening").prop('disabled', true);
            $("#step2").show();

            return true;
        });
        $("select#num_seats").click(function () {
            $("#step3").show();
            $("#num-seats").text($(this).val());
            myApplication.selectedNumSeats = parseInt($(this).val());
            return true;
        });

        // handle reserva and cancel buttons
        $(".btn#reserve").click(function () {
            $("#reservationWindow").modal('show');
            $("#movieName").text(myApplication.screening.title);
            $("#screeningDateTime").text(myApplication.screening.datetime.format("dddd, mmmm dS, yyyy, h:MM"));
            $("#auditoriumName").text(myApplication.auditorium.name);
            var seatsList = new Array();
            myApplication.selectedSeatsList.forEach(function (s) {
                var row = Math.floor(s / myApplication.auditorium.cols);
                var col = s - row * myApplication.auditorium.cols + 1;
                seatsList.push(col + String.fromCharCode(65 + row))
            });
            $("#selectedSeats").text(seatsList.join(", "));
        });

        $(".btn#cancel").click(function () {
            myApplication.cancelReservation();
            myApplication.init();
        });
        $(".btn#confirmReservation").click(function() {
            myApplication.confirmReservation(function() {
                $("#reservationWindow").modal('hide');
                $("#confirmationWindow").modal('show');
            });
        });
        $("#confirmationWindow").on('hidden.bs.modal', function(evt) {
           myApplication.init();
        });
    },

    init: function () {
        myApplication.resetGUI();

        myApplication.currentReservationId = null;
        myApplication.blockedSeatsList = new Set();
        myApplication.selectedSeatsList = new Set();
        myApplication.auditorium = {
            id: null,
            rows: null,
            name: null,
            cols: null,
            total_num_seats: null
        };
        myApplication.screening = {
            id: null,
            title: null,
            datetime: null
        };

        Pusher.logToConsole = true;
        myApplication.pusher = new Pusher('c6c88f0bd9523ee60c3e', {
            cluster: 'eu',
            encrypted: true
        });

        // Subscribe for the updates.
        var channel = myApplication.pusher.subscribe('appcinema-reservation');

        channel.bind('blocked-seats', function (data) {
            if (myApplication.screening.id === data.screening_id) {
                myApplication.blockSeats(data.blocked_seats);
            }
        });


        // CoreAPI REST requests.
        var auth = new coreapi.auth.SessionAuthentication({
            csrfCookieName: 'csrftoken',
            csrfHeaderName: 'X-CSRFToken'
        });
        myApplication.client = new coreapi.Client({auth: auth})
    }
};

$(document).ready(function () {
    myApplication.init();
    myApplication.initGUI();
});