/**
 * Client-side Router and Navigation controller for Chhand.
 * Manages view switching between Poems, Meters, and Rhymes.
 */

export class NavigationRouter {
  constructor(options = {}) {
    this.routes = ["poems", "meters", "rhymes"];
    this.currentRoute = "poems";
    this.onRouteChanged = options.onRouteChanged || null;

    this.init();
  }

  init() {
    window.addEventListener("hashchange", () => {
      this.handleHashChange();
    });

    // Handle initial route on page load
    this.handleHashChange();
  }

  handleHashChange() {
    const rawHash = window.location.hash.replace("#", "").trim().toLowerCase();
    const route = this.routes.includes(rawHash) ? rawHash : "poems";
    this.activateRoute(route, false);
  }

  navigateTo(route, updateHistory = true) {
    if (!this.routes.includes(route)) return;
    if (updateHistory) {
      window.location.hash = route;
    }
    this.activateRoute(route, updateHistory);
  }

  activateRoute(route, updateHash = false) {
    this.currentRoute = route;

    if (updateHash && window.location.hash !== `#${route}`) {
      window.location.hash = route;
    }

    // 1. Update Navigation Links in Header
    document.querySelectorAll(".nav-link").forEach(link => {
      const href = link.getAttribute("href") || "";
      const linkRoute = href.replace("#", "").trim().toLowerCase();
      const isActive = linkRoute === route;
      link.classList.toggle("active", isActive);
      link.setAttribute("aria-current", isActive ? "page" : "false");
    });

    // 2. Toggle View Containers
    document.querySelectorAll(".app-view").forEach(view => {
      const viewRoute = view.dataset.view;
      if (viewRoute === route) {
        view.style.display = "";
        view.removeAttribute("hidden");
      } else {
        view.style.display = "none";
        view.setAttribute("hidden", "true");
      }
    });

    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: "instant" });

    // 3. Fire route change callback
    if (this.onRouteChanged) {
      this.onRouteChanged(route);
    }
  }
}
