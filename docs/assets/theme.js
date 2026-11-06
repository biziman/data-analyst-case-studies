/* Light/dark theme switcher for the static site.
   A head snippet in the built pages sets <html data-theme> before first paint
   (saved choice, else system preference). This file wires the top-bar toggle,
   persists the choice in localStorage, and dispatches a window "themechange"
   event so widgets.js can restyle the Plotly charts. */
(function () {
  "use strict";

  const STORE_KEY = "theme";
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  const current = () => (document.documentElement.dataset.theme === "dark" ? "dark" : "light");

  function stored() {
    try { return localStorage.getItem(STORE_KEY); } catch (e) { return null; }
  }

  function persist(theme) {
    try { localStorage.setItem(STORE_KEY, theme); } catch (e) { /* private mode: session only */ }
  }

  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      const dark = theme === "dark";
      const label = dark ? "Switch to light theme" : "Switch to dark theme";
      btn.setAttribute("aria-label", label);
      btn.setAttribute("title", label);
      btn.setAttribute("aria-pressed", String(dark));
    }
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: theme } }));
  }

  document.addEventListener("DOMContentLoaded", function () {
    // The head snippet sets data-theme before paint; fall back to the system
    // preference if it is missing (e.g. the snippet failed to run).
    const preset = document.documentElement.dataset.theme;
    apply(preset === "dark" || preset === "light" ? preset : media.matches ? "dark" : "light");
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        const next = current() === "dark" ? "light" : "dark";
        persist(next);
        apply(next);
      });
    }
  });

  // Follow the system preference only while the visitor has made no choice.
  const onSystemChange = (e) => {
    if (stored()) return;
    apply(e.matches ? "dark" : "light");
  };
  if (media.addEventListener) media.addEventListener("change", onSystemChange);
  else if (media.addListener) media.addListener(onSystemChange);
})();
