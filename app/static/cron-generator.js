function intValue(el, min, max, fallback) {
  const n = parseInt(el.value, 10);
  if (Number.isNaN(n)) return fallback;
  return Math.max(min, Math.min(max, n));
}

function cleanCsvNumbers(value, min, max) {
  return [...new Set(
    value.split(",")
      .map(v => parseInt(v.trim(), 10))
      .filter(v => Number.isInteger(v) && v >= min && v <= max)
  )].sort((a,b) => a-b);
}

function selectedWeekdays(helper) {
  return [...helper.querySelectorAll(".cron-weekday:checked")]
    .map(el => parseInt(el.value, 10))
    .filter(v => Number.isInteger(v));
}

function buildCron(helper) {
  const preset = helper.querySelector(".cron-preset").value;
  const everyMinutes = intValue(helper.querySelector(".cron-minutes"), 1, 59, 10);
  const start = intValue(helper.querySelector(".cron-hour-start"), 0, 23, 8);
  const end = intValue(helper.querySelector(".cron-hour-end"), 0, 23, 18);
  const minute = intValue(helper.querySelector(".cron-minute-fixed"), 0, 59, 0);
  const weekdays = selectedWeekdays(helper);
  const hours = cleanCsvNumbers(helper.querySelector(".cron-hours-list").value, 0, 23);
  const monthDays = cleanCsvNumbers(helper.querySelector(".cron-month-days").value, 1, 31);

  if (preset === "every_minutes") return `*/${everyMinutes} * * * *`;
  if (preset === "hourly_range") return `${minute} ${start}-${end} * * *`;
  if (preset === "daily_time") return `${minute} ${start} * * *`;
  if (preset === "weekly_time") {
    const day = weekdays.length ? weekdays[0] : 1;
    return `${minute} ${start} * * ${day}`;
  }
  if (preset === "selected_weekdays") {
    if (!weekdays.length) return "";
    return `${minute} ${start} * * ${weekdays.join(",")}`;
  }
  if (preset === "selected_weekdays_hours") {
    if (!weekdays.length || !hours.length) return "";
    return `${minute} ${hours.join(",")} * * ${weekdays.join(",")}`;
  }
  if (preset === "monthly_days") {
    if (!monthDays.length) return "";
    return `${minute} ${start} ${monthDays.join(",")} * *`;
  }
  if (preset === "custom") {
    return helper.closest("form").querySelector(".cron-expression").value.trim();
  }
  return "";
}

function updatePreview(helper) {
  const value = buildCron(helper);
  const preview = helper.querySelector(".cron-preview-value");
  preview.textContent = value || "Bitte passende Werte auswählen";
  return value;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".cron-helper").forEach(helper => {
    const form = helper.closest("form");
    const cronInput = form.querySelector(".cron-expression");
    const scheduleType = form.querySelector(".schedule-type");

    helper.querySelector(".cron-preview").addEventListener("click", () => updatePreview(helper));

    helper.querySelector(".cron-apply").addEventListener("click", () => {
      const value = updatePreview(helper);
      if (!value) {
        alert("Bitte die erforderlichen Wochentage, Uhrzeiten oder Monatstage auswählen.");
        return;
      }
      cronInput.value = value;
      scheduleType.value = "cron";
      cronInput.focus();
    });

    helper.querySelectorAll("input, select").forEach(el => {
      el.addEventListener("change", () => updatePreview(helper));
    });
  });
});
