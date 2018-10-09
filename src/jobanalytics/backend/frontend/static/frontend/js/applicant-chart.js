var work_ethic_endpoint = '/api/chart/data/work_ethic/';
var work_ethic_data = [];
var work_ethic_labels = [];

var ratio_endpoint = '/api/chart/data/match_ratio/'
var ratio_data = []
var ratio_labels = [];

var skills_endpoint = '/api/chart/data/freq_skills/'
var skills_data = []
var skills_labels = [];

var ctx = null;
var skills = null;

var ctx2 = null;
var ratio = null;

var ctx3 = null;
var workEthic = null;

function configChart(labels, data, chartType, labelTitle){
    var config = {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: labelTitle,
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255,99,132,1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }],
                xAxes: []
            }
        }
    }
    return config
}


$.ajax({
    method: "GET",
    url: work_ethic_endpoint,
    success: function(data){
        work_ethic_labels = data.labels
        work_ethic_data = data.default
        ctx3 = document.getElementById("workEthicChart").getContext('2d');
        workEthic = new Chart(ctx3, configChart(work_ethic_labels, work_ethic_data, 'doughnut', 'Top Work Ethic amongst applicants'));
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
})
$.ajax({
    method: "GET",
    url: ratio_endpoint,
    success: function(data){
        ratio_labels = data.labels
        ratio_data = data.default
        ctx2 = document.getElementById("ratioChart").getContext('2d');
        ratio = new Chart(ctx2, configChart(ratio_labels, ratio_data, 'pie', 'Ratio of applicants job match score'));
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
})
$.ajax({
    method: "GET",
    url: skills_endpoint,
    success: function(data){
        skills_labels = data.labels
        skills_data = data.default
        ctx = document.getElementById("skillsChart").getContext('2d');
        skills = new Chart(ctx, configChart(skills_labels, skills_data, 'polarArea', 'Top Skills amongst Applicants'));
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
})



