/**
 * Network Health strip — compares darkstore-only vs darkstore + brand-store (Omuni) using dashboard SKU counts.
 */
(function () {
  var INV_ON_MULTIPLIER = 8.2;

  function formatApprox(n) {
    return "~" + Math.round(n).toLocaleString("en-IN");
  }

  function formatPart(n) {
    return "~" + Math.round(n).toLocaleString("en-IN");
  }

  function getCatalogLen() {
    var cat = window.LIFESTYLE_CATALOG;
    return cat && cat.length ? cat.length : 0;
  }

  function isOmuniOn() {
    var s = window.omuniState;
    return s && typeof s.isEnabled === "function" ? s.isEnabled() : false;
  }

  function updateInventoryNumbers() {
    var n = getCatalogLen();
    var elOff = document.getElementById("networkHealthInventoryOff");
    var elOffBracket = document.getElementById("networkHealthInventoryOffBracket");
    var elOn = document.getElementById("networkHealthInventoryOn");
    var elOnBracket = document.getElementById("networkHealthInventoryOnBracket");

    if (elOff) elOff.textContent = n > 0 ? formatApprox(n) : "—";
    if (elOffBracket) {
      elOffBracket.textContent =
        n > 0 ? "(" + formatPart(0) + " from stores + " + formatPart(n) + " from darkstores)" : "";
    }

    if (elOn) {
      if (n <= 0) {
        elOn.textContent = "—";
      } else {
        var totalOn = Math.round(n * INV_ON_MULTIPLIER);
        var fromDark = n;
        var fromStores = Math.max(0, totalOn - fromDark);
        elOn.textContent = formatApprox(totalOn);
        if (elOnBracket) {
          elOnBracket.textContent =
            "(" + formatPart(fromStores) + " from stores + " + formatPart(fromDark) + " from darkstores)";
        }
      }
    } else if (elOnBracket) {
      elOnBracket.textContent = "";
    }
  }

  function syncOmuniClusters() {
    var on = isOmuniOn();
    var offCluster = document.getElementById("networkHealthClusterOff");
    var onCluster = document.getElementById("networkHealthClusterOn");
    if (offCluster) offCluster.hidden = on;
    if (onCluster) onCluster.hidden = !on;

    var convOff = document.getElementById("networkHealthConvOff");
    var convOn = document.getElementById("networkHealthConvOn");
    if (convOff) convOff.hidden = on;
    if (convOn) convOn.hidden = !on;

    var mode = document.getElementById("networkHealthModeText");
    if (mode) {
      mode.textContent = on
        ? "Combined network: darkstores + brand stores — inventory reflects Omuni (darkstore + store) catalogue on this dashboard."
        : "Darkstore network only — inventory count reflects products available on this dashboard without nearby brand-store stock.";
    }
  }

  function activateTab(which) {
    var foot = which === "footprint";
    var tabF = document.getElementById("networkHealthTabFootprint");
    var tabC = document.getElementById("networkHealthTabConversion");
    var panF = document.getElementById("networkHealthPanelFootprint");
    var panC = document.getElementById("networkHealthPanelConversion");
    if (tabF) {
      tabF.classList.toggle("network-health__tab--active", foot);
      tabF.setAttribute("aria-selected", foot ? "true" : "false");
    }
    if (tabC) {
      tabC.classList.toggle("network-health__tab--active", !foot);
      tabC.setAttribute("aria-selected", !foot ? "true" : "false");
    }
    if (panF) panF.hidden = !foot;
    if (panC) panC.hidden = foot;
  }

  function initTabs() {
    var list = document.querySelector(".network-health__tabs");
    if (!list) return;
    list.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-network-health-tab]");
      if (!btn) return;
      var which = btn.getAttribute("data-network-health-tab");
      if (which === "footprint" || which === "conversion") activateTab(which);
    });
  }

  function refresh() {
    updateInventoryNumbers();
    syncOmuniClusters();
  }

  function boot() {
    initTabs();
    refresh();
    document.addEventListener("omuni:state-changed", function () {
      syncOmuniClusters();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
