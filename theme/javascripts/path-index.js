(function () {
  "use strict";

  var navIndexPaths = null;
  var navPagePaths = null;
  var metaLoading = false;

  function siteBase() {
    if (typeof __md_get === "function") {
      var base = __md_get("base");
      if (base) {
        return base;
      }
    }
    return "/";
  }

  function navMetaUrl() {
    return new URL(
      "javascripts/docserver-nav-meta.json",
      new URL(siteBase(), window.location.href)
    ).href;
  }

  function normalizePathname(pathname) {
    if (!pathname) {
      return "/";
    }
    var path = pathname;
    try {
      path = decodeURIComponent(pathname);
    } catch (e) {
      path = pathname;
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

  function normalizeIndexPath(pathname) {
    var norm = normalizePathname(pathname);
    if (norm === "/") {
      return "/";
    }
    return norm + "/";
  }

  function linkTargetIndexPath(link) {
    var href = link.getAttribute("href");
    if (!href || href.charAt(0) === "#") {
      return null;
    }
    try {
      return normalizeIndexPath(
        new URL(href, window.location.href).pathname
      );
    } catch (e) {
      return null;
    }
  }

  function currentPagePath() {
    return normalizeIndexPath(normalizePathname(window.location.pathname));
  }

  function isPathLinkEnabled(target) {
    if (!target) {
      return false;
    }
    if (navIndexPaths.has(target)) {
      return true;
    }
    if (target === currentPagePath()) {
      return false;
    }
    return navPagePaths.has(target);
  }

  function loadNavMeta(done) {
    if (navPagePaths && navIndexPaths) {
      done();
      return;
    }
    if (metaLoading) {
      window.setTimeout(function () {
        loadNavMeta(done);
      }, 50);
      return;
    }
    metaLoading = true;
    fetch(navMetaUrl())
      .then(function (res) {
        if (!res.ok) {
          throw new Error("nav meta");
        }
        return res.json();
      })
      .then(function (data) {
        navIndexPaths = new Set(data.index_paths || []);
        navPagePaths = new Set(data.page_paths || data.index_paths || []);
        metaLoading = false;
        done();
      })
      .catch(function () {
        navIndexPaths = null;
        navPagePaths = null;
        metaLoading = false;
        done();
      });
  }

  function applyPathBar() {
    var pathNav = document.querySelector(".md-content .md-path");
    if (!pathNav || !navPagePaths || !navIndexPaths) {
      return;
    }

    var items = pathNav.querySelectorAll(".md-path__item");

    items.forEach(function (item) {
      var link = item.querySelector(".md-path__link");
      item.classList.remove("md-path__item--disabled");
      if (!link) {
        return;
      }
      var target = linkTargetIndexPath(link);
      var enabled = isPathLinkEnabled(target);
      if (enabled) {
        link.classList.remove("md-path__link--disabled");
        link.removeAttribute("aria-disabled");
        link.removeAttribute("tabindex");
      } else {
        link.classList.add("md-path__link--disabled");
        link.setAttribute("aria-disabled", "true");
        link.setAttribute("tabindex", "-1");
      }
    });
  }

  function run() {
    loadNavMeta(function () {
      window.requestAnimationFrame(applyPathBar);
    });
  }

  function bind() {
    if (typeof document$ !== "undefined" && document$.subscribe) {
      document$.subscribe(run);
    }
    if (typeof location$ !== "undefined" && location$.subscribe) {
      location$.subscribe(run);
    }
  }

  function init() {
    run();
    bind();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", run);
})();
