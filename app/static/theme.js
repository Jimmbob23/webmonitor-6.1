(() => {
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme() {
    const dark = media.matches;
    const theme = dark ? "dark" : "light";

    document.documentElement.setAttribute("data-bs-theme", theme);
    document.documentElement.classList.toggle("wm-dark", dark);

    document.querySelectorAll("table.table, table.table-darkish").forEach((table) => {
      table.classList.toggle("table-dark", dark);
      table.classList.toggle("table-light", !dark);

      table.style.backgroundColor = dark ? "#111827" : "#ffffff";
      table.style.color = dark ? "#ffffff" : "#111827";

      table.querySelectorAll("thead, tbody, tfoot, tr, th, td").forEach((element) => {
        element.style.setProperty(
          "background-color",
          dark ? "#111827" : "#ffffff",
          "important"
        );
        element.style.setProperty(
          "color",
          dark ? "#ffffff" : "#111827",
          "important"
        );
        element.style.setProperty(
          "border-color",
          dark ? "#374151" : "#d1d5db",
          "important"
        );
        element.style.setProperty("box-shadow", "none", "important");
      });
    });
  }

  function start() {
    applyTheme();

    const observer = new MutationObserver(() => applyTheme());
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  if (typeof media.addEventListener === "function") {
    media.addEventListener("change", applyTheme);
  } else if (typeof media.addListener === "function") {
    media.addListener(applyTheme);
  }
})();
