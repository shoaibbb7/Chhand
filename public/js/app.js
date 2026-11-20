/**
 * Main application entry point for Chhand.
 * Coordinates guided onboarding, editor, deterministic meter engine,
 * AI rewrites, rhyme assistant, and view routing (Poems, Meters, Rhymes).
 */

import { analyzePoem, findRhymes, requestRewrite } from "./api.js";
import { PoetryEditor } from "./editor.js";
import { MetersPage } from "./metersPage.js";
import { NavigationRouter } from "./navigation.js";
import { RhymesPage } from "./rhymesPage.js";
import { renderRhymePills, renderSuggestions } from "./suggestions.js";
import { METERS, parseCustomPattern } from "./templates.js";

const TERM_DEFINITIONS = {
  charan: {
    title: "What is a Charan (चरण)?",
    body: "A Charan is a quarter or rhythmic section of a verse. In a Doha, there are 4 charans (two per couplet) with targets of 13, 11, 13, and 11 matras. Each section has its own independent target and live matra count in Chhand.",
  },
  matra: {
    title: "What is a Matra (मात्रा)?",
    body: "A Matra is the basic rhythmic time unit in Hindi metrics. Short vowels (अ, इ, उ, ऋ) count as 1 matra (Laghu •). Long vowels (आ, ई, ऊ, ए, ऐ, ओ, औ) or syllables before conjuncts/anusvara count as 2 matras (Guru —).",
  },
};

class ChhandApp {
  constructor() {
    this.currentMeter = "doha";
    this.customPattern = [12, 12, 14, 12];
    this.pronunciationMode = "orthographic";
    this.activeCharanGlobalIndex = 3; // Focus Line 2 second charan by default
    this.activeLineText = "साथ रहेगा फिर नूर";
    this.activeTargetMatras = 11;
    this.currentAbortController = null;
    this.toastTimer = null;

    this.initDOM();
    this.initGuide();
    this.initEditor();
    this.initPages();
    this.bindEvents();

    // Initial analysis on page load
    this.runAnalysis(this.editor.getFlatCharans());
    this.loadRhymesForCurrentLine("नूर");
  }

  initDOM() {
    this.statusPill = document.getElementById("overall-status-pill");
    this.btnToggleGuide = document.getElementById("btn-toggle-guide");
    this.firstTimeGuide = document.getElementById("first-time-guide");
    this.btnDismissGuide = document.getElementById("btn-dismiss-guide");

    this.meterTabs = document.querySelectorAll(".meter-tab");
    this.customPatternRow = document.getElementById("custom-pattern-row");
    this.customPatternInput = document.getElementById("custom-pattern-input");
    this.meterExplanationBanner = document.getElementById("meter-explanation-banner");

    this.poemProgressTitle = document.getElementById("poem-progress-title");
    this.poemProgressBadges = document.getElementById("poem-progress-badges");
    this.btnLoadDemo = document.getElementById("btn-load-demo-example");
    this.btnLoadBroken = document.getElementById("btn-load-broken-example");

    this.coupletNameLabel = document.getElementById("couplet-name-label");
    this.coupletTargetLabel = document.getElementById("couplet-target-label");

    this.rewriteTargetLineLabel = document.getElementById("rewrite-target-line-label");
    this.rewriteTitle = document.getElementById("rewrite-title");
    this.btnTriggerRewrite = document.getElementById("btn-trigger-rewrite");
    this.suggestionsList = document.getElementById("suggestions-list");

    this.rhymePillsContainer = document.getElementById("rhyme-pills-container");
    this.rhymeSearchInput = document.getElementById("rhyme-search-input");
    this.btnFindRhymes = document.getElementById("btn-find-rhymes");

    this.btnAddCouplet = document.getElementById("btn-add-couplet");
    this.btnClearPoem = document.getElementById("btn-clear-poem");

    this.termPopover = document.getElementById("term-popover");
    this.termPopoverTitle = document.getElementById("term-popover-title");
    this.termPopoverBody = document.getElementById("term-popover-body");
    this.btnCloseTermPopover = document.getElementById("btn-close-term-popover");
  }

