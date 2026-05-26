(function () {
  "use strict";

  var navIndexPaths = null;
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

  function pathSegments(pathname) {
    var norm = normalizePathname(pathname);
    if (norm === "/") {
      return [];
    }
    return norm.split("/").filter(Boolean);
  }

  function directoryIndexPath(segments, depth) {
    if (depth <= 0) {
      return "/";
    }
    return "/" + segments.slice(0, depth).join("/") + "/";
  }

  function loadNavMeta(done) {
    if (navIndexPaths) {
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
        metaLoading = false;
        done();
      })
      .catch(function () {
        navIndexPaths = new Set();
        metaLoading = false;
        done();
      });
  }

  function applyPathBar() {
    var pathNav = document.querySelector(".md-content .md-path");
    if (!pathNav || !navIndexPaths) {
      return;
    }

    var segments = pathSegments(window.location.pathname);
    var pagePath = normalizePathname(window.location.pathname);
    var items = pathNav.querySelectorAll(".md-path__item");

    items.forEach(function (item, index) {
      var link = item.querySelector(".md-path__link");
      item.classList.remove("md-path__item--disabled");
      if (!link) {
        return;
      }
      var isLast = index === items.length - 1;
      var canonical = isLast
        ? pagePath
        : directoryIndexPath(segments, index);
      if (
        isLast &&
        navIndexPaths.has(directoryIndexPath(segments, segments.length))
      ) {
        canonical = directoryIndexPath(segments, segments.length);
      }
      var enabled = navIndexPaths.has(normalizeIndexPath(canonical));
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
