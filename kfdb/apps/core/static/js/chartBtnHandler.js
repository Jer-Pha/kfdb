const chartBtn = document.getElementById('display-stats');

function toggleCharts() {
    let charts = document.getElementById('charts');
    charts.style.display = charts.style.display == "none" ? "block" : "none";
}

chartBtn.addEventListener('click', toggleCharts);
