(function () {
  "use strict";

  var SCHEME_KEY = "docserver-scheme";
  var STYLE_KEY = "docserver-style";

  function readSchemeFromMaterialStorage() {
    if (typeof __md_get !== "function") {
      return null;
    }
    try {
      var palette = __md_get("__palette");
      if (palette && palette.color && palette.color.scheme) {
        return palette.color.scheme;
      }
      if (typeof __md_scope !== "undefined") {
        var rootPath = new URL("/", __md_scope).pathname;
        var raw = localStorage.getItem(rootPath + ".__palette");
        if (raw) {
          var parsed = JSON.parse(raw);
          if (parsed && parsed.color && parsed.color.scheme) {
            return parsed.color.scheme;
          }
        }
      }
    } catch (e) {
      /* ignore */
    }
    return null;
  }

  try {
    var root = document.documentElement;
    var style = localStorage.getItem(STYLE_KEY);
    if (style) {
      root.setAttribute("data-docserver-style", style);
    }
    var scheme = localStorage.getItem(SCHEME_KEY);
    if (scheme !== "default" && scheme !== "slate") {
      scheme = readSchemeFromMaterialStorage();
    }
    if (scheme === "default" || scheme === "slate") {
      root.setAttribute("data-docserver-scheme-guard", scheme);
      localStorage.setItem(SCHEME_KEY, scheme);
    }
  } catch (e) {
    /* ignore */
  }
})();
