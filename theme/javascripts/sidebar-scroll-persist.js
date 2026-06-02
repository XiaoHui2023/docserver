(function () {
  "use strict";

  var primaryScrollTop = 0;
  var hasPrimaryScroll = false;

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
        rememberPrimaryScroll();
      },
      true
    );
  }

  function onInstantPage() {
    bindScrollMemory();
    restorePrimaryScroll();
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
