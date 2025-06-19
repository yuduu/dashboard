// ======== COMBINED & OPTIMIZED update.js ========
// (Combines date.js, modal.js, sidebar.js, table.js, chart.js, dashboard.js)
// ================================================

// --- date.js (Optimized) ---
document.getElementById("currentYear").textContent = new Date().getFullYear();

// --- modal.js (Optimized) ---
const Modal = {
  init() {
    this.modal = document.getElementById("modal");
    this.modal.addEventListener("click", e => e.target === this.modal && this.close());
    document.querySelectorAll("[data-modal]").forEach(btn => {
      btn.addEventListener("click", () => this.open(btn.dataset.modal));
    });
  },
  open(id) {
    document.getElementById(id).classList.add("active");
    this.modal.classList.add("active");
  },
  close() {
    document.querySelector(".modal-content.active")?.classList.remove("active");
    this.modal.classList.remove("active");
  }
};

// --- sidebar.js (Optimized) ---
const Sidebar = {
  toggle() {
    document.getElementById("sidebar").classList.toggle("collapsed");
    localStorage.setItem("sidebarCollapsed", this.isCollapsed());
  },
  isCollapsed() {
    return document.getElementById("sidebar").classList.contains("collapsed");
  },
  init() {
    document.getElementById("sidebarToggle").addEventListener("click", this.toggle);
    if (localStorage.getItem("sidebarCollapsed") === "true") this.toggle();
  }
};

// --- table.js (Optimized) ---
const DataTable = {
  init(tableId) {
    this.table = document.getElementById(tableId);
    if (!this.table) return;
    
    this.sortBtns = this.table.querySelectorAll("th[data-sort]");
    this.sortBtns.forEach(th => {
      th.addEventListener("click", () => this.sortTable(th));
    });
  },
  sortTable(th) {
    const colIndex = th.cellIndex;
    const sortType = th.dataset.sort;
    const tbody = this.table.querySelector("tbody");
    const rows = [...tbody.rows];

    rows.sort((a, b) => {
      let x = a.cells[colIndex].textContent.trim();
      let y = b.cells[colIndex].textContent.trim();
      
      if (sortType === "number") {
        return parseFloat(x) - parseFloat(y);
      } else if (sortType === "date") {
        return new Date(x) - new Date(y);
      }
      return x.localeCompare(y);
    });

    if (th.classList.contains("sorted-asc")) {
      rows.reverse();
      th.classList.replace("sorted-asc", "sorted-desc");
    } else {
      th.classList.remove("sorted-desc");
      th.classList.add("sorted-asc");
    }

    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    rows.forEach(row => tbody.appendChild(row));
  }
};

// --- chart.js (Optimized) ---
const ChartRenderer = {
  init(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: data.title,
          data: data.values,
          borderColor: '#4e73df',
          backgroundColor: 'rgba(78, 115, 223, 0.05)',
          tension: 0.3
        }]
      },
      options: {
        scales: { y: { beginAtZero: true } },
        plugins: { legend: { display: false } }
      }
    });
  }
};

// --- dashboard.js (Optimized) ---
const Dashboard = {
  loadData() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/dashboard", true);
    xhr.onload = () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        this.updateUI(data);
      }
    };
    xhr.send();
  },
  updateUI(data) {
    document.getElementById("totalBooks").textContent = data.totalBooks;
    document.getElementById("activeUsers").textContent = data.activeUsers;
    ChartRenderer.init("readingChart", data.readingChart);
    DataTable.init("booksTable");
  },
  init() {
    Modal.init();
    Sidebar.init();
    this.loadData();
    setInterval(this.loadData, 300000); // Refresh every 5 minutes
  }
};

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => Dashboard.init());