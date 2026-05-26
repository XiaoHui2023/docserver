(function () {
  "use strict";

  var STORAGE_KEY = "docserver-style";
  var SCHEME_KEY = "docserver-scheme";
  var DEFAULT_STYLE = "j";

  /** 顺序：J 默认放首位；其余见 THEME-PALETTES.md */
  var STYLE_ORDER = [
    "j",
    "i",
    "k",
    "l",
    "c",
    "b",
    "a",
    "d",
    "e",
    "f",
    "g",
    "h",
  ];

  /** 有 theme/palettes/*.css 配套，不依赖 Material 内置色板名 */
  var STYLES_WITH_PALETTE_CSS = { j: 1, i: 1, k: 1, l: 1, c: 1 };

  var STYLES = {
    j: {
      label: "GitHub 灰栏",
      hint: "浅灰顶栏与侧栏，蓝色链接",
      primary: { default: "grey", slate: "black" },
      accent: { default: "blue", slate: "light blue" },
    },
    i: {
      label: "GitHub 经典",
      hint: "白底黑字，深色模式黑顶栏",
      primary: { default: "white", slate: "black" },
      accent: { default: "blue", slate: "blue" },
    },
    k: {
      label: "纯灰极简",
      hint: "蓝灰低饱和，长时间阅读",
      primary: { default: "blue grey", slate: "blue grey" },
      accent: { default: "blue", slate: "light blue" },
    },
    l: {
      label: "黑白蓝链",
      hint: "黑顶栏 + 蓝链接，侧栏随明暗",
      primary: { default: "black", slate: "black" },
      accent: { default: "blue", slate: "light blue" },
    },
    c: {
      label: "青绿运维",
      hint: "青绿主色，偏基础设施文档",
      primary: { default: "teal", slate: "teal" },
      accent: { default: "green", slate: "light green" },
    },
    b: {
      label: "企业蓝",
      hint: "Material 企业蓝主色",
      primary: { default: "blue", slate: "blue" },
      accent: { default: "light blue", slate: "light blue" },
    },
    a: {
      label: "经典靛蓝",
      hint: "Material 靛蓝技术文档风",
      primary: { default: "indigo", slate: "indigo" },
      accent: { default: "indigo", slate: "indigo" },
    },
    d: {
      label: "深紫产品",
      hint: "深紫主色 + 粉色强调",
      primary: { default: "deep purple", slate: "deep purple" },
      accent: { default: "pink", slate: "pink" },
    },
    e: {
      label: "蓝灰专业",
      hint: "蓝灰主色 + 青色强调",
      primary: { default: "blue grey", slate: "blue grey" },
      accent: { default: "cyan", slate: "cyan" },
    },
    f: {
      label: "青橙对比",
      hint: "青色主色 + 橙色强调",
      primary: { default: "cyan", slate: "cyan" },
      accent: { default: "orange", slate: "orange" },
    },
    g: {
      label: "森林绿",
      hint: "绿色主色，开源平台风",
      primary: { default: "green", slate: "green" },
      accent: { default: "light green", slate: "light green" },
    },
    h: {
      label: "深色顶栏",
      hint: "黑顶栏 + 琥珀色强调",
      primary: { default: "black", slate: "black" },
      accent: { default: "amber", slate: "amber" },
    },
  };

  var TRIGGER_TOOLTIP = "切换配色风格";
  var SHARE_TOOLTIP = "复制页面链接";
  var SHARE_COPIED = "链接已复制到剪贴板";

  /** Material link-variant 图标 */
  var SHARE_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path fill="currentColor" d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1M8 13h8v-2H8v2m9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5"/></svg>';

  var shareFeedbackTimer = null;

  function materialColorSlug(name) {
    return String(name).trim().toLowerCase().replace(/\s+/g, "-");
  }

  /** Material「apps」网格图标，表示多套配色方案 */
  var STYLE_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path fill="currentColor" d="M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"/>' +
    "</svg>";

  function getSavedStyle() {
    try {
      var id = localStorage.getItem(STORAGE_KEY);
      return STYLES[id] ? id : DEFAULT_STYLE;
    } catch (e) {
      return DEFAULT_STYLE;
    }
  }

  function currentScheme() {
    return document.body.getAttribute("data-md-color-scheme") === "slate"
      ? "slate"
      : "default";
  }

  function applyMaterialColors(styleId) {
    var cfg = STYLES[styleId] || STYLES[DEFAULT_STYLE];
    var scheme = currentScheme();
    document.body.setAttribute(
      "data-md-color-primary",
      materialColorSlug(cfg.primary[scheme])
    );
    document.body.setAttribute(
      "data-md-color-accent",
      materialColorSlug(cfg.accent[scheme])
    );
  }

  function clearMaterialColors() {
    document.body.removeAttribute("data-md-color-primary");
    document.body.removeAttribute("data-md-color-accent");
  }

  function updateSchemeGuard(scheme) {
    if (scheme !== "default" && scheme !== "slate") {
      return;
    }
    document.documentElement.setAttribute("data-docserver-scheme-guard", scheme);
    try {
      localStorage.setItem(SCHEME_KEY, scheme);
    } catch (e) {
      /* ignore */
    }
  }

  function colorFromPaletteInput(input) {
    if (!input) {
      return null;
    }
    return {
      media: input.getAttribute("data-md-color-media") || "",
      scheme: input.getAttribute("data-md-color-scheme"),
      primary: input.getAttribute("data-md-color-primary"),
      accent: input.getAttribute("data-md-color-accent"),
    };
  }

  function readPaletteFromMaterialStorage() {
    if (typeof __md_get !== "function") {
      return null;
    }
    try {
      var palette = __md_get("__palette");
      if (palette && palette.color) {
        return palette.color;
      }
      if (typeof __md_scope !== "undefined") {
        var rootPath = new URL("/", __md_scope).pathname;
        var raw = localStorage.getItem(rootPath + ".__palette");
        if (raw) {
          var parsed = JSON.parse(raw);
          if (parsed && parsed.color) {
            return parsed.color;
          }
        }
      }
    } catch (e) {
      /* ignore */
    }
    return null;
  }

  /** 顶栏 radio 在 instant 换页时仍保留；Material 的 __palette 按路径分桶，不能单靠 __md_get */
  function readPaletteColor() {
    var checked = document.querySelector('input[name="__palette"]:checked');
    var fromDom = colorFromPaletteInput(checked);
    if (fromDom && fromDom.scheme) {
      return fromDom;
    }
    var stored = null;
    try {
      var scheme = localStorage.getItem(SCHEME_KEY);
      if (scheme === "default" || scheme === "slate") {
        stored = { scheme: scheme };
      }
    } catch (e) {
      /* ignore */
    }
    var color = readPaletteFromMaterialStorage();
    if (!color) {
      return stored;
    }
    if (color.media === "(prefers-color-scheme)") {
      var media = matchMedia("(prefers-color-scheme: light)");
      var input = document.querySelector(
        media.matches
          ? "[data-md-color-media='(prefers-color-scheme: light)']"
          : "[data-md-color-media='(prefers-color-scheme: dark)']"
      );
      if (input) {
        return colorFromPaletteInput(input);
      }
    }
    return color;
  }

  function pinSchemeGuard() {
    var color = readPaletteColor();
    if (color && color.scheme) {
      updateSchemeGuard(color.scheme);
      return;
    }
    if (document.body) {
      var scheme = document.body.getAttribute("data-md-color-scheme");
      if (scheme === "default" || scheme === "slate") {
        updateSchemeGuard(scheme);
      }
    }
  }

  function shouldSkipMaterialColorKey(key) {
    if (key === "primary" || key === "accent") {
      return !!STYLES_WITH_PALETTE_CSS[getSavedStyle()];
    }
    return false;
  }

  /** 按 localStorage 校正 body 配色；自定义 palette CSS 时不写 primary/accent，避免 instant 换页闪一下 */
  function applyBodyPaletteFromStorage() {
    if (!document.body) {
      return;
    }
    var color = readPaletteColor();
    if (!color) {
      return;
    }
    updateSchemeGuard(color.scheme);
    Object.keys(color).forEach(function (key) {
      if (key === "media" || shouldSkipMaterialColorKey(key)) {
        return;
      }
      var val = color[key];
      if (!val) {
        return;
      }
      var attr = "data-md-color-" + key;
      if (document.body.getAttribute(attr) !== val) {
        document.body.setAttribute(attr, val);
      }
    });
    if (STYLES_WITH_PALETTE_CSS[getSavedStyle()]) {
      clearMaterialColors();
    }
  }

  function restoreMaterialPalette() {
    applyBodyPaletteFromStorage();
  }

  function refreshDocserverColors() {
    var id = getSavedStyle();
    document.documentElement.setAttribute("data-docserver-style", id);
    if (!STYLES_WITH_PALETTE_CSS[id]) {
      applyMaterialColors(id);
    }
  }

  function syncPaletteRadios() {
    if (!document.body) {
      return;
    }
    var scheme = document.body.getAttribute("data-md-color-scheme");
    if (!scheme) {
      return;
    }
    document.querySelectorAll('input[name="__palette"]').forEach(function (input) {
      input.checked = input.getAttribute("data-md-color-scheme") === scheme;
    });
  }

  function closeStyleMenu(menu) {
    if (!menu) {
      return;
    }
    menu.classList.remove("docserver-style-picker__menu--open");
    var trigger = menu.querySelector(".docserver-style-picker__trigger");
    var list = menu.querySelector(".docserver-style-picker__list");
    if (trigger) {
      trigger.setAttribute("aria-expanded", "false");
    }
    if (list) {
      list.hidden = true;
    }
  }

  function closeAllStyleMenus(except) {
    document.querySelectorAll(".docserver-style-picker__menu").forEach(function (menu) {
      if (menu !== except) {
        closeStyleMenu(menu);
      }
    });
  }

  function openStyleMenu(menu) {
    closeAllStyleMenus(menu);
    menu.classList.add("docserver-style-picker__menu--open");
    var trigger = menu.querySelector(".docserver-style-picker__trigger");
    var list = menu.querySelector(".docserver-style-picker__list");
    if (trigger) {
      trigger.setAttribute("aria-expanded", "true");
    }
    if (list) {
      list.hidden = false;
    }
  }

  function syncAllPickers(styleId) {
    document.querySelectorAll(".docserver-style-picker__select").forEach(function (el) {
      if (el.value !== styleId) {
        el.value = styleId;
      }
    });
    document.querySelectorAll(".docserver-style-picker__item").forEach(function (item) {
      var active = item.getAttribute("data-value") === styleId;
      item.classList.toggle("docserver-style-picker__item--active", active);
      item.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  function applyStyle(styleId, persist) {
    var id = STYLES[styleId] ? styleId : DEFAULT_STYLE;
    document.documentElement.setAttribute("data-docserver-style", id);
    if (persist !== false) {
      try {
        localStorage.setItem(STORAGE_KEY, id);
      } catch (e) {
        /* ignore */
      }
    }
    if (STYLES_WITH_PALETTE_CSS[id]) {
      clearMaterialColors();
    } else {
      applyMaterialColors(id);
    }
    syncAllPickers(id);
    syncTriggerTooltip(id);
  }

  function syncTriggerTooltip(styleId) {
    var cfg = STYLES[styleId] || STYLES[DEFAULT_STYLE];
    var tip = TRIGGER_TOOLTIP + "：" + cfg.label;
    document
      .querySelectorAll(".docserver-style-picker__trigger")
      .forEach(function (btn) {
        btn.title = tip;
        btn.setAttribute("data-tooltip", tip);
        btn.setAttribute("aria-label", tip);
      });
  }

  function buildSelect(className) {
    var select = document.createElement("select");
    select.className = "docserver-style-picker__select " + className;
    select.setAttribute("aria-label", "配色风格");

    STYLE_ORDER.forEach(function (id) {
      var opt = document.createElement("option");
      opt.value = id;
      opt.textContent = STYLES[id].label;
      select.appendChild(opt);
    });

    select.value = getSavedStyle();
    select.addEventListener("change", function () {
      applyStyle(select.value, true);
    });
    return select;
  }

  function buildStyleMenu() {
    var menu = document.createElement("div");
    menu.className = "docserver-style-picker__menu";

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className =
      "md-header__button md-icon docserver-style-picker__trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.innerHTML = STYLE_ICON;

    var list = document.createElement("ul");
    list.className = "docserver-style-picker__list";
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", "配色风格");
    list.hidden = true;

    STYLE_ORDER.forEach(function (id) {
      var item = document.createElement("li");
      item.className = "docserver-style-picker__item";
      item.setAttribute("role", "option");
      item.setAttribute("data-value", id);
      item.textContent = STYLES[id].label;
      item.title = STYLES[id].hint || STYLES[id].label;
      item.addEventListener("click", function () {
        applyStyle(id, true);
        closeStyleMenu(menu);
      });
      list.appendChild(item);
    });

    trigger.addEventListener("click", function (ev) {
      ev.stopPropagation();
      if (menu.classList.contains("docserver-style-picker__menu--open")) {
        closeStyleMenu(menu);
      } else {
        openStyleMenu(menu);
      }
    });

    menu.appendChild(trigger);
    menu.appendChild(list);
    return menu;
  }

  function clipboardCopiedMessage() {
    return SHARE_COPIED;
  }

  function decodeUriComponentSafe(part) {
    if (!part) {
      return part;
    }
    try {
      return decodeURIComponent(part.replace(/\+/g, " "));
    } catch (e) {
      return part;
    }
  }

  /** 复制用 URL：pathname/search/hash 中的 % 编码还原为 Unicode（如中文路径） */
  function getPageShareUrl() {
    var url = new URL(window.location.href);
    var path = url.pathname
      .split("/")
      .map(function (segment) {
        return segment ? decodeUriComponentSafe(segment) : segment;
      })
      .join("/");
    var search = "";
    if (url.search.length > 1) {
      search = "?" + decodeUriComponentSafe(url.search.slice(1));
    }
    var hash = "";
    if (url.hash.length > 1) {
      hash = "#" + decodeUriComponentSafe(url.hash.slice(1));
    }
    return url.origin + path + search + hash;
  }

  function copyTextFallback(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    document.body.removeChild(area);
  }

  function hideShareToast(wrap) {
    var toast = wrap && wrap.querySelector(".docserver-page-share__toast");
    if (!toast) {
      return;
    }
    toast.classList.remove("docserver-page-share__toast--visible");
    toast.setAttribute("hidden", "");
  }

  function showShareCopiedFeedback(trigger) {
    var wrap = trigger.closest(".docserver-page-share");
    var toast = wrap && wrap.querySelector(".docserver-page-share__toast");
    if (!toast) {
      return;
    }
    toast.textContent = clipboardCopiedMessage();
    toast.removeAttribute("hidden");
    toast.classList.add("docserver-page-share__toast--visible");
    if (shareFeedbackTimer) {
      window.clearTimeout(shareFeedbackTimer);
    }
    shareFeedbackTimer = window.setTimeout(function () {
      shareFeedbackTimer = null;
      hideShareToast(wrap);
    }, 1800);
  }

  function copyPageLink(trigger) {
    var text = getPageShareUrl();
    var done = function () {
      showShareCopiedFeedback(trigger);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(text)
        .then(done)
        .catch(function () {
          copyTextFallback(text);
          done();
        });
      return;
    }
    copyTextFallback(text);
    done();
  }

  function mountPageShare() {
    var header = document.querySelector(".md-header__inner");
    if (!header) {
      return;
    }
    var search = header.querySelector("[data-md-component=search]");
    if (!search) {
      return;
    }
    var existing = document.getElementById("docserver-page-share");
    if (existing) {
      if (!existing.querySelector(".docserver-page-share__toast")) {
        var legacyToast = document.createElement("span");
        legacyToast.className = "docserver-page-share__toast";
        legacyToast.setAttribute("role", "status");
        legacyToast.setAttribute("aria-live", "polite");
        legacyToast.hidden = true;
        existing.appendChild(legacyToast);
      }
      return;
    }

    var wrap = document.createElement("div");
    wrap.className = "md-header__option docserver-page-share";
    wrap.id = "docserver-page-share";

    var toast = document.createElement("span");
    toast.className = "docserver-page-share__toast";
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.hidden = true;

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "md-header__button md-icon docserver-page-share__trigger";
    trigger.title = SHARE_TOOLTIP;
    trigger.setAttribute("aria-label", SHARE_TOOLTIP);
    trigger.innerHTML = SHARE_ICON;
    trigger.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      copyPageLink(trigger);
    });

    wrap.appendChild(trigger);
    wrap.appendChild(toast);
    search.after(wrap);
    reorderHeaderControls(header);
  }

  function reorderHeaderControls(header) {
    if (header.dataset.docserverHeaderOrdered === "1") {
      return;
    }
    var palette = header.querySelector("[data-md-component=palette]");
    var search = header.querySelector("[data-md-component=search]");
    var pageShare = document.getElementById("docserver-page-share");
    var stylePicker = document.getElementById("docserver-style-picker-header");
    var searchLabel = header.querySelector('label[for="__search"]');
    if (!palette || !search) {
      return;
    }
    if (searchLabel && searchLabel.nextElementSibling !== search) {
      header.insertBefore(searchLabel, search);
    }

    function placeAfter(node, ref) {
      if (node && ref && ref.nextElementSibling !== node) {
        ref.after(node);
      }
    }

    var anchor = search;
    placeAfter(pageShare, anchor);
    if (pageShare) {
      anchor = pageShare;
    }
    placeAfter(stylePicker, anchor);
    if (stylePicker) {
      anchor = stylePicker;
    }
    placeAfter(palette, anchor);
    header.dataset.docserverHeaderOrdered = "1";
  }

  function mountHeaderPicker() {
    var header = document.querySelector(".md-header__inner");
    if (!header) {
      return;
    }

    var existing = document.getElementById("docserver-style-picker-header");
    if (existing && existing.querySelector(".docserver-style-picker__trigger")) {
      syncAllPickers(getSavedStyle());
      reorderHeaderControls(header);
      return;
    }
    if (existing) {
      existing.remove();
    }

    var palette = header.querySelector("[data-md-component=palette]");
    if (!palette) {
      return;
    }

    var wrap = document.createElement("div");
    wrap.className =
      "md-header__option docserver-style-picker docserver-style-picker--header";
    wrap.id = "docserver-style-picker-header";
    wrap.appendChild(buildStyleMenu());
    palette.before(wrap);
    reorderHeaderControls(header);
  }

  function mountDrawerPicker() {
    if (document.getElementById("docserver-style-picker-drawer")) {
      return;
    }
    var nav = document.querySelector(".md-sidebar--primary .md-nav--primary");
    if (!nav) {
      return;
    }
    var list = nav.querySelector(":scope > ul.md-nav__list");
    if (!list) {
      return;
    }

    var wrap = document.createElement("div");
    wrap.className = "docserver-style-picker docserver-style-picker--drawer";
    wrap.id = "docserver-style-picker-drawer";

    var label = document.createElement("span");
    label.className = "docserver-style-picker__label";
    label.textContent = "配色风格";

    var select = buildSelect("docserver-style-picker__select--drawer");
    wrap.appendChild(label);
    wrap.appendChild(select);
    nav.insertBefore(wrap, list);
  }

  function bindSchemeToggle() {
    document.querySelectorAll('input[name="__palette"]').forEach(function (input) {
      if (input.dataset.docserverBound) {
        return;
      }
      input.dataset.docserverBound = "1";
      input.addEventListener("change", function () {
        var id = getSavedStyle();
        if (!STYLES_WITH_PALETTE_CSS[id]) {
          applyMaterialColors(id);
        }
        pinSchemeGuard();
      });
    });
  }

  function bindGlobalDismiss() {
    if (document.body.dataset.docserverStyleDismiss) {
      return;
    }
    document.body.dataset.docserverStyleDismiss = "1";
    document.addEventListener("click", function () {
      closeAllStyleMenus();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        closeAllStyleMenus();
      }
    });
  }

  /** instant 换页后仅同步顶栏控件，避免重复全量初始化 */
  function onPageReady() {
    if (!document.body) {
      return;
    }
    var saved = getSavedStyle();
    mountPageShare();
    mountHeaderPicker();
    syncAllPickers(saved);
    syncTriggerTooltip(saved);
    mountDrawerPicker();
    bindSchemeToggle();
  }

  /** instant 换页：只钉住 scheme-guard，不改 body（避免搜索栏重算配色） */
  function syncAfterInstantNavigation() {
    pinSchemeGuard();
    refreshDocserverColors();
    syncPaletteRadios();
  }

  function bindInstantNavigation() {
    if (typeof location$ !== "undefined" && location$.subscribe) {
      location$.subscribe(function () {
        pinSchemeGuard();
      });
    }
    if (typeof document$ !== "undefined" && document$.subscribe) {
      document$.subscribe(function () {
        syncAfterInstantNavigation();
      });
    }
  }

  function init() {
    if (!document.body) {
      return;
    }
    var saved = getSavedStyle();
    restoreMaterialPalette();
    applyStyle(saved, false);
    syncPaletteRadios();
    bindSchemeToggle();
    bindGlobalDismiss();
    bindInstantNavigation();
    pinSchemeGuard();
    onPageReady();
  }

  try {
    document.documentElement.setAttribute("data-docserver-style", getSavedStyle());
    pinSchemeGuard();
  } catch (e) {
    /* ignore */
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", function () {
    syncAfterInstantNavigation();
  });
})();
