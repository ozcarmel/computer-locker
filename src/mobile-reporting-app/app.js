const sampleReport = {
  "2026-05-23": {
    unlockedUsageSeconds: 7200,
    regularLockAppearances: 5,
    dailyLimitLockAppearances: 1,
    parentExtraSecondsGranted: 1200,
    testLockAppearances: 1,
    parentActionDeniedCount: 0,
    parentExitAllowedCount: 1
  },
  "2026-05-24": {
    unlockedUsageSeconds: 2400,
    regularLockAppearances: 2,
    dailyLimitLockAppearances: 0,
    parentExtraSecondsGranted: 0,
    testLockAppearances: 0,
    parentActionDeniedCount: 1,
    parentExitAllowedCount: 0
  }
};

const reportList = document.querySelector("#reportList");
const emptyState = document.querySelector("#emptyState");
const template = document.querySelector("#dayTemplate");
const totalUsage = document.querySelector("#totalUsage");
const totalLocks = document.querySelector("#totalLocks");
const reportDays = document.querySelector("#reportDays");
const dataSource = document.querySelector("#dataSource");
const fileInput = document.querySelector("#reportFile");
const refreshButton = document.querySelector("#refreshButton");
const activitySource = document.querySelector("#activitySource");
const activityEmptyState = document.querySelector("#activityEmptyState");
const activityReport = document.querySelector("#activityReport");
const appsUsedList = document.querySelector("#appsUsedList");
const browserHistoryList = document.querySelector("#browserHistoryList");
const browserTotalTime = document.querySelector("#browserTotalTime");
const appsTotalTime = document.querySelector("#appsTotalTime");

function formatDuration(seconds) {
  const totalMinutes = Math.max(0, Math.round(Number(seconds || 0) / 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours}h ${String(minutes).padStart(2, "0")}m`;
}

function formatDate(dateKey) {
  const date = new Date(`${dateKey}T12:00:00`);
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric"
  }).format(date);
}

function formatTime(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.slice(11, 16);
  }
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function locksForDay(day) {
  return Number(day.regularLockAppearances || 0) + Number(day.dailyLimitLockAppearances || 0);
}

function parentActionsForDay(day) {
  return Number(day.parentActionDeniedCount || 0) + Number(day.parentExitAllowedCount || 0);
}

function isBrowserApp(appName) {
  const normalized = String(appName || "").toLowerCase();
  return ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"].includes(normalized);
}

function normalizeReport(report) {
  if (!report || typeof report !== "object" || Array.isArray(report)) {
    return {};
  }
  return report;
}

function renderReport(report, sourceLabel) {
  const normalized = normalizeReport(report);
  const entries = Object.entries(normalized).sort(([left], [right]) => right.localeCompare(left));

  reportList.replaceChildren();
  emptyState.hidden = entries.length !== 0;
  dataSource.textContent = sourceLabel;

  let usageSeconds = 0;
  let lockCount = 0;

  for (const [dateKey, day] of entries) {
    usageSeconds += Number(day.unlockedUsageSeconds || 0);
    lockCount += locksForDay(day);

    const card = template.content.firstElementChild.cloneNode(true);
    card.querySelector("h3").textContent = formatDate(dateKey);
    card.querySelector(".day-subtitle").textContent = dateKey;
    card.querySelector(".usage-pill").textContent = formatDuration(day.unlockedUsageSeconds);
    card.querySelector('[data-field="totalLocks"]').textContent = locksForDay(day);
    card.querySelector('[data-field="parentActions"]').textContent = parentActionsForDay(day);
    reportList.appendChild(card);
  }

  totalUsage.textContent = formatDuration(usageSeconds);
  totalLocks.textContent = String(lockCount);
  reportDays.textContent = String(entries.length);
}

async function loadBundledReport() {
  try {
    const response = await fetch("report-data.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error("No bundled report");
    }
    renderReport(await response.json(), "Locker report");
  } catch (_error) {
    renderReport(sampleReport, "Sample locker data");
  }
}

function renderEmptyList(container, message) {
  const item = document.createElement("p");
  item.className = "muted-line";
  item.textContent = message;
  container.replaceChildren(item);
}

function renderActivityReport(report, sourceLabel) {
  const hasReport = report && typeof report === "object";
  activitySource.textContent = sourceLabel;
  activityEmptyState.hidden = hasReport;
  activityReport.hidden = !hasReport;

  if (!hasReport) {
    appsUsedList.replaceChildren();
    browserHistoryList.replaceChildren();
    browserTotalTime.textContent = "0h 00m";
    appsTotalTime.textContent = "0h 00m";
    return;
  }

  const apps = Array.isArray(report.appsUsed) ? report.appsUsed : [];
  const browserHistory = Array.isArray(report.browserHistory) ? report.browserHistory : [];
  const browserApps = apps.filter((app) => isBrowserApp(app.appName));
  const otherApps = apps.filter((app) => !isBrowserApp(app.appName));
  const browserSeconds = browserApps.reduce((sum, app) => sum + Number(app.seconds || 0), 0);
  const appSeconds = otherApps.reduce((sum, app) => sum + Number(app.seconds || 0), 0);

  browserTotalTime.textContent = formatDuration(browserSeconds);
  appsTotalTime.textContent = formatDuration(appSeconds);

  if (browserHistory.length === 0) {
    renderEmptyList(browserHistoryList, "No browser history found for this report period.");
  } else {
    browserHistoryList.replaceChildren(...browserHistory.slice(0, 12).map((entry) => {
      const row = document.createElement("div");
      row.className = "activity-row stacked";
      const title = document.createElement("strong");
      title.textContent = entry.title || entry.url || "Visited page";
      const meta = document.createElement("span");
      meta.textContent = `${formatTime(entry.visitedAt)} - ${entry.browser || "Browser"}`;
      const link = document.createElement("small");
      link.textContent = entry.url || "";
      row.append(title, meta, link);
      return row;
    }));
  }

  if (otherApps.length === 0) {
    renderEmptyList(appsUsedList, "No non-browser app usage recorded yet.");
  } else {
    appsUsedList.replaceChildren(...otherApps.slice(0, 8).map((app) => {
      const row = document.createElement("div");
      row.className = "activity-row";
      const title = document.createElement("strong");
      title.textContent = app.appName || "Unknown app";
      const meta = document.createElement("span");
      meta.textContent = formatDuration(app.seconds);
      row.append(title, meta);
      return row;
    }));
  }
}

async function loadActivityReport() {
  try {
    const response = await fetch("activity-report.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error("No activity report");
    }
    renderActivityReport(await response.json(), "Latest activity report");
  } catch (_error) {
    renderActivityReport(null, "No activity report");
  }
}

fileInput.addEventListener("change", async () => {
  const [file] = fileInput.files;
  if (!file) {
    return;
  }

  try {
    const report = JSON.parse(await file.text());
    renderReport(report, file.name);
  } catch (_error) {
    alert("The selected file is not valid report JSON.");
    fileInput.value = "";
  }
});

async function refreshReports() {
  refreshButton.disabled = true;
  activitySource.textContent = "Refreshing...";
  dataSource.textContent = "Refreshing...";
  try {
    const response = await fetch("/api/refresh", { method: "POST", cache: "no-store" });
    if (!response.ok) {
      throw new Error("Refresh endpoint unavailable");
    }
  } catch (_error) {
    // Static-file fallback: reload the latest generated JSON if the server endpoint is unavailable.
  } finally {
    await loadActivityReport();
    await loadBundledReport();
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", refreshReports);

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("service-worker.js").catch(() => {});
}

loadActivityReport();
loadBundledReport();
