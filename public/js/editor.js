/**
 * Poetry Editor component for Chhand.
 * Manages charan inputs, real-time scansion, per-section status tracking,
 * and collapsible akshara-by-akshara matra breakdown drawers.
 */

import { formatLineStatusBadge, renderDetailedScansionGrid, renderScansionMarks } from "./meterBar.js";

export class PoetryEditor {
  constructor(options = {}) {
    this.container = options.container;
    this.onAnalyzeRequired = options.onAnalyzeRequired || null;
    this.onActiveCharanChanged = options.onActiveCharanChanged || null;
    this.onProgressUpdated = options.onProgressUpdated || null;

    this.targets = options.targets || [13, 11, 13, 11];
    this.meterName = options.meterName || "doha";

    // Initial default poem: classical Doha
    this.lines = [
      { charans: ["मन का दीपक जब जले", "मिटे अँधेरा दूर"] },
      { charans: ["सीख सदा सच की रखो", "साथ रहेगा फिर नूर"] },
    ];

    this.activeCharanGlobalIndex = 3; // Focus Line 2 second charan by default
    this.debounceTimer = null;
    this.openDrawers = new Set(); // Tracks indices of opened detail drawers
    this.lastAnalysisResults = null;

    this.render();
  }

  setTargets(targets, meterName = "custom") {
    this.targets = targets;
    this.meterName = meterName;
    this.render();
    this.triggerDebouncedAnalysis();
  }

  getFlatCharans() {
    const list = [];
    this.lines.forEach(line => {
      list.push(line.charans[0] || "");
      list.push(line.charans[1] || "");
    });
    return list;
  }

  setCharanText(globalIndex, text) {
    let count = 0;
    for (let l = 0; l < this.lines.length; l++) {
      for (let c = 0; c < 2; c++) {
        if (count === globalIndex) {
          this.lines[l].charans[c] = text;
          const input = this.container.querySelector(`[data-global-index="${globalIndex}"]`);
          if (input) {
            input.value = text;
          }
          this.triggerDebouncedAnalysis();
          return;
        }
        count++;
      }
    }
  }

  loadCouplets(couplets) {
    if (!Array.isArray(couplets) || couplets.length === 0) return;
    this.lines = couplets.map(c => ({
      charans: [c.charans[0] || "", c.charans[1] || ""],
    }));
    this.render();
    this.triggerDebouncedAnalysis();
  }

  focusCharan(globalIndex) {
    this.activeCharanGlobalIndex = globalIndex;
    const input = this.container.querySelector(`[data-global-index="${globalIndex}"]`);
    if (input) {
      input.focus();
      const flat = this.getFlatCharans();
      if (this.onActiveCharanChanged) {
        this.onActiveCharanChanged(globalIndex, flat[globalIndex] || "");
      }
    }
  }

  addCouplet() {
    this.lines.push({ charans: ["", ""] });
    this.render();
    this.triggerDebouncedAnalysis();
  }

  clearAll() {
    this.lines = [
      { charans: ["", ""] },
      { charans: ["", ""] },
    ];
    this.openDrawers.clear();
    this.render();
    this.triggerDebouncedAnalysis();
  }

