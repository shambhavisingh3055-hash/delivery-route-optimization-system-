// ==========================================================
// AI ROUTE - MAIN JAVASCRIPT
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {


    // ======================================================
    // GREETING
    // ======================================================

    const headerTitle = document.querySelector(".header h1");

    if (
        headerTitle &&
        window.location.pathname === "/"
    ) {

        const hour = new Date().getHours();

        let greeting = "Welcome";

        if (hour < 12) {

            greeting = "Good Morning 👋";

        }
        else if (hour < 17) {

            greeting = "Good Afternoon ☀";

        }
        else {

            greeting = "Good Evening 🌙";

        }

        headerTitle.innerHTML =
            greeting +
            "<br>AI/ML Delivery Route Optimization System";

    }


    // ======================================================
    // CARD HOVER EFFECT
    // ======================================================

    const cards = document.querySelectorAll(".card");

    cards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {

            card.style.transform =
                "translateY(-10px) scale(1.03)";

        });


        card.addEventListener("mouseleave", function () {

            card.style.transform =
                "translateY(0px) scale(1)";

        });

    });


    // ======================================================
    // UPLOAD DATASET
    // ======================================================

    const csvFile =
        document.getElementById("csvFile");


    if (csvFile) {

        csvFile.addEventListener(
            "change",
            function () {

                const file = this.files[0];

                if (file) {

                    const fileName =
                        document.getElementById("fileName");


                    if (fileName) {

                        fileName.innerHTML =
                            "Selected File : " +
                            file.name +
                            " ✅";

                    }

                }

            }
        );

    }


   
    // ======================================================
    // AI PREDICTION
    // ======================================================

    const predictBtn =
        document.getElementById("predictBtn");


    if (predictBtn) {

        predictBtn.addEventListener(
            "click",
            async function () {


                // ==============================
                // GET INPUT ELEMENTS
                // ==============================

                const distanceInput =
                    document.getElementById(
                        "distanceInput"
                    );


                const trafficInput =
                    document.getElementById(
                        "trafficInput"
                    );


                const weatherInput =
                    document.getElementById(
                        "weatherInput"
                    );


                const predictionTime =
                    document.getElementById(
                        "predictionTime"
                    );


                const traffic =
                    document.getElementById(
                        "traffic"
                    );


                const weather =
                    document.getElementById(
                        "weather"
                    );


                const errorBox =
                    document.getElementById(
                        "predictionError"
                    );


                // ==============================
                // GET VALUES
                // ==============================

                const distance =
                    distanceInput
                        ? distanceInput.value.trim()
                        : "";


                const trafficValue =
                    trafficInput
                        ? trafficInput.value
                        : "";


                const weatherValue =
                    weatherInput
                        ? weatherInput.value
                        : "";


                // ==============================
                // VALIDATION
                // ==============================

                if (
                    distance === "" ||
                    trafficValue === "" ||
                    weatherValue === ""
                ) {

                    if (errorBox) {

                        errorBox.innerHTML =
                            '<i class="fa-solid fa-circle-exclamation"></i> Please enter distance and select traffic and weather conditions.';

                        errorBox.style.display =
                            "block";

                    }

                    return;

                }


                // Hide previous error

                if (errorBox) {

                    errorBox.style.display =
                        "none";

                }


                // ==============================
                // BUTTON LOADING
                // ==============================

                predictBtn.disabled = true;

                predictBtn.innerHTML =
                    '<i class="fa-solid fa-spinner fa-spin"></i> Predicting...';


                try {


                    // ==========================
                    // SEND DATA TO FLASK
                    // ==========================

                    const response =
                        await fetch(
                            "/api/predict",
                            {

                                method: "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json"

                                },

                                body: JSON.stringify({

                                    distance_km:
                                        Number(distance),

                                    traffic:
                                        trafficValue,

                                    weather:
                                        weatherValue

                                })

                            }
                        );


                    // ==========================
                    // GET RESPONSE
                    // ==========================

                    const data =
                        await response.json();


                    // ==========================
                    // CHECK ERROR
                    // ==========================

                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Prediction failed."
                        );

                    }


                    // ==========================
                    // DISPLAY PREDICTION
                    // ==========================

                    if (predictionTime) {

                        predictionTime.innerHTML =
                            Number(
                                data.predicted_time_min
                            ).toFixed(2) +
                            " min";

                    }


                    // ==========================
                    // DISPLAY TRAFFIC
                    // ==========================

                    if (traffic) {

                        traffic.innerHTML =
                            data.traffic;

                    }


                    // ==========================
                    // DISPLAY WEATHER
                    // ==========================

                    if (weather) {

                        weather.innerHTML =
                            data.weather;

                    }


                    // ==========================
                    // SUCCESS BUTTON
                    // ==========================

                    // ==========================
// SUCCESS BUTTON
// ==========================

predictBtn.innerHTML =
    '<i class="fa-solid fa-check"></i> Prediction Complete';

predictBtn.style.background =
    "#16a34a";

// Enable button again
predictBtn.disabled = false;

// Reset button after 1 second
setTimeout(function () {

    predictBtn.innerHTML =
        '<i class="fa-solid fa-brain"></i> Run Prediction';

    predictBtn.style.background = "";

}, 1000);

                }
                catch (error) {

                    console.error(
                        "Prediction Error:",
                        error
                    );


                    if (errorBox) {

                        errorBox.innerHTML =
                            '<i class="fa-solid fa-circle-exclamation"></i> ' +
                            error.message;

                        errorBox.style.display =
                            "block";

                    }


                    predictBtn.innerHTML =
                        '<i class="fa-solid fa-brain"></i> Run Prediction';


                    predictBtn.disabled = false;

                }

            }
        );

    }


  // ======================================================
