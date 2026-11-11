const storeSelect = document.getElementById("storeSelect");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

let overviewChart;
let itemChart;

async function loadStores() {
    const response = await fetch("/api/stores");
    const stores = await response.json();

    storeSelect.innerHTML = stores
        .map(store => `<option value="${store}">${store}</option>`)
        .join("");

    await loadDashboard();
    await loadItems();
}

async function loadDashboard() {
    const store = storeSelect.value;

    const response = await fetch(
        `/api/summary?store_id=${encodeURIComponent(store)}`
    );

    const summary = await response.json();

    document.getElementById("salesTotal").textContent =
        summary.sales_total.toLocaleString();

    document.getElementById("forecastTotal").textContent =
        summary.forecast_total.toLocaleString();

    document.getElementById("selectedStore").textContent = store;

    const sales = new Map(
        summary.sales_days.map(row => [row.date, row.value])
    );

    const forecasts = new Map(
        summary.forecast_days.map(row => [row.date, row.value])
    );

    const dates = [
        ...new Set([
            ...summary.sales_days.map(row => row.date),
            ...summary.forecast_days.map(row => row.date),
        ]),
    ];

    if (overviewChart) {
        overviewChart.destroy();
    }

    overviewChart = new Chart(
        document.getElementById("overviewChart"),
        {
            type: "line",
            data: {
                labels: dates,
                datasets: [
                    {
                        label: "Historical Sales",
                        data: dates.map(date => sales.get(date) || 0),
                        borderColor: "#2563eb",
                        backgroundColor: "#2563eb22",
                        tension: 0.3,
                    },
                    {
                        label: "Forecast",
                        data: dates.map(date => forecasts.get(date) || 0),
                        borderColor: "#dc2626",
                        backgroundColor: "#dc262622",
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
            },
        }
    );
}

async function loadItems() {
    const store = storeSelect.value;
    const search = searchInput.value;

    const response = await fetch(
        `/api/items?store_id=${encodeURIComponent(store)}&search=${encodeURIComponent(search)}`
    );

    const items = await response.json();

    if (items.length === 0) {
        document.getElementById("itemsTable").innerHTML =
            "<p>No items found.</p>";
        return;
    }

    document.getElementById("itemsTable").innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Department</th>
                    <th>Category</th>
                    <th>On Hand</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.item_id}</td>
                        <td>${item.dept_id}</td>
                        <td>${item.cat_id}</td>
                        <td>${item.on_hand}</td>
                        <td>
                            <button class="item-button"
                                onclick="loadItemSeries('${item.item_id}')">
                                View Forecast
                            </button>
                        </td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

async function loadItemSeries(itemId) {
    const store = storeSelect.value;

    const response = await fetch(
        `/api/series?item_id=${encodeURIComponent(itemId)}&store_id=${encodeURIComponent(store)}`
    );

    const result = await response.json();

    document.getElementById("selectedItem").textContent =
        `${itemId} - ${store}`;

    const salesMap = new Map(
        result.sales.map(row => [row.date, row.value])
    );

    const forecastMap = new Map(
        result.forecasts.map(row => [row.date, row.value])
    );

    const dates = [
        ...new Set([
            ...result.sales.map(row => row.date),
            ...result.forecasts.map(row => row.date),
        ]),
    ];

    if (itemChart) {
        itemChart.destroy();
    }

    itemChart = new Chart(
        document.getElementById("itemChart"),
        {
            type: "line",
            data: {
                labels: dates,
                datasets: [
                    {
                        label: "Sales",
                        data: dates.map(date => salesMap.get(date) ?? null),
                        borderColor: "#2563eb",
                        tension: 0.3,
                    },
                    {
                        label: "Forecast",
                        data: dates.map(date => forecastMap.get(date) ?? null),
                        borderColor: "#dc2626",
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                spanGaps: true,
            },
        }
    );
}

storeSelect.addEventListener("change", async () => {
    await loadDashboard();
    await loadItems();
});

searchButton.addEventListener("click", loadItems);

loadStores();