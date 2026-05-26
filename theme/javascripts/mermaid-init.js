(function () {
  "use strict";

  var loaded = false;

  function mermaidScriptUrl() {
    var cfg = document.getElementById("__config");
    if (cfg) {
      try {
        var base = JSON.parse(cfg.textContent).base || ".";
        var prefix = base === "." ? "" : base.replace(/\/?$/, "/");
        return prefix + "javascripts/mermaid.min.js";
      } catch (e) {
        /* ignore */
      }
    }
    return "javascripts/mermaid.min.js";
  }

  function pageNeedsMermaid() {
    return !!document.querySelector(
      ".mermaid, .language-mermaid, pre code.language-mermaid"
    );
  }

  function loadMermaid() {
    if (loaded || !pageNeedsMermaid()) {
      return;
    }
    loaded = true;
    var s = document.createElement("script");
    s.src = mermaidScriptUrl();
    s.async = true;
    document.body.appendChild(s);
  }

  function onPage() {
    loaded = false;
    loadMermaid();
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(onPage);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onPage);
  } else {
    onPage();
  }
})();
