/* Fitness Depot Columbia — site behaviour
   Progressive enhancement only: every section works with JS disabled. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------------
     Mobile navigation
     --------------------------------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    var closeNav = function () {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      nav.classList.toggle("is-open", !open);
      toggle.setAttribute("aria-expanded", String(!open));
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeNav();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeNav();
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1100) closeNav();
    });
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
    var revealer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            revealer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    Array.prototype.forEach.call(revealables, function (el) {
      revealer.observe(el);
    });
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
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var match = sections.filter(function (s) {
            return s.target === entry.target;
          })[0];
          if (!match) return;
          if (entry.isIntersecting) {
            sections.forEach(function (s) {
              s.link.removeAttribute("aria-current");
            });
            match.link.setAttribute("aria-current", "true");
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (s) {
      spy.observe(s.target);
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

    var now = centralNow();
    if (now) {
      var window_ = STAFFED[now.day];
      var staffed =
        !!window_ && now.minutes >= window_[0] * 60 && now.minutes < window_[1] * 60;

      Array.prototype.forEach.call(statusEls, function (el) {
        el.textContent = staffed
          ? "Front desk open now"
          : "Front desk closed — members have 24/7 access";
      });
    }
  }

  /* ---------------------------------------------------------------------
     Current year in the footer
     --------------------------------------------------------------------- */
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