// REPORT CHART
// ======================================================

const reportChart =
    document.getElementById("deliveryChart");

const totalDeliveries =
    document.getElementById("totalDeliveries");

const totalDistance =
    document.getElementById("totalDistance");

const totalDeliveryTime =
    document.getElementById("totalDeliveryTime");

const averageDeliveryTime =
    document.getElementById("averageDeliveryTime");


if (reportChart) {

    fetch("/api/report")

        .then(function(response) {

            return response.json();

        })

        .then(function(data) {

            if (!data.success) {

                console.error(
                    "Report Error:",
                    data.message
                );

                return;

            }


            // ==========================================
            // UPDATE REPORT CARDS
            // ==========================================

            if (totalDeliveries) {

                totalDeliveries.innerHTML =
                    data.total_deliveries;

            }


            if (totalDistance) {

                totalDistance.innerHTML =
                    Number(
                        data.total_distance_km
                    ).toFixed(2) + " km";

            }


            if (totalDeliveryTime) {

                const totalHours =
                    Number(
                        data.total_delivery_time_min
                    ) / 60;

                totalDeliveryTime.innerHTML =
                    totalHours.toFixed(2) + " hrs";

            }


            if (averageDeliveryTime) {

                averageDeliveryTime.innerHTML =
                    Number(
                        data.average_delivery_time_min
                    ).toFixed(2) + " min";

            }


            // ==========================================
            // TRAFFIC DATA
            // ==========================================

            const trafficData =
                data.traffic_analysis || {};

            const trafficLabels =
                Object.keys(trafficData);

            const trafficValues =
                Object.values(trafficData);


            // ==========================================
            // CREATE CHART
            // ==========================================

            new Chart(
                reportChart,
                {

                    type: "bar",

                    data: {

                        labels: trafficLabels,

                        datasets: [{

                            label:
                                "Average Delivery Time (min)",

                            data:
                                trafficValues

                        }]

                    },

                    options: {

    responsive: true,

    maintainAspectRatio: true,

    aspectRatio: 2,

                        plugins: {

                            legend: {

                                display: true

                            }

                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                title: {

                                    display: true,

                                    text:
                                        "Delivery Time (minutes)"

                                }

                            },

                            x: {

                                title: {

                                    display: true,

                                    text:
                                        "Traffic Condition"

                                }

                            }

                        }

                    }

                }
            );

        })

                     .catch(function(error) {

            console.error(
                "Report Loading Error:",
                error
            );

        });

    }


// ======================================================
// DASHBOARD DATA
// ======================================================

const dashboardDeliveries =
    document.getElementById("dashboardDeliveries");

const dashboardDistance =
    document.getElementById("dashboardDistance");

const dashboardTime =
    document.getElementById("dashboardTime");

const dashboardFuel =
    document.getElementById("dashboardFuel");


