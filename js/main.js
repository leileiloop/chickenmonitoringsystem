// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");

function activeLink() {
  list.forEach((item) => {
    item.classList.remove("hovered");
  });
  this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");

toggle.onclick = function () {
  navigation.classList.toggle("active");
  main.classList.toggle("active");
};

//<!-- ========================= Notif ==================== -->

function toggleNotifi() {
    var box = document.getElementById('box');
    box.style.height = box.style.height === '0px' ? 'auto' : '0px';
    box.style.opacity = box.style.opacity === '0' ? '1' : '0';
}




//<!-- ========================= Date Time ==================== -->
function updateDateTime() {
        // Get the current date and time
        var currentDateTime = new Date();

        // Format the date as YYYY-MM-DD
        var year = currentDateTime.getFullYear();
        var month = (currentDateTime.getMonth() + 1).toString().padStart(2, '0'); // Month is zero-based
        var day = currentDateTime.getDate().toString().padStart(2, '0');

        // Format the time as HH:MM:SS
        var hours = currentDateTime.getHours().toString().padStart(2, '0');
        var minutes = currentDateTime.getMinutes().toString().padStart(2, '0');
        var seconds = currentDateTime.getSeconds().toString().padStart(2, '0');

        // Display the formatted date and time in the span
        document.getElementById("displayDateTime").innerText = year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
    }

    // Update the time every second (1000 milliseconds)
    setInterval(updateDateTime, 1000);

    // Initial call to set the time immediately
    updateDateTime();

//<!-- ========================= Temperature Chart ==================== -->

// Get the canvas element for temperature chart
var ctxTemperature = document.getElementById('lineChart').getContext('2d');

// Initialize an empty data array for the temperature chart
var dataTemperature = {
    labels: [],
    datasets: [{
        label: 'Temperature',
        borderColor: 'rgb(75, 192, 192)',
        data: [],
        fill: false
    }]
};

// Initialize the temperature line chart
var lineChartTemperature = new Chart(ctxTemperature, {
    type: 'line',
    data: dataTemperature,
    options: {
        scales: {
            x: [{
                type: 'linear',
                position: 'bottom'
            }]
        }
    }
});

// Function to add new data point to the temperature chart
function addDataTemperature(label, value) {
    // Add label to the labels array
    dataTemperature.labels.push(label);

    // Add value to the data array
    dataTemperature.datasets[0].data.push(value);

    // Limit the number of data points to display (e.g., 10)
    var maxDataPoints = 10;
    while (dataTemperature.labels.length > maxDataPoints) {
        dataTemperature.labels.shift();
        dataTemperature.datasets[0].data.shift();
    }

    // Update the chart
    lineChartTemperature.update();
}

// Simulate real-time data update for temperature chart
setInterval(function () {
    var label = new Date().toLocaleTimeString();
    var value = Math.random() * 100; // Replace this with your actual temperature data
    addDataTemperature(label, value);
}, 1000); // Update every second


//<!-- ========================= Humidity Chart ==================== -->

// Get the canvas element for temperature chart
var ctxHumidity = document.getElementById('lineChart1').getContext('2d');

// Initialize an empty data array for the temperature chart
var dataHumidity = {
    labels: [],
    datasets: [{
        label: 'Humidity',
        borderColor: 'rgb(75, 192, 192)',
        data: [],
        fill: false
    }]
};

// Initialize the temperature line chart
var lineChartHumidity = new Chart(ctxHumidity, {
    type: 'line',
    data: dataHumidity,
    options: {
        scales: {
            x: [{
                type: 'linear',
                position: 'bottom'
            }]
        }
    }
});

// Function to add new data point to the temperature chart
function addDataHumidity(label, value) {
    // Add label to the labels array
    dataHumidity.labels.push(label);

    // Add value to the data array
    dataHumidity.datasets[0].data.push(value);

    // Limit the number of data points to display (e.g., 10)
    var maxDataPoints = 10;
    while (dataHumidity.labels.length > maxDataPoints) {
        dataHumidity.labels.shift();
        dataHumidity.datasets[0].data.shift();
    }

    // Update the chart
    lineChartHumidity.update();
}

// Simulate real-time data update for temperature chart
setInterval(function () {
    var label = new Date().toLocaleTimeString();
    var value = Math.random() * 100; // Replace this with your actual temperature data
    addDataHumidity(label, value);
}, 1000); // Update every second


//<!-- ========================= Growth Poultry Image ==================== -->

// Function to update egg counts
        function updateEggCounts() {
            // Fetch egg counts from the server
            fetch('/chick_counts')
                .then(response => response.json())
                .then(data => {
                    // Update the HTML content with the fetched counts
                    document.getElementById('hatchedCount').innerHTML = 'Hatched Egg Count: ' + data.hatched_egg_count;
                    document.getElementById('unhatchedCount').innerHTML = 'Unhatched Egg Count: ' + data.unhatched_egg_count;
                })
                .catch(error => {
                    console.error('Error fetching egg counts:', error);
                });
        }

        // Update egg counts every 1 second (adjust as needed)
        setInterval(updateEggCounts, 1000);

function CaptureImage() {
         fetch('{{ url_for("tasks") }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'click=Capture',  // Adjust the data as needed
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response if needed
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}



//<!-- ========================= Growth Table ==================== -->

// Function to update the table with data from the server
async function updateTable() {
    const response = await fetch('/table_data');
    const data = await response.json();
    const tableBody = document.getElementById('table-body');

    // Clear existing rows
    tableBody.innerHTML = '';

    // Add new rows based on the data received
    data.data.forEach(row => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `<td>${row.Days}</td><td>${row.Size}</td><td>${row.Weight}</td>`;
        tableBody.appendChild(newRow);
  });
}
// Update the table every 5 seconds (adjust as needed)
setInterval(updateTable, 5000);



window.onload = function() {
    updateLights();
};

//<!-- ========================= Env Changing Lights ==================== -->

function updateLights() {
    const lights = [
        { statusId: 'light1-status', imgId: 'light1', imgOn: '/static/imgs/LightB.jpg', imgOff: '/static/imgs/LightA.png' },
        { statusId: 'light2-status', imgId: 'light2', imgOn: '/static/imgs/LightB.jpg', imgOff: '/static/imgs/LightA.png' },
        { statusId: 'light3-status', imgId: 'light3', imgOn: '/static/imgs/LightB.jpg', imgOff: '/static/imgs/LightA.png' },
        { statusId: 'light4-status', imgId: 'light4', imgOn: '/static/imgs/LightB.jpg', imgOff: '/static/imgs/LightA.png' }
    ];

    lights.forEach(light => {
        const statusElement = document.getElementById(light.statusId);
        const imgElement = document.getElementById(light.imgId);

        if (statusElement.innerHTML === 'ON') {
            imgElement.src = light.imgOn;
        } else {
            imgElement.src = light.imgOff;
        }
    });
}


