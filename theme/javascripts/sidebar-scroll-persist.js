(function () {
  "use strict";

  var primaryScrollTop = 0;
  var hasPrimaryScroll = false;
  var pendingRestorePath = null;

  function primaryScrollEl() {
    var sidebar = document.querySelector(".md-sidebar--primary");
    if (!sidebar) {
      return null;
    }
    return sidebar.querySelector(".md-sidebar__scrollwrap");
  }

  function rememberPrimaryScroll() {
    var el = primaryScrollEl();
    if (!el) {
      return;
    }
    primaryScrollTop = el.scrollTop;
    hasPrimaryScroll = true;
  }

  function normalizePath(pathname) {
    var path = pathname || "/";
    try {
      path = decodeURIComponent(path);
    } catch (e) {
      path = pathname || "/";
    }
    if (path.length > 1 && path.charAt(path.length - 1) === "/") {
      path = path.slice(0, -1);
    }
    if (path === "/index.html") {
      return "/";
    }
    if (path.length > "/index.html".length && path.endsWith("/index.html")) {
      path = path.slice(0, -"/index.html".length) || "/";
    }
    return path || "/";
  }

  function currentPath() {
    return normalizePath(window.location.pathname);
  }

  function restorePrimaryScroll() {
    if (!hasPrimaryScroll) {
      return;
    }
    var el = primaryScrollEl();
    if (!el) {
      return;
    }
    var top = primaryScrollTop;
    function apply() {
      el.scrollTop = top;
    }
    apply();
    window.requestAnimationFrame(function () {
      apply();
      window.requestAnimationFrame(apply);
    });
  }

  function isInternalNavLink(anchor) {
    var href = anchor.getAttribute("href");
    if (!href || href.charAt(0) === "#") {
      return false;
    }
    try {
      var url = new URL(href, window.location.href);
      return url.origin === window.location.origin;
    } catch (e) {
      return false;
    }
  }

  function targetPath(anchor) {
    try {
      return normalizePath(new URL(anchor.getAttribute("href"), window.location.href).pathname);
    } catch (e) {
      return null;
    }
  }

  function bindScrollMemory() {
    var el = primaryScrollEl();
    if (!el || el.dataset.docserverScrollBound) {
      return;
    }
    el.dataset.docserverScrollBound = "1";
    el.addEventListener(
      "scroll",
      function () {
        rememberPrimaryScroll();
      },
      { passive: true }
    );
  }

  function bindClickCapture() {
    if (document.body && document.body.dataset.docserverSidebarScrollCapture) {
      return;
    }
    if (document.body) {
      document.body.dataset.docserverSidebarScrollCapture = "1";
    }
    document.addEventListener(
      "click",
      function (ev) {
        var anchor = ev.target.closest("a[href]");
        if (!anchor || !isInternalNavLink(anchor)) {
          return;
        }
        var target = targetPath(anchor);
        if (target && target === currentPath()) {
          pendingRestorePath = target;
          rememberPrimaryScroll();
        } else {
          pendingRestorePath = null;
          hasPrimaryScroll = false;
        }
      },
      true
    );
  }

  function onInstantPage() {
    bindScrollMemory();
    if (pendingRestorePath && pendingRestorePath === currentPath()) {
      restorePrimaryScroll();
    }
    pendingRestorePath = null;
  }

  function bindInstant() {
    if (typeof document$ !== "undefined" && document$.subscribe) {
      document$.subscribe(onInstantPage);
    }
  }

  function init() {
    bindScrollMemory();
    bindClickCapture();
    bindInstant();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
