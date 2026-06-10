(function () {
  "use strict";

  function primaryNav() {
    return document.querySelector(".md-sidebar--primary .md-nav--primary");
  }

  function isNavBranchToggle(toggle) {
    return toggle && toggle.id && toggle.id.indexOf("__nav") === 0;
  }

  function activePageLink(nav) {
    if (!nav) {
      return null;
    }
    return nav.querySelector("a.md-nav__link--active[href]");
  }

  function collapseNavBranches(nav) {
    if (!nav) {
      return;
    }
    nav.querySelectorAll("input.md-nav__toggle").forEach(function (toggle) {
      if (!isNavBranchToggle(toggle)) {
        return;
      }
      toggle.checked = false;
      toggle.classList.remove("md-toggle--indeterminate");
    });
  }

  function expandAncestorsOf(link) {
    var item = link.closest(".md-nav__item");
    while (item) {
      var toggle = item.querySelector(":scope > input.md-nav__toggle");
      if (isNavBranchToggle(toggle)) {
        toggle.checked = true;
        toggle.classList.remove("md-toggle--indeterminate");
      }
      item = item.parentElement
        ? item.parentElement.closest(".md-nav__item")
        : null;
    }
  }

  function syncNavExpandToActiveNow() {
    var nav = primaryNav();
    if (!nav) {
      return;
    }
    collapseNavBranches(nav);
    var active = activePageLink(nav);
    if (active) {
      expandAncestorsOf(active);
    }
  }

  function syncNavExpandToActive() {
    window.requestAnimationFrame(function () {
      syncNavExpandToActiveNow();
      window.requestAnimationFrame(syncNavExpandToActiveNow);
    });
  }

  function bindInstant() {
    if (typeof document$ !== "undefined" && document$.subscribe) {
      document$.subscribe(syncNavExpandToActive);
    }
  }

  function init() {
    bindInstant();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