if (dashboardDeliveries) {

    // Get dashboard data
    fetch("/api/report")
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {

            if (!data.success) {

                console.error(
                    "Dashboard Report Error:",
                    data.message
                );

                return;
            }


            // ======================================
            // TOTAL DELIVERIES
            // ======================================

            dashboardDeliveries.innerHTML =
                data.total_deliveries;


            // ======================================
            // ESTIMATED TIME
            // ======================================

            dashboardTime.innerHTML =
                Number(
                    data.total_delivery_time_min || 0
                ).toFixed(2) + " min";


            // ======================================
            // OPTIMIZED DISTANCE
            // ======================================

            const optimizedDistance =
                Number(
                    data.optimized_distance_km || 0
                );

            dashboardDistance.innerHTML =
                optimizedDistance.toFixed(2) + " km";


            // ======================================
            // ESTIMATED FUEL USAGE
            // Assumption: 10 km per litre
            // ======================================

            const fuelUsage =
                optimizedDistance / 10;

            dashboardFuel.innerHTML =
                fuelUsage.toFixed(2) + " L";

        })
        .catch(function(error) {

            console.error(
                "Dashboard Data Error:",
                error
            );

        });

}


   
           

// ======================================================
// DASHBOARD OPTIMIZE BUTTON
// ======================================================

const dashboardOptimizeBtn =
    document.getElementById("dashboardOptimizeBtn");

if (dashboardOptimizeBtn) {

    dashboardOptimizeBtn.addEventListener(
        "click",
        function () {

            window.location.href = "/optimize";

        }
    );

}


});
// ==========================================================
// DISPLAY OPTIMIZED ROUTE TABLE
// ==========================================================

function displayRouteTable(route) {


    const routeContainer =
        document.querySelector(
            ".table-container"
        );


    const emptyRoute =
        document.querySelector(
            ".empty-route"
        );


    if (!routeContainer) {

        return;

    }


    // ==============================================
    // CHECK ROUTE DATA
    // ==============================================

    if (
        !Array.isArray(route) ||
        route.length === 0
    ) {

        routeContainer.innerHTML = `

            <div class="empty-route">

                <i class="fa-solid fa-route"></i>

                <h3>
                    No Route Data Available
                </h3>

                <p>
                    The optimization API did not
                    return any delivery records.
                </p>

            </div>

        `;

        return;

    }


    // ==============================================
    // CREATE TABLE
    // ==============================================

    let tableHTML = `

        <table class="route-table">

            <thead>

                <tr>

                    <th>Route Order</th>

                    <th>Customer</th>

                    <th>Latitude</th>

                    <th>Longitude</th>

                    <th>Distance</th>

                    <th>Traffic</th>

                    <th>Weather</th>

                    <th>Delivery Time</th>

                </tr>

            </thead>

            <tbody>

    `;


    // ==============================================
    // ADD ROUTE ROWS
    // ==============================================

    route.forEach(
        function (delivery, index) {


            const order =
                delivery.route_order ??
                (index + 1);


            const customer =
                delivery.customer ??
                "Unknown";


            const latitude =
                delivery.latitude ??
                "-";


            const longitude =
                delivery.longitude ??
                "-";


            const distance =
                Number(
                    delivery.route_distance_km || 0
                );


            const traffic =
                delivery.traffic ??
                "-";


            const weather =
                delivery.weather ??
                "-";


            const deliveryTime =
                delivery.delivery_time_min ??
                "-";


            tableHTML += `

                <tr>

                    <td>
                        ${order}
                    </td>

                    <td>
                        ${customer}
                    </td>

                    <td>
                        ${Number(latitude).toFixed(4)}
                    </td>

                    <td>
                        ${Number(longitude).toFixed(4)}
                    </td>

                    <td>
                        ${distance.toFixed(2)} km
                    </td>

                    <td>
                        ${traffic}
                    </td>

                    <td>
                        ${weather}
                    </td>

                    <td>
                        ${deliveryTime} min
                    </td>

                </tr>

            `;

        }
    );


    tableHTML += `

            </tbody>

        </table>

    `;


    routeContainer.innerHTML =
        tableHTML;


    // Hide initial empty state

    if (emptyRoute) {

        emptyRoute.style.display =
            "none";

    }

}


// ==========================================================
// SHOW OPTIMIZATION ERROR
// ==========================================================

function showOptimizationError(message) {


    let errorBox =
        document.querySelector(
            ".error-message"
        );


    if (!errorBox) {


        errorBox =
            document.createElement(
                "div"
            );


        errorBox.className =
            "error-message";


        const main =
            document.querySelector(
                ".main"
            );


        if (main) {

            const content =
                main.querySelector(
                    ".content"
                );


            main.insertBefore(
                errorBox,
                content
            );

        }

    }


    errorBox.innerHTML = `

        <i class="fa-solid fa-circle-exclamation"></i>

        ${message}

    `;


    errorBox.style.display =
        "block";

}