  initGuide() {
    const isDismissed = localStorage.getItem("chhand_intro_dismissed") === "true";
    if (this.firstTimeGuide) {
      this.firstTimeGuide.style.display = isDismissed ? "none" : "block";
    }

    if (this.btnDismissGuide) {
      this.btnDismissGuide.addEventListener("click", () => {
        if (this.firstTimeGuide) {
          this.firstTimeGuide.style.display = "none";
        }
        localStorage.setItem("chhand_intro_dismissed", "true");
        this.showToast("Guide dismissed. You can reopen it anytime using the Guide button in the header.");
      });
    }

    if (this.btnToggleGuide) {
      this.btnToggleGuide.addEventListener("click", () => {
        if (!this.firstTimeGuide) return;
        const isHidden = this.firstTimeGuide.style.display === "none";
        this.firstTimeGuide.style.display = isHidden ? "block" : "none";
        if (isHidden) {
          this.firstTimeGuide.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    }
  }

  initEditor() {
    const container = document.getElementById("couplets-lines-container");
    const targets = METERS[this.currentMeter]?.targets || [13, 11, 13, 11];

    this.editor = new PoetryEditor({
      container,
      targets,
      meterName: this.currentMeter,
      onAnalyzeRequired: (charans) => this.runAnalysis(charans),
      onActiveCharanChanged: (index, text) => this.handleActiveCharanChanged(index, text),
      onProgressUpdated: (progress) => this.handleProgressUpdated(progress),
    });
  }

  initPages() {
    // 1. Navigation Router
    this.router = new NavigationRouter({
      onRouteChanged: (route) => {
        if (route === "poems") {
          this.runAnalysis(this.editor.getFlatCharans());
        }
      },
    });

    // 2. Meters Page
    const metersContainer = document.getElementById("meters-view");
    if (metersContainer) {
      this.metersPage = new MetersPage({
        container: metersContainer,
        onSelectMeter: (meterId) => {
          this.setMeter(meterId);
          this.router.navigateTo("poems");
          this.showToast(`Selected meter: ${meterId === "doha" ? "दोहा (Doha)" : "चौपाई (Chaupai)"}`);
        },
        onSelectCustomMeter: (charans) => {
          this.customPattern = charans;
          if (this.customPatternInput) {
            this.customPatternInput.value = charans.join(", ");
          }
          this.setMeter("custom");
          this.router.navigateTo("poems");
          this.showToast(`Custom meter applied: ${charans.join(" | ")}`);
        },
      });
    }

    // 3. Rhymes Page
    const rhymesContainer = document.getElementById("rhymes-view");
    if (rhymesContainer) {
      this.rhymesPage = new RhymesPage({
        container: rhymesContainer,
        onUseInPoem: (word) => {
          this.insertRhymeWord(word);
        },
      });
    }
  }

  handleProgressUpdated(progress) {
    if (!this.poemProgressTitle || !progress) return;

    const { total, completed, notStarted, needsRevision, lineProgress } = progress;

    if (completed === total) {
      this.poemProgressTitle.textContent = `All ${total} sections in meter! Perfect poetic rhythm. ✓`;
      this.poemProgressTitle.className = "progress-title matched";
    } else if (completed === 0 && notStarted === total) {
      this.poemProgressTitle.textContent = "Start writing your poem by typing into any section below.";
      this.poemProgressTitle.className = "progress-title";
    } else {
      const parts = [];
      if (completed > 0) parts.push(`${completed} in meter`);
      if (needsRevision > 0) parts.push(`${needsRevision} need${needsRevision === 1 ? "s" : ""} revision`);
      if (notStarted > 0) parts.push(`${notStarted} not started`);

      this.poemProgressTitle.textContent = `${completed} of ${total} sections completed (${parts.join(", ")})`;
      this.poemProgressTitle.className = "progress-title";
    }

    // Render progress badge chips
    if (this.poemProgressBadges && lineProgress) {
      this.poemProgressBadges.textContent = "";
      lineProgress.forEach(item => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = `progress-chip ${item.status}`;
        
        let icon = "•";
        if (item.status === "matched") icon = "✓";
        else if (item.status === "revision") icon = "✗";

        chip.innerHTML = `<span class="chip-icon">${icon}</span> ${item.label}`;
        chip.title = `Click to jump to Section ${item.index + 1}`;
        chip.addEventListener("click", () => {
          this.editor.focusCharan(item.index);
        });
        this.poemProgressBadges.appendChild(chip);
      });
    }
  }

  insertRhymeWord(word) {
    const flat = this.editor.getFlatCharans();
    const current = (flat[this.activeCharanGlobalIndex] || "").trim();
    const updated = current ? `${current} ${word}` : word;
    this.editor.setCharanText(this.activeCharanGlobalIndex, updated);
    this.router.navigateTo("poems");
    this.showToast(`Inserted "${word}" into line`);
  }

  showToast(message) {
    const toast = document.getElementById("global-toast");
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = "block";
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => {
      toast.style.display = "none";
    }, 2800);
  }

  bindEvents() {
    // Meter Tabs
    this.meterTabs.forEach(tab => {
      tab.addEventListener("click", () => {
        const meter = tab.dataset.meter;
        this.setMeter(meter);
      });
    });

    // Custom Pattern Input
    this.customPatternInput.addEventListener("input", (e) => {
      const parsed = parseCustomPattern(e.target.value);
      if (parsed) {
        this.customPattern = parsed;
        this.editor.setTargets(parsed, "custom");
        this.updateExplanationBanner();
        this.runAnalysis(this.editor.getFlatCharans());
      }
    });

    // Demo Example Loaders
    if (this.btnLoadDemo) {
      this.btnLoadDemo.addEventListener("click", () => {
        this.loadDemoExample();
      });
    }

    if (this.btnLoadBroken) {
      this.btnLoadBroken.addEventListener("click", () => {
        this.loadBrokenExample();
      });
    }

    // AI Rewrite button
    this.btnTriggerRewrite.addEventListener("click", () => {
      this.generateRewrites();
    });

    // Rhyme Search Form
    const rhymeForm = document.getElementById("rhyme-search-form");
    if (rhymeForm) {
      rhymeForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const word = this.rhymeSearchInput.value.trim();
        if (word) {
          this.loadRhymesForCurrentLine(word);
        }
      });
    }

