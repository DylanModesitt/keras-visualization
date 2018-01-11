window.onload = function () {

    var trainingLoss = data.map(function(x) {return x.loss});
    var testingLoss = data.map(function(x) {return x.val_loss});
    var trainingAcc = data.map(function(x) {return x.acc});
    var testingAcc = data.map(function(x) {return x.val_acc});

    var acc = document.getElementById("acc").getContext("2d");
    var loss = document.getElementById("loss").getContext("2d");

    var labels = [];
    for (var i = 0; i <= trainingLoss.length; i++) {
        labels.push(i);
    }

    function makeConfig(data1, data2, name) {
        return {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Training",
                            backgroundColor: "#B0BEC5",
                            borderColor: "#B0BEC5",
                            data: data1,
                            fill: false
                        },
                        {
                            label: "Test",
                            backgroundColor: "#607D8B",
                            borderColor: "#607D8B",
                            data: data2,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: name
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'epoch'
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: name + ' value'
                            }
                        }]
                    }
                }
            }
    }

    new Chart(loss, makeConfig(trainingLoss, testingLoss, "Loss"));
    new Chart(acc, makeConfig(trainingAcc, testingAcc, "Accuracy"));

}