  triggerDebouncedAnalysis() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      if (this.onAnalyzeRequired) {
        this.onAnalyzeRequired(this.getFlatCharans());
      }
    }, 280);
  }

  render() {
    this.container.textContent = "";

    this.lines.forEach((line, lineIdx) => {
      const lineEl = document.createElement("div");
      lineEl.className = "couplet-line";
      lineEl.dataset.lineIndex = lineIdx;

      // Pair wrapper for the two charans in this couplet
      const pairWrap = document.createElement("div");
      pairWrap.className = "charan-cards-pair";

      // Charan A (first half)
      const idxA = lineIdx * 2;
      const targetA = this.targets[idxA % this.targets.length] || 13;
      const cardA = this.createCharanCard(idxA, lineIdx + 1, 1, line.charans[0], targetA);
      pairWrap.appendChild(cardA);

      // Visual Caesura Divider
      const divider = document.createElement("div");
      divider.className = "charan-pair-divider";
      divider.innerHTML = '<span class="divider-bar">|</span>';
      divider.setAttribute("aria-hidden", "true");
      pairWrap.appendChild(divider);

      // Charan B (second half)
      const idxB = lineIdx * 2 + 1;
      const targetB = this.targets[idxB % this.targets.length] || 11;
      const cardB = this.createCharanCard(idxB, lineIdx + 1, 2, line.charans[1], targetB);
      pairWrap.appendChild(cardB);

      lineEl.appendChild(pairWrap);
      this.container.appendChild(lineEl);
    });

    // If we have existing analysis, re-apply it to the new elements
    if (this.lastAnalysisResults) {
      this.updateAnalysis(this.lastAnalysisResults);
    }
  }

  createCharanCard(globalIndex, lineNum, halfNum, text, target) {
    const card = document.createElement("div");
    card.className = "charan-card";
    card.dataset.globalIndex = globalIndex;
    if (globalIndex === this.activeCharanGlobalIndex) {
      card.classList.add("active-charan");
    }

    // 1. Header: Section name, target, and status badge
    const header = document.createElement("div");
    header.className = "charan-card-header";

    const titleWrap = document.createElement("div");
    titleWrap.className = "charan-meta-info";

    const titleSpan = document.createElement("span");
    titleSpan.className = "charan-title";
    titleSpan.textContent = `Section ${globalIndex + 1} · चरण ${globalIndex + 1}`;
    titleWrap.appendChild(titleSpan);

    const targetBadge = document.createElement("span");
    targetBadge.className = "charan-target-indicator";
    targetBadge.textContent = `Target: ${target} matras`;
    titleWrap.appendChild(targetBadge);

    header.appendChild(titleWrap);

    // Initial status badge (default to not started if text is empty)
    const statusWrap = document.createElement("div");
    statusWrap.className = "charan-status-wrap";
    statusWrap.id = `charan-status-wrap-${globalIndex}`;
    const initialBadge = formatLineStatusBadge("not-started", 0, 0, target, !text.trim());
    statusWrap.appendChild(initialBadge);
    header.appendChild(statusWrap);

    card.appendChild(header);

    // 2. Input Box
    const inputWrap = document.createElement("div");
    inputWrap.className = "charan-input-container";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "charan-input";
    input.dataset.globalIndex = globalIndex;
    input.value = text;
    input.placeholder = "चरण प्रविष्ट करें...";
    input.setAttribute("aria-label", `Line ${lineNum}, Section ${halfNum}`);

    input.addEventListener("input", (e) => {
      const val = e.target.value;
      const l = Math.floor(globalIndex / 2);
      const c = globalIndex % 2;
      this.lines[l].charans[c] = val;
      this.triggerDebouncedAnalysis();
    });

    input.addEventListener("focus", () => {
      this.setActiveCharan(globalIndex);
    });

    inputWrap.appendChild(input);
    card.appendChild(inputWrap);

    // 3. Scansion Marks Row (Laghu • / Guru —)
    const marksRow = document.createElement("div");
    marksRow.className = "charan-marks-row";
    marksRow.id = `charan-marks-${globalIndex}`;
    card.appendChild(marksRow);

    // 4. Feedback bar: live count summary & drawer toggle button
    const feedbackBar = document.createElement("div");
    feedbackBar.className = "charan-feedback-bar";

    const countSummary = document.createElement("span");
    countSummary.className = "charan-count-summary";
    countSummary.id = `charan-count-summary-${globalIndex}`;
    countSummary.textContent = text.trim() ? "Analyzing..." : "Not started";
    feedbackBar.appendChild(countSummary);

    const toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.className = "btn-toggle-details";
    toggleBtn.id = `btn-toggle-details-${globalIndex}`;
    const isOpen = this.openDrawers.has(globalIndex);
    toggleBtn.innerHTML = isOpen ? "<span>✕ Hide Matra Details</span>" : "<span>👁 View Matra Details</span>";
    toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    toggleBtn.addEventListener("click", () => {
      this.toggleDetailDrawer(globalIndex);
    });
    feedbackBar.appendChild(toggleBtn);

    card.appendChild(feedbackBar);

    // 5. Collapsible Matra Details Drawer
    const drawer = document.createElement("div");
    drawer.className = "charan-details-drawer";
    drawer.id = `charan-details-drawer-${globalIndex}`;
    drawer.style.display = isOpen ? "block" : "none";
    card.appendChild(drawer);

    return card;
  }

  setActiveCharan(globalIndex) {
    this.activeCharanGlobalIndex = globalIndex;
    
    // Update active highlight classes
    this.container.querySelectorAll(".charan-card").forEach(c => {
      const idx = parseInt(c.dataset.globalIndex, 10);
      c.classList.toggle("active-charan", idx === globalIndex);
    });

    const flat = this.getFlatCharans();
    if (this.onActiveCharanChanged) {
      this.onActiveCharanChanged(globalIndex, flat[globalIndex] || "");
    }
  }

  toggleDetailDrawer(globalIndex) {
    const drawer = document.getElementById(`charan-details-drawer-${globalIndex}`);
    const btn = document.getElementById(`btn-toggle-details-${globalIndex}`);
    if (!drawer || !btn) return;

    if (this.openDrawers.has(globalIndex)) {
      this.openDrawers.delete(globalIndex);
      drawer.style.display = "none";
      btn.innerHTML = "<span>👁 View Matra Details</span>";
      btn.setAttribute("aria-expanded", "false");
    } else {
      this.openDrawers.add(globalIndex);
      drawer.style.display = "block";
      btn.innerHTML = "<span>✕ Hide Matra Details</span>";
      btn.setAttribute("aria-expanded", "true");
      
      // Render details if results exist
      if (this.lastAnalysisResults && this.lastAnalysisResults.lines[globalIndex]) {
        const res = this.lastAnalysisResults.lines[globalIndex];
        drawer.textContent = "";
        drawer.appendChild(renderDetailedScansionGrid(res.syllables, res.break_positions));
      }
    }
  }

  updateAnalysis(results) {
    if (!results || !results.lines) return;
    this.lastAnalysisResults = results;

    const flatCharans = this.getFlatCharans();
    let completedCount = 0;
    let notStartedCount = 0;
    let revisionCount = 0;
    const lineProgress = [];

    results.lines.forEach((res, idx) => {
      const text = (flatCharans[idx] || "").trim();
      const isEmpty = text.length === 0;

      // 1. Status Badge
      const statusWrap = document.getElementById(`charan-status-wrap-${idx}`);
      if (statusWrap) {
        statusWrap.textContent = "";
        const badge = formatLineStatusBadge(
          res.status,
          res.difference,
          res.actual_matras,
          res.target_matras,
          isEmpty
        );
        statusWrap.appendChild(badge);
      }

      // 2. Scansion Marks
      const marksContainer = document.getElementById(`charan-marks-${idx}`);
      if (marksContainer) {
        marksContainer.textContent = "";
        if (isEmpty) {
          const emptyMark = document.createElement("span");
          emptyMark.className = "mark-empty-placeholder";
          emptyMark.textContent = "—";
          marksContainer.appendChild(emptyMark);
        } else {
          marksContainer.appendChild(renderScansionMarks(res.syllables, res.break_positions));
        }
      }

      // 3. Overflow input border
      const input = this.container.querySelector(`[data-global-index="${idx}"]`);
      if (input) {
        input.classList.toggle("overflow-active", !isEmpty && res.status === "over");
      }

      // 4. Live count summary
      const countSummary = document.getElementById(`charan-count-summary-${idx}`);
      if (countSummary) {
        if (isEmpty) {
          countSummary.textContent = "Not started";
          countSummary.className = "charan-count-summary not-started";
        } else if (res.status === "matched") {
          countSummary.textContent = `${res.actual_matras} matras · In meter ✓`;
          countSummary.className = "charan-count-summary matched";
        } else if (res.status === "over") {
          countSummary.textContent = `${res.actual_matras} matras (${Math.abs(res.difference)} extra)`;
          countSummary.className = "charan-count-summary over";
        } else {
          countSummary.textContent = `${res.actual_matras} matras (${Math.abs(res.difference)} needed)`;
          countSummary.className = "charan-count-summary under";
        }
      }

      // 5. Drawer Grid (if open)
      const drawer = document.getElementById(`charan-details-drawer-${idx}`);
      if (drawer && this.openDrawers.has(idx)) {
        drawer.textContent = "";
        drawer.appendChild(renderDetailedScansionGrid(res.syllables, res.break_positions));
      }

      // Track progress
      if (isEmpty) {
        notStartedCount++;
        lineProgress.push({ index: idx, status: "not-started", label: `Section ${idx + 1}` });
      } else if (res.status === "matched") {
        completedCount++;
        lineProgress.push({ index: idx, status: "matched", label: `Section ${idx + 1}` });
      } else {
        revisionCount++;
        lineProgress.push({ index: idx, status: "revision", label: `Section ${idx + 1}` });
      }
    });

    // Notify progress update
    if (this.onProgressUpdated) {
      this.onProgressUpdated({
        total: results.lines.length,
        completed: completedCount,
        notStarted: notStartedCount,
        needsRevision: revisionCount,
        lineProgress,
      });
    }
  }
}
