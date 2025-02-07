// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", function () {
    
    // Flatpickr Initialization
    flatpickr(".flatpickr", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        time_24hr: true,
        allowInput: true
    });

    // Handle Adjust Time Checkboxes
    var adjustTimeIn = document.getElementById("adjust_time_in");
    var adjustTimeOut = document.getElementById("adjust_time_out");

    if (adjustTimeIn) {
        adjustTimeIn.addEventListener("change", function () {
            document.getElementById("time_input_in").style.display = this.checked ? "block" : "none";
        });
    }

    if (adjustTimeOut) {
        adjustTimeOut.addEventListener("change", function () {
            document.getElementById("time_input_out").style.display = this.checked ? "block" : "none";
        });
    }
});
