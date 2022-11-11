const renderChart = (data, labels) => {
    const ctx = document.getElementById('incomeExpenseChart').getContext('2d');
    ctx.width = 1000;
    ctx.height = 1000;
    const incomeExpenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total income-expense',
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
                text: "Total income-expense",
            }
        }
    });
}

const getChartData = () => {
    fetch('http://127.0.0.1:8000/overview/income_expense_summary')
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const income_expense_data = results.expense_income_data;
            const [labels, data] = [Object.keys(income_expense_data), Object.values(income_expense_data),];
            renderChart(data, labels);
        });
};

document.onload = getChartData();