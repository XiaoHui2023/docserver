(function () {
  "use strict";

  var FILTER_ID = "docserver-nav-filter";
  var HIDDEN = "docserver-nav-filter--hidden";
  var DEBOUNCE_MS = 120;
  var savedQuery = "";

  function sidebarInner() {
    return document.querySelector(".md-sidebar--primary .md-sidebar__inner");
  }

  function primaryNavRoot() {
    return document.querySelector(
      ".md-sidebar--primary .md-nav--primary > ul.md-nav__list"
    );
  }

  function navItemLabel(item) {
    var link =
      item.querySelector(":scope > a.md-nav__link") ||
      item.querySelector(":scope > label.md-nav__link");
    if (!link) {
      return "";
    }
    var ell = link.querySelector(".md-ellipsis");
    var text = (ell ? ell.textContent : link.textContent).replace(/\s+/g, " ").trim();
    var href = link.getAttribute("href");
    if (href && href !== ".") {
      return text + " " + href;
    }
    return text;
  }

  function childNavItems(item) {
    var sub = item.querySelector(":scope > nav.md-nav:not(.md-nav--secondary)");
    if (!sub) {
      return [];
    }
    var list = sub.querySelector(":scope > ul.md-nav__list");
    if (!list) {
      return [];
    }
    return Array.prototype.slice.call(
      list.querySelectorAll(":scope > li.md-nav__item")
    );
  }

  function setItemVisible(item, visible) {
    item.classList.toggle(HIDDEN, !visible);
  }

  function expandItem(item) {
    var toggle = item.querySelector(":scope > input.md-nav__toggle");
    if (toggle) {
      toggle.checked = true;
    }
  }

  function filterItem(item, query) {
    if (!query) {
      setItemVisible(item, true);
      childNavItems(item).forEach(function (child) {
        filterItem(child, "");
      });
      return true;
    }

    var hay = navItemLabel(item).toLowerCase();
    var selfMatch = hay.indexOf(query) !== -1;
    var childMatch = false;

    childNavItems(item).forEach(function (child) {
      if (filterItem(child, query)) {
        childMatch = true;
      }
    });

    var visible = selfMatch || childMatch;
    setItemVisible(item, visible);
    if (childMatch) {
      expandItem(item);
    }
    return visible;
  }

  function applyFilter(query) {
    var root = primaryNavRoot();
    if (!root) {
      return;
    }
    var q = query.trim().toLowerCase();
    var items = root.querySelectorAll(":scope > li.md-nav__item");
    var anyVisible = false;

    Array.prototype.forEach.call(items, function (item) {
      if (filterItem(item, q)) {
        anyVisible = true;
      }
    });

    var box = document.getElementById(FILTER_ID);
    if (box) {
      box.classList.toggle("docserver-nav-filter--empty", q.length > 0 && !anyVisible);
    }
  }

  function clearFilter(input) {
    savedQuery = "";
    input.value = "";
    applyFilter("");
    input.blur();
  }

  function mountNavFilter() {
    var inner = sidebarInner();
    if (!inner) {
      return;
    }
    var nav = inner.querySelector(".md-nav--primary");
    if (!nav || !nav.querySelector(":scope > ul.md-nav__list")) {
      return;
    }

    var existing = document.getElementById(FILTER_ID);
    if (existing && inner.contains(existing)) {
      var input = existing.querySelector(".docserver-nav-filter__input");
      if (input && input.value !== savedQuery) {
        input.value = savedQuery;
      }
      applyFilter(savedQuery);
      return;
    }
    if (existing) {
      existing.remove();
    }

    var wrap = document.createElement("div");
    wrap.className = "docserver-nav-filter";
    wrap.id = FILTER_ID;

    var input = document.createElement("input");
    input.type = "search";
    input.className = "docserver-nav-filter__input";
    input.setAttribute("aria-label", "筛选导航");
    input.placeholder = "筛选导航…";
    input.autocomplete = "off";
    input.spellcheck = false;

    var timer = 0;
    input.addEventListener("input", function () {
      savedQuery = input.value;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () {
        applyFilter(savedQuery);
      }, DEBOUNCE_MS);
    });

    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        ev.preventDefault();
        clearFilter(input);
      }
    });

    var empty = document.createElement("p");
    empty.className = "docserver-nav-filter__empty";
    empty.textContent = "无匹配项";

    wrap.appendChild(input);
    wrap.appendChild(empty);
    inner.insertBefore(wrap, nav);
    if (savedQuery) {
      input.value = savedQuery;
      applyFilter(savedQuery);
    }
  }

  function afterInstantNav() {
    var existing = document.getElementById(FILTER_ID);
    var inner = sidebarInner();
    if (existing && inner && inner.contains(existing)) {
      applyFilter(savedQuery);
      return;
    }
    mountNavFilter();
  }

  function bindNavigation() {
    if (typeof document$ !== "undefined" && document$.subscribe) {
      document$.subscribe(function () {
        afterInstantNav();
      });
      return;
    }
  }

  function init() {
    mountNavFilter();
    bindNavigation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", mountNavFilter);
})();
