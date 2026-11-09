
(function () {
  "use strict";

  const root = document.documentElement;
  const THEME_KEY = "zhiqi-theme";

  function applyTheme(theme) {
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }

  function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(stored || (prefersDark ? "dark" : "light"));
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.addEventListener("click", function () {
        const next = root.classList.contains("dark") ? "light" : "dark";
        localStorage.setItem(THEME_KEY, next);
        applyTheme(next);
      });
    });
  }

  function initNav() {
    const toggle = document.querySelector("[data-nav-toggle]");
    const panel = document.querySelector("[data-nav-panel]");
    if (!toggle || !panel) return;
    toggle.addEventListener("click", function () {
      const open = panel.classList.toggle("hidden");
      toggle.setAttribute("aria-expanded", open ? "false" : "true");
    });
  }

  function initMessages() {
    document.querySelectorAll("[data-dismiss]").forEach(function (button) {
      button.addEventListener("click", function () {
        const alert = button.closest(".alert");
        if (alert) alert.remove();
      });
    });
  }

  function initConfirms() {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (!window.confirm(form.dataset.confirm)) {
          event.preventDefault();
        }
      });
    });
  }

  function initColumnToggles() {
    document.querySelectorAll("[data-col-toggle]").forEach(function (button) {
      button.addEventListener("click", function () {
        const table = document.querySelector(button.dataset.table);
        if (!table) return;
        const col = button.dataset.colToggle;
        table.querySelectorAll("[data-col='" + col + "']").forEach(function (cell) {
          cell.classList.toggle("hidden");
        });
        button.classList.toggle("opacity-50");
      });
    });
  }

  function initLineItems() {
    const formset = document.querySelector("[data-formset]");
    if (!formset) return;
    const total = formset.querySelector("input[name$='-TOTAL_FORMS']");
    const prefix = total ? total.name.replace("-TOTAL_FORMS", "") : "items";
    const addButton = formset.querySelector("[data-add-row]");
    const template = document.getElementById(prefix + "-empty");
    const tbody = formset.querySelector("[data-formset-rows]");
    if (!addButton || !template || !tbody || !total) return;
    addButton.addEventListener("click", function () {
      const index = parseInt(total.value, 10);
      const html = template.innerHTML.replace(/__prefix__/g, String(index));
      const wrapper = document.createElement("tbody");
      wrapper.innerHTML = html.trim();
      const row = wrapper.querySelector("tr");
      if (row) {
        tbody.appendChild(row);
        total.value = String(index + 1);
      }
    });
    formset.addEventListener("click", function (event) {
      const remove = event.target.closest("[data-remove-row]");
      if (!remove) return;
      const row = remove.closest("tr");
      if (!row) return;
      const checkbox = row.querySelector("input[name$='-DELETE']");
      if (checkbox) {
        checkbox.checked = true;
        row.classList.add("hidden");
      } else {
        row.remove();
      }
    });
  }

  function initCharts() {
    const node = document.getElementById("dashboard-charts");
    if (!node || typeof window.Chart === "undefined") return;
    let payload;
    try {
      payload = JSON.parse(node.dataset.charts || "{}");
    } catch (error) {
      return;
    }
    const palette = ["#3563f5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6", "#f97316"];
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true } },
    };
    const charts = [
      ["chart-trend", "line", payload.trend || payload.monthly, "近 12 個月核銷金額", false],
      ["chart-department", "doughnut", payload.department_share, "部門占比", true],
      ["chart-category", "doughnut", payload.category_share, "費用科目占比", true],
      ["chart-project", "bar", payload.project_chart, "計畫預算 vs 已核銷", false],
    ];
    charts.forEach(function (entry) {
      const canvas = document.getElementById(entry[0]);
      if (!canvas) return;
      const data = entry[2] || {};
      let datasets;
      if (entry[0] === "chart-project") {
        datasets = [
          { label: "預算", data: data.budget || [], backgroundColor: "#93c5fd" },
          { label: "已核銷", data: data.spent || [], backgroundColor: "#3563f5" },
        ];
      } else if (entry[4]) {
        datasets = [{ data: data.values || [], backgroundColor: palette }];
      } else {
        datasets = [
          {
            label: entry[3],
            data: data.values || [],
            borderColor: "#3563f5",
            backgroundColor: "rgba(53, 99, 245, 0.15)",
            fill: true,
            tension: 0.35,
          },
        ];
      }
      new window.Chart(canvas, {
        type: entry[1],
        data: { labels: data.labels || [], datasets: datasets },
        options: Object.assign({}, baseOptions, entry[4] ? { scales: {} } : {}),
      });
    });
  }

  function initTvRefresh() {
    const node = document.querySelector("[data-tv-refresh]");
    if (!node) return;
    const seconds = parseInt(node.dataset.tvRefresh, 10) || 60;
    window.setTimeout(function () {
      window.location.reload();
    }, seconds * 1000);
  }

  function initPwa() {
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", function () {
        navigator.serviceWorker.register("/sw.js").catch(function () {
        });
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initNav();
    initMessages();
    initConfirms();
    initColumnToggles();
    initLineItems();
    initCharts();
    initTvRefresh();
    initPwa();
  });
})();
