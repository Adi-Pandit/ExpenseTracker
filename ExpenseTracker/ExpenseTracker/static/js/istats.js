const renderChart = (data, labels) => {
    const ctx = document.getElementById('imyChart').getContext('2d');
    const imyChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months incomes',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132)',
                    'rgba(54, 162, 235)',
                    'rgba(255, 206, 86)',
                    'rgba(75, 192, 192)',
                    'rgba(153, 102, 255)',
                    'rgba(255, 159, 64)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
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
            title: {
                display: true,
                text: "Source wise income",
            }
        }
    });
}

const getChartData = () => {
    fetch('http://127.0.0.1:8000/income/income_source_summary')
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const source_data = results.income_source_data;
            const [labels, data] = [Object.keys(source_data), Object.values(source_data),];
            renderChart(data, labels);
        });
};

document.onload = getChartData();