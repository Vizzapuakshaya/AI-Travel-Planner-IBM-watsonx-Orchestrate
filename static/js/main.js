/**
 * TravelPlannerAI — Main JavaScript
 * IBM watsonx Orchestrate powered travel planning
 */

"use strict";

/* ═══════════════════════════════════════════════════════════
   GLOBAL UTILITIES
═══════════════════════════════════════════════════════════ */

const App = {
  loading: null,

  init() {
    this.loading = document.getElementById("loadingOverlay");
    this.initNavbar();
    this.initAnimations();
    this.initTooltips();
    this.initDateDefaults();
  },

  showLoading(msg = "Generating your personalized itinerary…") {
    if (!this.loading) return;
    const txt = this.loading.querySelector(".loading-text");
    if (txt) txt.textContent = msg;
    this.loading.classList.add("active");
  },

  hideLoading() {
    if (this.loading) this.loading.classList.remove("active");
  },

  showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const icons = { success: "check-circle", danger: "exclamation-circle", warning: "exclamation-triangle", info: "info-circle" };
    const id = "toast_" + Date.now();
    const html = `
      <div id="${id}" class="toast align-items-center text-bg-${type} border-0 shadow" role="alert" aria-live="assertive">
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center gap-2">
            <i class="fas fa-${icons[type] || "info-circle"}"></i>
            <span>${message}</span>
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    container.insertAdjacentHTML("beforeend", html);
    const el = document.getElementById(id);
    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
    el.addEventListener("hidden.bs.toast", () => el.remove());
  },

  initNavbar() {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;
    const onScroll = () => {
      navbar.style.boxShadow = window.scrollY > 30
        ? "0 4px 20px rgba(0,0,0,0.25)"
        : "none";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
  },

  initAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animationPlayState = "running";
          e.target.classList.add("visible");
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".fade-in-up, .fade-in").forEach(el => {
      el.style.animationPlayState = "paused";
      observer.observe(el);
    });
  },

  initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el);
    });
  },

  initDateDefaults() {
    const today = new Date().toISOString().split("T")[0];
    const plusWeek = new Date(Date.now() + 7 * 864e5).toISOString().split("T")[0];
    const startEl = document.getElementById("start_date");
    const endEl   = document.getElementById("end_date");
    if (startEl && !startEl.value) { startEl.min = today; startEl.value = today; }
    if (endEl   && !endEl.value)   { endEl.min   = today; endEl.value   = plusWeek; }
    if (startEl && endEl) {
      startEl.addEventListener("change", () => {
        endEl.min = startEl.value;
        if (endEl.value < startEl.value) endEl.value = startEl.value;
      });
    }
  },
};

/* ═══════════════════════════════════════════════════════════
   HERO QUICK-SEARCH (landing page)
═══════════════════════════════════════════════════════════ */

function heroSearch() {
  const dest = document.getElementById("heroDestination");
  if (!dest || !dest.value.trim()) {
    App.showToast("Please enter a destination to get started.", "warning");
    dest && dest.focus();
    return;
  }
  sessionStorage.setItem("prefill_destination", dest.value.trim());
  window.location.href = "/plan";
}

/* ═══════════════════════════════════════════════════════════
   TRIP PLANNER FORM
═══════════════════════════════════════════════════════════ */

const Planner = {
  currentStep: 1,
  totalSteps:  3,

  init() {
    const form = document.getElementById("tripForm");
    if (!form) return;

    // Pre-fill destination from hero search
    const prefill = sessionStorage.getItem("prefill_destination");
    if (prefill) {
      const destInput = document.getElementById("destination");
      if (destInput) destInput.value = prefill;
      sessionStorage.removeItem("prefill_destination");
    }

    form.addEventListener("submit", (e) => { e.preventDefault(); this.submit(); });
    this.updateStepUI();
  },

  next() {
    if (!this.validateStep(this.currentStep)) return;
    if (this.currentStep < this.totalSteps) {
      this.currentStep++;
      this.updateStepUI();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  },

  prev() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateStepUI();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  },

  validateStep(step) {
    const panels = document.querySelectorAll(".step-panel");
    const panel  = panels[step - 1];
    if (!panel) return true;
    let ok = true;
    panel.querySelectorAll("[required]").forEach(input => {
      if (!input.value.trim()) {
        input.classList.add("is-invalid");
        ok = false;
      } else {
        input.classList.remove("is-invalid");
      }
    });
    if (!ok) App.showToast("Please fill in all required fields.", "warning");
    return ok;
  },

  updateStepUI() {
    // Panels
    document.querySelectorAll(".step-panel").forEach((p, i) => {
      p.style.display = (i + 1 === this.currentStep) ? "block" : "none";
    });
    // Step indicators
    document.querySelectorAll(".step").forEach((s, i) => {
      s.classList.remove("active", "done");
      if (i + 1 === this.currentStep) s.classList.add("active");
      if (i + 1 <  this.currentStep)  s.classList.add("done");
    });
    // Buttons
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const subBtn  = document.getElementById("submitBtn");
    if (prevBtn) prevBtn.style.display = this.currentStep > 1 ? "inline-flex" : "none";
    if (nextBtn) nextBtn.style.display = this.currentStep < this.totalSteps ? "inline-flex" : "none";
    if (subBtn)  subBtn.style.display  = this.currentStep === this.totalSteps ? "inline-flex" : "none";
  },

  async submit() {
    if (!this.validateStep(this.currentStep)) return;

    const preferences = [];
    document.querySelectorAll(".pref-check:checked").forEach(cb => preferences.push(cb.value));

    const payload = {
      destination:          document.getElementById("destination")?.value.trim()   || "",
      start_date:           document.getElementById("start_date")?.value           || "",
      end_date:             document.getElementById("end_date")?.value             || "",
      budget:               document.querySelector(".budget-opt:checked")?.value   || "medium",
      travelers:            document.getElementById("travelers")?.value            || 2,
      preferences,
      special_requirements: document.getElementById("special_requirements")?.value.trim() || "",
    };

    if (!payload.destination || !payload.start_date || !payload.end_date) {
      App.showToast("Please fill in destination and travel dates.", "warning");
      return;
    }

    App.showLoading("✈ IBM watsonx Orchestrate is crafting your personalized itinerary…");

    try {
      const res  = await fetch("/api/generate-itinerary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success) {
        App.showToast("Itinerary generated successfully!", "success");
        setTimeout(() => { window.location.href = "/itinerary"; }, 800);
      } else {
        App.hideLoading();
        App.showToast(data.error || "Generation failed. Please try again.", "danger");
      }
    } catch (err) {
      App.hideLoading();
      App.showToast("Network error. Please check your connection.", "danger");
      console.error(err);
    }
  },
};

/* ═══════════════════════════════════════════════════════════
   ITINERARY PAGE
═══════════════════════════════════════════════════════════ */

const Itinerary = {
  init() {
    this.initAccordion();
    this.animateBudgetBars();
    this.initChecklistPersist();
  },

  initAccordion() {
    document.querySelectorAll(".day-header").forEach(header => {
      header.addEventListener("click", () => {
        const body  = header.nextElementSibling;
        const icon  = header.querySelector(".toggle-icon");
        const isOpen = body?.style.display !== "none";
        body.style.display = isOpen ? "none" : "block";
        if (icon) icon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
      });
    });
  },

  animateBudgetBars() {
    const bars = document.querySelectorAll(".budget-bar .progress-bar");
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const bar   = e.target;
          const width = bar.getAttribute("data-width") || "50";
          setTimeout(() => { bar.style.width = width + "%"; }, 100);
          observer.unobserve(bar);
        }
      });
    }, { threshold: 0.3 });
    bars.forEach(b => { b.style.width = "0"; observer.observe(b); });
  },

  initChecklistPersist() {
    document.querySelectorAll(".checklist-item input[type=checkbox]").forEach(cb => {
      const key = "chk_" + cb.id;
      cb.checked = localStorage.getItem(key) === "1";
      cb.addEventListener("change", () => localStorage.setItem(key, cb.checked ? "1" : "0"));
    });
  },

  async downloadPDF() {
    App.showLoading("Generating your PDF itinerary…");
    try {
      const res = await fetch("/api/download-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "PDF generation failed");
      }
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = "travel_itinerary.pdf";
      a.click();
      URL.revokeObjectURL(url);
      App.showToast("PDF downloaded successfully!", "success");
    } catch (err) {
      App.showToast(err.message || "Could not download PDF.", "danger");
    } finally {
      App.hideLoading();
    }
  },

  printItinerary() {
    window.print();
  },
};

/* ═══════════════════════════════════════════════════════════
   DESTINATION QUICK-INFO (landing page cards)
═══════════════════════════════════════════════════════════ */

async function exploreDestination(dest) {
  App.showLoading(`Loading ${dest} highlights…`);
  try {
    const res  = await fetch("/api/destination-info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ destination: dest }),
    });
    const data = await res.json();
    App.hideLoading();
    if (data.success) {
      sessionStorage.setItem("prefill_destination", dest);
      window.location.href = "/plan";
    }
  } catch {
    App.hideLoading();
    sessionStorage.setItem("prefill_destination", dest);
    window.location.href = "/plan";
  }
}

/* ═══════════════════════════════════════════════════════════
   CONTACT FORM
═══════════════════════════════════════════════════════════ */

function handleContactForm(e) {
  e.preventDefault();
  const btn = e.target.querySelector('[type=submit]');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending…'; }
  setTimeout(() => {
    App.showToast("Message sent! We'll reply within 24 hours.", "success");
    e.target.reset();
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Send Message'; }
  }, 1200);
}

/* ═══════════════════════════════════════════════════════════
   BOOT
═══════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  App.init();
  Planner.init();
  Itinerary.init();

  // Contact form (client-side fallback)
  const contactForm = document.getElementById("contactForm");
  if (contactForm) contactForm.addEventListener("submit", handleContactForm);
});
