(function () {
  "use strict";

  function primaryNav() {
    return document.querySelector(".md-sidebar--primary .md-nav--primary");
  }

  function primaryScrollEl() {
    var sidebar = document.querySelector(".md-sidebar--primary");
    if (!sidebar) {
      return null;
    }
    return sidebar.querySelector(".md-sidebar__scrollwrap");
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

  function elementTopInScroll(el, child) {
    var elRect = el.getBoundingClientRect();
    var childRect = child.getBoundingClientRect();
    return childRect.top - elRect.top + el.scrollTop;
  }

  function hasChildNav(item) {
    return !!item.querySelector(":scope > nav.md-nav");
  }

  function scrollActiveIntoView(link) {
    var el = primaryScrollEl();
    var item = link ? link.closest(".md-nav__item") : null;
    if (!el || !item) {
      return;
    }

    var target = hasChildNav(item) ? item : link;
    var margin = 16;
    var top = elementTopInScroll(el, target) - margin;
    var bottom =
      elementTopInScroll(el, target) + target.getBoundingClientRect().height + margin;
    var viewTop = el.scrollTop;
    var viewBottom = viewTop + el.clientHeight;

    if (top < viewTop || bottom > viewBottom) {
      el.scrollTop = Math.max(0, top);
    }
  }

  function syncNavExpandToActiveNow(options) {
    var nav = primaryNav();
    if (!nav) {
      return;
    }
    collapseNavBranches(nav);
    var active = activePageLink(nav);
    if (active) {
      expandAncestorsOf(active);
      if (!options || options.scroll !== false) {
        scrollActiveIntoView(active);
      }
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
    syncNavExpandToActive();
    bindInstant();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