    if (this.btnFindRhymes) {
      this.btnFindRhymes.addEventListener("click", () => {
        const word = this.rhymeSearchInput.value.trim();
        if (word) {
          this.loadRhymesForCurrentLine(word);
        }
      });
    }

    // Add Couplet
    this.btnAddCouplet.addEventListener("click", () => {
      this.editor.addCouplet();
      this.showToast("Added new couplet line");
    });

    // Clear Poem
    this.btnClearPoem.addEventListener("click", () => {
      if (confirm("Are you sure you want to clear the editor?")) {
        this.editor.clearAll();
        this.showToast("Editor cleared");
      }
    });

    // Terminology help buttons
    document.querySelectorAll(".btn-term-help").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const term = e.currentTarget.dataset.term;
        this.showTermPopover(term, e.currentTarget);
      });
    });

    if (this.btnCloseTermPopover) {
      this.btnCloseTermPopover.addEventListener("click", () => {
        this.hideTermPopover();
      });
    }

    // Close popover when clicking outside
    document.addEventListener("click", (e) => {
      if (
        this.termPopover &&
        this.termPopover.style.display !== "none" &&
        !this.termPopover.contains(e.target) &&
        !e.target.closest(".btn-term-help")
      ) {
        this.hideTermPopover();
      }
    });
  }

  showTermPopover(term, triggerElement) {
    if (!this.termPopover || !TERM_DEFINITIONS[term]) return;

    const data = TERM_DEFINITIONS[term];
    this.termPopoverTitle.textContent = data.title;
    this.termPopoverBody.textContent = data.body;
    this.termPopover.style.display = "block";

    // Position popover near trigger if possible
    if (triggerElement) {
      const rect = triggerElement.getBoundingClientRect();
      const popoverRect = this.termPopover.getBoundingClientRect();
      const top = Math.max(10, rect.top - popoverRect.height - 8);
      const left = Math.min(window.innerWidth - popoverRect.width - 20, Math.max(10, rect.left));
      this.termPopover.style.top = `${top + window.scrollY}px`;
      this.termPopover.style.left = `${left + window.scrollX}px`;
    }
  }

  hideTermPopover() {
    if (this.termPopover) {
      this.termPopover.style.display = "none";
    }
  }

  loadDemoExample() {
    this.setMeter("doha");
    const demoCouplets = [
      { charans: ["मन का दीपक जब जले", "मिटे अँधेरा दूर"] },
      { charans: ["सीख सदा सच की रखो", "रहेगा सदा नूर"] },
    ];
    this.editor.loadCouplets(demoCouplets);
    this.showToast("Loaded classic Doha example (all sections in meter ✓)");
  }

  loadBrokenExample() {
    this.setMeter("doha");
    const brokenCouplets = [
      { charans: ["मन का दीपक जब जले", "मिटे अँधेरा दूर"] },
      { charans: ["सीख सदा सच की रखो", "साथ रहेगा फिर नूर"] }, // 13 matras, needs 11
    ];
    this.editor.loadCouplets(brokenCouplets);
    this.editor.focusCharan(3);
    this.showToast("Loaded broken example. Section 4 has 2 extra matras (13/11). Click 'Improve This Line'!");
  }

  setMeter(meter) {
    this.currentMeter = meter;
    this.meterTabs.forEach(t => {
      const isActive = t.dataset.meter === meter;
      t.classList.toggle("active", isActive);
      t.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    let targets = METERS[meter]?.targets || [13, 11, 13, 11];

    if (meter === "custom") {
      this.customPatternRow.style.display = "flex";
      targets = this.customPattern;
      this.coupletNameLabel.textContent = "Couplet 1 · Custom";
      this.coupletTargetLabel.textContent = this.customPattern.join(" | ");
    } else {
      this.customPatternRow.style.display = "none";
      const tmpl = METERS[meter];
      this.coupletNameLabel.textContent = `Couplet 1 · ${tmpl.name === "doha" ? "Doha" : "Chaupai"}`;
      this.coupletTargetLabel.textContent = tmpl.patternDisplay;
    }

    this.editor.setTargets(targets, meter);
    this.updateExplanationBanner();
    this.updateActiveCharanInfo();
    this.runAnalysis(this.editor.getFlatCharans());
  }

  updateExplanationBanner() {
    if (!this.meterExplanationBanner) return;
    if (this.currentMeter === "doha") {
      this.meterExplanationBanner.textContent =
        "दोहा (Doha) — Four rhythmic sections following the traditional 13 · 11 · 13 · 11 matra pattern.";
    } else if (this.currentMeter === "chaupai") {
      this.meterExplanationBanner.textContent =
        "चौपाई (Chaupai) — Four rhythmic sections, each following a 16-matra target.";
    } else {
      this.meterExplanationBanner.textContent =
        `कस्टम छंद (Custom) — Custom target: ${this.customPattern.join(" · ")} matras per section.`;
    }
  }

  handleActiveCharanChanged(index, text) {
    this.activeCharanGlobalIndex = index;
    this.activeLineText = text;
    this.updateActiveCharanInfo();

    // Extract last word for rhyme lookup if present
    const cleanWord = text.trim().split(/\s+/).pop() || "";
    if (cleanWord) {
      this.loadRhymesForCurrentLine(cleanWord);
    }
  }

  updateActiveCharanInfo() {
    let targets = METERS[this.currentMeter]?.targets || [13, 11, 13, 11];
    if (this.currentMeter === "custom") {
      targets = this.customPattern;
    }
    const targetIdx = this.activeCharanGlobalIndex % targets.length;
    this.activeTargetMatras = targets[targetIdx];

    const sectionNum = this.activeCharanGlobalIndex + 1;
    this.rewriteTargetLineLabel.textContent = `SECTION ${sectionNum} · चरण ${sectionNum}`;

    if (this.currentMeter === "doha") {
      this.rewriteTitle.textContent = `Need help fixing Section ${sectionNum}? (Target: ${this.activeTargetMatras})`;
    } else if (this.currentMeter === "chaupai") {
      this.rewriteTitle.textContent = `Need help fixing Section ${sectionNum}? (Target: 16)`;
    } else {
      this.rewriteTitle.textContent = `Need help fixing Section ${sectionNum}? (Target: ${this.activeTargetMatras})`;
    }

    // Update button text and state
    const flat = this.editor.getFlatCharans();
    const currentText = (flat[this.activeCharanGlobalIndex] || "").trim();
    if (!currentText) {
      this.btnTriggerRewrite.disabled = true;
      this.btnTriggerRewrite.innerHTML = '<span>Type in Section to Improve</span>';
    } else {
      this.btnTriggerRewrite.disabled = false;
      this.btnTriggerRewrite.innerHTML = '<span>Improve This Line</span>';
    }
  }

  async runAnalysis(charans) {
    if (this.currentAbortController) {
      this.currentAbortController.abort();
    }
    this.currentAbortController = new AbortController();

    try {
      const payload = {
        meter: this.currentMeter,
        charans: charans,
        custom_pattern: this.currentMeter === "custom" ? this.customPattern : null,
        pronunciation_mode: this.pronunciation_mode,
      };

      const result = await analyzePoem(payload, this.currentAbortController.signal);
      this.editor.updateAnalysis(result);
      this.updateOverallStatus(result);
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Analysis error:", err);
      }
    }
  }

  updateOverallStatus(result) {
    if (!result) return;
    this.statusPill.textContent = result.summary;
    this.statusPill.className = `nav-status ${result.overall_status === "matched" ? "matched" : ""}`;
  }

  async generateRewrites() {
    const flat = this.editor.getFlatCharans();
    const currentText = (flat[this.activeCharanGlobalIndex] || this.activeLineText || "").trim();

    if (!currentText) {
      this.showToast("Please enter a line first before requesting rewrites.");
      return;
    }

    this.btnTriggerRewrite.disabled = true;
    this.btnTriggerRewrite.innerHTML = '<span class="loading-spinner"></span> Finding Hindi alternatives that fit your rhythm...';

    try {
      // Extract rhyme requirement from partner charan if in rhyming position
      let rhymeRequirement = null;
      if (this.activeCharanGlobalIndex % 2 === 1 && this.activeCharanGlobalIndex >= 3) {
        const partnerIndex = this.activeCharanGlobalIndex - 2;
        const partnerText = flat[partnerIndex] || "";
        const words = partnerText.trim().split(/\s+/);
        if (words.length > 0 && words[words.length - 1]) {
          rhymeRequirement = words[words.length - 1];
        }
      }

      const payload = {
        original_line: currentText,
        target_matra_count: this.activeTargetMatras,
        selected_meter: this.currentMeter,
        charan_index: this.activeCharanGlobalIndex,
        custom_pattern: this.currentMeter === "custom" ? this.customPattern : null,
        instructions: "Preserve the original meaning and natural poetic tone.",
        rhyme_requirement: rhymeRequirement,
        max_suggestions: 3,
        pronunciation_mode: this.pronunciation_mode,
      };

      const res = await requestRewrite(payload);

      renderSuggestions(
        res.suggestions,
        this.suggestionsList,
        (acceptedLine) => {
          this.editor.setCharanText(this.activeCharanGlobalIndex, acceptedLine);
          this.runAnalysis(this.editor.getFlatCharans());
          this.showToast("Accepted rewrite. Scansion updated.");
        },
        (_skippedIdx) => {
          this.showToast("Suggestion dismissed.");
        }
      );
    } catch (err) {
      console.warn("Rewrite request:", err);
      this.suggestionsList.textContent = "";
      const errBox = document.createElement("div");
      errBox.className = "empty-state";
      if (err.code === "GEMINI_NOT_CONFIGURED" || err.code === "LLM_NOT_CONFIGURED") {
        errBox.textContent = "AI suggestions are currently unavailable. Meter analysis and rhyme search are still available.";
      } else if (err.code === "NO_VERIFIED_SUGGESTIONS" || err.code === "NO_VERIFIED_REWRITES") {
        errBox.textContent = "We couldn't find a verified alternative this time. Try changing your instructions or try again.";
      } else {
        errBox.textContent = err.message || "Failed to generate verified rewrites.";
      }
      this.suggestionsList.appendChild(errBox);
    } finally {
      this.btnTriggerRewrite.disabled = false;
      this.btnTriggerRewrite.innerHTML = '<span>Improve This Line</span>';
    }
  }

  async loadRhymesForCurrentLine(word) {
    if (!word) return;
    try {
      const res = await findRhymes(word, 8);
      const allWords = [...(res.exact_matches || []), ...(res.approximate_matches || [])];

      const contextNote = document.getElementById("rhyme-context-note");
      if (contextNote) {
        const sectionNum = this.activeCharanGlobalIndex + 1;
        if (this.activeCharanGlobalIndex % 2 === 1 && this.activeCharanGlobalIndex >= 3) {
          const partnerIndex = this.activeCharanGlobalIndex - 2;
          const flat = this.editor.getFlatCharans();
          const partnerText = flat[partnerIndex] || "";
          const partnerWord = partnerText.trim().split(/\s+/).pop() || "";
          if (partnerWord) {
            contextNote.textContent = `Section ${sectionNum} ends in "${res.original_word}", rhyming with "${partnerWord}" on Section ${partnerIndex + 1}.`;
          } else {
            contextNote.textContent = `Section ${sectionNum} ends in "${res.original_word}".`;
          }
        } else {
          contextNote.textContent = `Rhymes for "${res.original_word}". Click any word to copy or search.`;
        }
      }

      const endingLabel = document.getElementById("rhyme-ending-label");
      if (endingLabel && res.rhyme_tail) {
        endingLabel.style.display = "block";
        endingLabel.textContent = `Other endings in -${res.rhyme_tail}`;
      }

      renderRhymePills(allWords, this.rhymePillsContainer, (selectedWord) => {
        this.rhymeSearchInput.value = selectedWord;
        this.showToast(`Selected rhyme: "${selectedWord}"`);
      });
    } catch (err) {
      console.error("Rhyme fetch error:", err);
    }
  }
}

// Bootstrap application on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.chhandApp = new ChhandApp();
});
