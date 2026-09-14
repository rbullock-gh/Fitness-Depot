/* Fitness Depot Columbia — site behaviour
   Progressive enhancement only: every section works with JS disabled. */
(function () {
  "use strict";

  // Tells the inline head script that this file actually ran, so it leaves the
  // .js flag (and therefore the hidden .reveal blocks) in place.
  document.documentElement.setAttribute("data-reveal-ready", "");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------------
     Mobile navigation
     --------------------------------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    var navIsOpen = function () {
      return toggle.getAttribute("aria-expanded") === "true";
    };

    var closeNav = function () {
      if (!navIsOpen()) return;
      // The panel is about to become visibility:hidden. If focus is inside it,
      // hand focus back to the toggle rather than letting it fall to <body>,
      // which would restart tabbing from the top of the document.
      var focusInside = nav.contains(document.activeElement);
      nav.classList.remove("is-open");
      nav.style.maxHeight = "";
      toggle.setAttribute("aria-expanded", "false");
      if (focusInside) toggle.focus();
    };

    toggle.addEventListener("click", function () {
      if (navIsOpen()) {
        closeNav();
        return;
      }
      nav.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      // Size the panel to the space actually below it. The CSS fallback assumes
      // the header sits at the top of the viewport, which is not true while the
      // topbar is still on screen -- on a short phone that over-allocated and
      // pushed the last link off the bottom with no way to scroll to it.
      nav.style.maxHeight =
        Math.max(160, window.innerHeight - nav.getBoundingClientRect().top - 12) + "px";
      // The toggle sits after the panel in source order, so without this the
      // next Tab would skip the menu entirely and land behind the overlay.
      // The panel is coming out of visibility:hidden and focus() is a no-op
      // until the browser has recomputed it as visible, hence the frame wait.
      var first = nav.querySelector("a");
      if (first) {
        window.requestAnimationFrame(function () {
          first.focus();
        });
      }
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeNav();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && navIsOpen()) closeNav();
    });

    // Read the SAME media query the stylesheet uses. window.innerWidth counts
    // the classic scrollbar and the media query does not, so on a desktop with
    // a ~15px scrollbar the two disagree between 1161 and 1176 and the menu
    // snapped shut while the user was still dragging the window edge.
    var mobileNav = window.matchMedia("(max-width: 1160px)");
    var onBreakpointChange = function (e) {
      if (!e.matches) closeNav();
    };
    if (mobileNav.addEventListener) {
      mobileNav.addEventListener("change", onBreakpointChange);
    } else if (mobileNav.addListener) {
      mobileNav.addListener(onBreakpointChange);
    }
  }

  /* ---------------------------------------------------------------------
     Header shadow once the page scrolls
     --------------------------------------------------------------------- */
  var header = document.querySelector(".header");
  var toTop = document.querySelector(".to-top");

  var onScroll = function () {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-stuck", y > 8);
    if (toTop) toTop.classList.toggle("is-visible", y > 700);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }

  /* ---------------------------------------------------------------------
     Scroll reveal
     --------------------------------------------------------------------- */
  var revealables = document.querySelectorAll(".reveal");

  if (!("IntersectionObserver" in window) || reduceMotion) {
    Array.prototype.forEach.call(revealables, function (el) {
      el.classList.add("is-in");
    });
  } else {
    var pending = Array.prototype.slice.call(revealables);

    var show = function (el) {
      el.classList.add("is-in");
      revealer.unobserve(el);
      var at = pending.indexOf(el);
      if (at !== -1) pending.splice(at, 1);
    };

    var revealer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) show(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    Array.prototype.forEach.call(revealables, function (el) {
      revealer.observe(el);
    });

    // Safety sweep. A fast fling can carry an element from below the viewport
    // to above it between two frames; the observer never sees it intersecting,
    // so its state never CHANGES and no callback ever fires for it. Nothing
    // removes .is-in, so that block would stay invisible for the rest of the
    // session. Runs only once scrolling has settled, and only over what is
    // still hidden, so it costs nothing on a normal scroll.
    var sweepTimer;
    var sweep = function () {
      if (!pending.length) return;
      var limit = window.innerHeight;
      pending.slice().forEach(function (el) {
        if (el.getBoundingClientRect().top < limit) show(el);
      });
    };

    window.addEventListener(
      "scroll",
      function () {
        if (!pending.length) return;
        window.clearTimeout(sweepTimer);
        sweepTimer = window.setTimeout(sweep, 140);
      },
      { passive: true }
    );
  }

  /* ---------------------------------------------------------------------
     Nav scrollspy
     --------------------------------------------------------------------- */
  var navLinks = nav ? nav.querySelectorAll('a[href^="#"]') : [];
  var sections = [];

  Array.prototype.forEach.call(navLinks, function (link) {
    var target = document.getElementById(link.getAttribute("href").slice(1));
    if (target) sections.push({ link: link, target: target });
  });

  if (sections.length && "IntersectionObserver" in window) {
    // Track what is actually in the band. Setting aria-current only when a
    // section enters leaves the last one marked after you scroll back to the
    // hero, where no section is in the band and the nav should be quiet.
    var inBand = [];

    var paint = function () {
      sections.forEach(function (s) {
        s.link.removeAttribute("aria-current");
      });
      if (inBand.length) {
        inBand[inBand.length - 1].link.setAttribute("aria-current", "true");
      }
    };

    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var match = sections.filter(function (s) {
            return s.target === entry.target;
          })[0];
          if (!match) return;
          var at = inBand.indexOf(match);
          if (entry.isIntersecting) {
            if (at === -1) inBand.push(match);
          } else if (at !== -1) {
            inBand.splice(at, 1);
          }
        });
        paint();
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (s) {
      spy.observe(s.target);
    });
  }

  /* ---------------------------------------------------------------------
     Amenity ticker pause control (WCAG 2.2.2)
     --------------------------------------------------------------------- */
  var tickerToggle = document.querySelector("[data-marquee-toggle]");

  if (tickerToggle) {
    var strip = tickerToggle.parentNode;
    var tickerLabel = tickerToggle.querySelector(".sr-only");

    tickerToggle.addEventListener("click", function () {
      var paused = tickerToggle.getAttribute("aria-pressed") === "true";
      tickerToggle.setAttribute("aria-pressed", String(!paused));
      strip.classList.toggle("is-paused", !paused);
      if (tickerLabel) {
        tickerLabel.textContent = paused
          ? "Pause the scrolling amenity list"
          : "Resume the scrolling amenity list";
      }
    });
  }

  /* ---------------------------------------------------------------------
     Defer the map iframe until it is close to the viewport
     --------------------------------------------------------------------- */
  var map = document.querySelector("[data-map-src]");
  if (map) {
    var loadMap = function () {
      if (map.getAttribute("src")) return;
      map.setAttribute("src", map.getAttribute("data-map-src"));
    };
    if ("IntersectionObserver" in window) {
      var mapObserver = new IntersectionObserver(
        function (entries) {
          if (entries[0].isIntersecting) {
            loadMap();
            mapObserver.disconnect();
          }
        },
        { rootMargin: "400px" }
      );
      mapObserver.observe(map);
    } else {
      loadMap();
    }
  }

  /* ---------------------------------------------------------------------
     Front-desk status.
     Staffed desk hours (Central time): Mon-Thu 8:00am-7:00pm, Fri 8:00am-5:00pm.
     Member access is 24/7, so the "closed" state says exactly that.
     --------------------------------------------------------------------- */
  var statusEls = document.querySelectorAll("[data-desk-status]");

  if (statusEls.length) {
    // day index -> [openHour, closeHour] in 24h Central time; absent = unstaffed
    var STAFFED = { 1: [8, 19], 2: [8, 19], 3: [8, 19], 4: [8, 19], 5: [8, 17] };

    var centralNow = function () {
      try {
        var parts = new Intl.DateTimeFormat("en-US", {
          timeZone: "America/Chicago",
          weekday: "short",
          hour: "numeric",
          minute: "numeric",
          hour12: false
        }).formatToParts(new Date());

        var get = function (type) {
          var p = parts.filter(function (x) {
            return x.type === type;
          })[0];
          return p ? p.value : null;
        };

        var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
        var hour = parseInt(get("hour"), 10);
        return {
          day: days[get("weekday")],
          minutes: (hour === 24 ? 0 : hour) * 60 + parseInt(get("minute"), 10)
        };
      } catch (err) {
        return null;
      }
    };

    // Recomputed on a timer and whenever the tab is shown again. Computing it
    // once meant a page left open past 7pm -- or a phone waking from sleep --
    // still read "Front desk open now" and sent someone to a locked desk.
    var renderDeskStatus = function () {
      var now = centralNow();
      if (!now) return;

      var window_ = STAFFED[now.day];
      var staffed =
        !!window_ && now.minutes >= window_[0] * 60 && now.minutes < window_[1] * 60;

      Array.prototype.forEach.call(statusEls, function (el) {
        el.textContent = staffed
          ? "Front desk open now · members enter 24/7"
          : "Front desk closed — members have 24/7 access";
      });
    };

    renderDeskStatus();
    window.setInterval(renderDeskStatus, 60000);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) renderDeskStatus();
    });
  }

  /* ---------------------------------------------------------------------
     Current year in the footer
     --------------------------------------------------------------------- */
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
