const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
tableOutput.style.display = 'none';
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none";
        tbody.innerHTML = "";
        fetch("http://127.0.0.1:8000/search-expenses", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);
                appTable.style.display = "none";
                tableOutput.style.display = "block";
                console.log("data.length", data.length);
                if (data.length === 0) {
                    noResults.style.display = "block";
                    tableOutput.style.display = "none";

                }
                else {
                    noResults.style.display = "none";
                    data.forEach((item) => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${item.amount}</td>
                                <td>${item.category}</td>
                                <td>${item.description}</td>
                                <td>${item.date}</td>
                                <td><a href="{% url 'expense-edit' expense.id %}" class="btn btn-secondary btn-sm">Edit</a><a href="{% url 'expense-delete' expense.id %}"><img src="{% static 'img/delete.png' %}" width="35" height="35"/></a></td>
                            </tr>`;
                    });
                }
            });
    }
    else {
        noResults.style.display = "none";
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});

