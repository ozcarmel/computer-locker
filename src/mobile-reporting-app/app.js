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

function locksForDay(day) {
  return Number(day.regularLockAppearances || 0) + Number(day.dailyLimitLockAppearances || 0);
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
    card.querySelector('[data-field="regularLockAppearances"]').textContent = day.regularLockAppearances || 0;
    card.querySelector('[data-field="dailyLimitLockAppearances"]').textContent = day.dailyLimitLockAppearances || 0;
    card.querySelector('[data-field="parentExtraSecondsGranted"]').textContent = formatDuration(day.parentExtraSecondsGranted);
    card.querySelector('[data-field="testLockAppearances"]').textContent = day.testLockAppearances || 0;
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
    renderReport(await response.json(), "Exported report");
  } catch (_error) {
    renderReport(sampleReport, "Sample data");
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

refreshButton.addEventListener("click", loadBundledReport);

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("service-worker.js").catch(() => {});
}

loadBundledReport();
