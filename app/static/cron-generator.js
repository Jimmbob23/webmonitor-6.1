function clampNumber(value, min, max, fallback) {
  const n = parseInt(value, 10);
  if (Number.isNaN(n)) return fallback;
  return Math.min(Math.max(n, min), max);
}

function buildCron(helper) {
  const preset = helper.querySelector(".cron-preset").value;
  const minutes = clampNumber(helper.querySelector(".cron-minutes").value, 1, 59, 10);
  const start = clampNumber(helper.querySelector(".cron-hour-start").value, 0, 23, 8);
  const end = clampNumber(helper.querySelector(".cron-hour-end").value, 0, 23, 18);

  if (preset === "every_minutes") return `*/${minutes} * * * *`;
  if (preset === "hourly_range") return `0 ${start}-${end} * * *`;
  if (preset === "daily_time") return `0 ${start} * * *`;
  if (preset === "weekdays_time") return `0 ${start} * * 1-5`;
  if (preset === "weekdays_range") return `0 ${start}-${end} * * 1-5`;
  return "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".cron-helper").forEach((helper) => {
    const form = helper.closest("form");
    const cronInput = form.querySelector(".cron-expression");
    const scheduleType = form.querySelector(".schedule-type");
    helper.querySelector(".cron-apply").addEventListener("click", () => {
      const cron = buildCron(helper);
      if (!cron) return;
      cronInput.value = cron;
      if (scheduleType) scheduleType.value = "cron";
      cronInput.focus();
    });
  });
});
