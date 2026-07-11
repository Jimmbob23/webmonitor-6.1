(() => {
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme() {
    const theme = media.matches ? "dark" : "light";
    document.documentElement.setAttribute("data-bs-theme", theme);
    document.documentElement.classList.toggle("wm-dark", theme === "dark");
  }

  applyTheme();

  if (typeof media.addEventListener === "function") {
    media.addEventListener("change", applyTheme);
  } else if (typeof media.addListener === "function") {
    media.addListener(applyTheme);
  }
})();
