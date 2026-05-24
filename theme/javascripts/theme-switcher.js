(function () {
  "use strict";

  var STORAGE_KEY = "docserver-style";
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

  function reorderHeaderControls(header) {
    var palette = header.querySelector("[data-md-component=palette]");
    var search = header.querySelector("[data-md-component=search]");
    var stylePicker = document.getElementById("docserver-style-picker-header");
    var searchLabel = header.querySelector('label[for="__search"]');
    if (!palette || !search) {
      return;
    }
    if (searchLabel && searchLabel.nextElementSibling !== search) {
      header.insertBefore(searchLabel, search);
    }
    if (stylePicker) {
      if (search.nextElementSibling !== stylePicker) {
        search.after(stylePicker);
      }
      if (stylePicker.nextElementSibling !== palette) {
        stylePicker.after(palette);
      }
    } else if (search.nextElementSibling !== palette) {
      search.after(palette);
    }
    header.dataset.docserverHeaderOrdered = "1";
  }

  function mountHeaderPicker() {
    var header = document.querySelector(".md-header__inner");
    if (!header) {
      return;
    }
    reorderHeaderControls(header);

    var existing = document.getElementById("docserver-style-picker-header");
    if (existing && existing.querySelector(".docserver-style-picker__trigger")) {
      syncAllPickers(getSavedStyle());
      delete header.dataset.docserverHeaderOrdered;
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
    delete header.dataset.docserverHeaderOrdered;
    reorderHeaderControls(header);
  }

  function mountDrawerPicker() {
    if (document.getElementById("docserver-style-picker-drawer")) {
      return;
    }
    var nav = document.querySelector(".md-sidebar--primary .md-nav");
    if (!nav) {
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
    nav.insertBefore(wrap, nav.firstChild);
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

  function init() {
    if (!document.body) {
      return;
    }
    var saved = getSavedStyle();
    applyStyle(saved, false);
    mountHeaderPicker();
    syncTriggerTooltip(saved);
    mountDrawerPicker();
    bindSchemeToggle();
    bindGlobalDismiss();
  }

  try {
    document.documentElement.setAttribute(
      "data-docserver-style",
      getSavedStyle()
    );
  } catch (e) {
    /* ignore */
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", init);

  document.addEventListener(
    "click",
    function (ev) {
      var link = ev.target.closest && ev.target.closest("a");
      if (!link || !link.href) {
        return;
      }
      try {
        if (link.origin !== location.origin) {
          return;
        }
      } catch (e) {
        return;
      }
      window.setTimeout(init, 150);
    },
    true
  );
})();
