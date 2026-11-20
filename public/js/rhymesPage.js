/**
 * Rhymes Page Component (तुकान्त स्टूडियो / Rhyme Discovery Studio).
 * Dedicated Hindi rhyme discovery workspace connecting to live /api/rhyme.
 */

import { fetchRhymeFamilies, findRhymes } from "./api.js";

export class RhymesPage {
  constructor(options = {}) {
    this.container = options.container;
    this.onUseInPoem = options.onUseInPoem || null;

    this.currentSearchWord = "";
    this.lastResult = null;
    this.families = [];

    this.init();
  }

  async init() {
    this.render();
    await this.loadFamilies();
  }

  render() {
    this.container.textContent = "";

    // 1. Header Section
    const headerEl = document.createElement("div");
    headerEl.className = "page-intro-header";
    headerEl.innerHTML = `
      <span class="page-eyebrow">RHYME STUDIO</span>
      <h1 class="page-main-heading">Find words that flow together</h1>
      <p class="page-description">
        Discover Hindi rhymes and explore matching endings for your next verse.
      </p>
    `;
    this.container.appendChild(headerEl);

    // 2. Main Search Card
    const searchCard = document.createElement("div");
    searchCard.className = "rhyme-search-main-card";
    searchCard.innerHTML = `
      <div class="card-label">SEARCH HINDI RHYMES</div>
      <form id="rhyme-page-search-form" class="rhyme-main-search-form" onsubmit="return false;">
        <div class="search-input-wrapper">
          <input
            type="text"
            id="rhyme-page-input"
            class="rhyme-page-input"
            placeholder="कोई शब्द लिखें... जैसे प्यार, बहार, इकरार"
            aria-label="Search Hindi rhymes"
            autocomplete="off"
          />
          <button type="button" id="btn-clear-rhyme-input" class="btn-clear-input" title="Clear input">&times;</button>
        </div>
        <div class="search-actions-row">
          <button type="submit" id="btn-submit-rhyme-search" class="btn-primary-meter">
            <span>Find Rhymes</span>
          </button>
        </div>
      </form>
    `;
    this.container.appendChild(searchCard);

    // 3. Search Results Container
    const resultsContainer = document.createElement("div");
    resultsContainer.id = "rhyme-results-display";
    resultsContainer.className = "rhyme-results-display";
    resultsContainer.style.display = "none";
    this.container.appendChild(resultsContainer);

    // 4. Rhyme Families Exploration Section
    const familiesSection = document.createElement("section");
    familiesSection.className = "rhyme-families-section";
    familiesSection.innerHTML = `
      <div class="section-title-wrap">
        <h2 class="section-heading">Explore rhyme families</h2>
        <p class="section-subtext">Click any ending family or word chip to inspect all matching rhymes.</p>
      </div>
      <div id="rhyme-families-grid" class="rhyme-families-grid">
        <div class="empty-state">Loading rhyme dictionary families...</div>
      </div>
    `;
    this.container.appendChild(familiesSection);

    // Bind Search Form Events
    const form = searchCard.querySelector("#rhyme-page-search-form");
    const input = searchCard.querySelector("#rhyme-page-input");
    const btnClear = searchCard.querySelector("#btn-clear-rhyme-input");

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = input.value.trim();
      if (val) {
        this.executeSearch(val);
      }
    });

    btnClear.addEventListener("click", () => {
      input.value = "";
      input.focus();
      resultsContainer.style.display = "none";
    });
  }

  async executeSearch(word) {
    const input = document.getElementById("rhyme-page-input");
    if (input) input.value = word;

    const resultsContainer = document.getElementById("rhyme-results-display");
    if (!resultsContainer) return;

    resultsContainer.style.display = "block";
    resultsContainer.innerHTML = `
      <div class="empty-state">
        <span class="loading-spinner"></span>
        <span style="margin-left: 0.5rem;">Finding rhymes for "${word}"...</span>
      </div>
    `;

    try {
      const data = await findRhymes(word, 24);
      this.currentSearchWord = word;
      this.lastResult = data;
      this.renderResults(data, resultsContainer);
    } catch (err) {
      resultsContainer.innerHTML = `
        <div class="empty-state" style="color: var(--color-vermilion);">
          ${err.message || "Failed to search rhymes. Please try another word."}
        </div>
      `;
    }
  }

  renderResults(data, container) {
    container.textContent = "";

    const exactList = data.exact_matches || [];
    const approxList = data.approximate_matches || [];
    const totalCount = exactList.length + approxList.length;

    // Search Summary Header
    const summaryCard = document.createElement("div");
    summaryCard.className = "rhyme-results-summary-card";
    summaryCard.innerHTML = `
      <div class="results-summary-left">
        <span class="results-count-pill">${totalCount} matches</span>
        <span class="results-target-word">तुकान्त शब्द: <strong>${data.original_word}</strong></span>
      </div>
      <div class="results-summary-right">
        <span class="results-tail-badge">तुक: <strong>-${data.rhyme_tail || "समान ध्वनि"}</strong></span>
      </div>
    `;
    container.appendChild(summaryCard);

    if (totalCount === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = `No rhyming words found in dictionary for "${data.original_word}". Try another word or ending.`;
      container.appendChild(empty);
      return;
    }

    // 1. Exact Matches Section
    if (exactList.length > 0) {
      const exactSection = document.createElement("div");
      exactSection.className = "rhyme-match-group";

      const heading = document.createElement("div");
      heading.className = "match-group-heading";
      heading.innerHTML = `
        <span class="badge-match-type exact">समान तुक · Exact Matches</span>
        <span class="match-group-count">(${exactList.length})</span>
      `;
      exactSection.appendChild(heading);

      const chipsGrid = document.createElement("div");
      chipsGrid.className = "rhyme-chips-grid";
      exactList.forEach(w => {
        chipsGrid.appendChild(this.createRhymeChip(w, "exact"));
      });
      exactSection.appendChild(chipsGrid);
      container.appendChild(exactSection);
    }

    // 2. Approximate Matches Section
    if (approxList.length > 0) {
      const approxSection = document.createElement("div");
      approxSection.className = "rhyme-match-group";

      const heading = document.createElement("div");
      heading.className = "match-group-heading";
      heading.innerHTML = `
        <span class="badge-match-type approx">सन्निकट तुक · Approximate Matches</span>
        <span class="match-group-count">(${approxList.length})</span>
      `;
      approxSection.appendChild(heading);

      const chipsGrid = document.createElement("div");
      chipsGrid.className = "rhyme-chips-grid";
      approxList.forEach(w => {
        chipsGrid.appendChild(this.createRhymeChip(w, "approx"));
      });
      approxSection.appendChild(chipsGrid);
      container.appendChild(approxSection);
    }
  }

  createRhymeChip(word, type) {
    const chip = document.createElement("div");
    chip.className = `rhyme-word-card ${type}`;

    const wordText = document.createElement("button");
    wordText.type = "button";
    wordText.className = "chip-word-title";
    wordText.textContent = word;
    wordText.title = `Click to find rhymes for "${word}"`;
    wordText.addEventListener("click", () => {
      this.executeSearch(word);
    });
    chip.appendChild(wordText);

    const actions = document.createElement("div");
    actions.className = "chip-actions";

    // Copy action
    const btnCopy = document.createElement("button");
    btnCopy.type = "button";
    btnCopy.className = "btn-chip-action";
    btnCopy.textContent = "Copy";
    btnCopy.addEventListener("click", (e) => {
      e.stopPropagation();
      navigator.clipboard.writeText(word).then(() => {
        btnCopy.textContent = "Copied!";
        btnCopy.classList.add("copied");
        setTimeout(() => {
          btnCopy.textContent = "Copy";
          btnCopy.classList.remove("copied");
        }, 1500);
      });
    });
    actions.appendChild(btnCopy);

    // Use in poem action
    const btnUse = document.createElement("button");
    btnUse.type = "button";
    btnUse.className = "btn-chip-action primary";
    btnUse.textContent = "Use in poem";
    btnUse.addEventListener("click", (e) => {
      e.stopPropagation();
      if (this.onUseInPoem) {
        this.onUseInPoem(word);
      }
    });
    actions.appendChild(btnUse);

    chip.appendChild(actions);
    return chip;
  }

  async loadFamilies() {
    const grid = document.getElementById("rhyme-families-grid");
    if (!grid) return;

    try {
      const data = await fetchRhymeFamilies();
      this.families = data.families || [];
      this.renderFamilies(this.families, grid);
    } catch {
      // Fallback starter families if network error
      this.families = [
        { ending: "-ूर", count: 8, sample: ["दूर", "नूर", "ज़रूर", "मशहूर"] },
        { ending: "-ार", count: 12, sample: ["प्यार", "इकरार", "करार", "बहार"] },
        { ending: "-ान", count: 10, sample: ["जान", "अरमान", "सम्मान", "जहान"] },
        { ending: "-ात", count: 8, sample: ["बात", "रात", "बरसात", "सौगात"] },
        { ending: "-ले", count: 7, sample: ["जले", "भले", "गले", "चले"] },
        { ending: "-न", count: 11, sample: ["मन", "तन", "धन", "गगन"] },
      ];
      this.renderFamilies(this.families, grid);
    }
  }

  renderFamilies(families, grid) {
    grid.textContent = "";

    families.forEach(fam => {
      const card = document.createElement("div");
      card.className = "rhyme-family-card";

      const header = document.createElement("div");
      header.className = "family-card-header";
      header.innerHTML = `
        <span class="family-ending-title">${fam.ending}</span>
        <span class="family-word-count">${fam.count} words</span>
      `;
      card.appendChild(header);

      const wordsWrap = document.createElement("div");
      wordsWrap.className = "family-sample-chips";
      (fam.sample || []).forEach(w => {
        const sampleBtn = document.createElement("button");
        sampleBtn.type = "button";
        sampleBtn.className = "family-sample-btn";
        sampleBtn.textContent = w;
        sampleBtn.addEventListener("click", () => {
          this.executeSearch(w);
          window.scrollTo({ top: 150, behavior: "smooth" });
        });
        wordsWrap.appendChild(sampleBtn);
      });
      card.appendChild(wordsWrap);

      const btnExplore = document.createElement("button");
      btnExplore.type = "button";
      btnExplore.className = "btn-explore-family";
      btnExplore.textContent = `Explore ${fam.ending} family →`;
      btnExplore.addEventListener("click", () => {
        const firstWord = fam.sample && fam.sample[0] ? fam.sample[0] : fam.ending.replace("-", "");
        this.executeSearch(firstWord);
        window.scrollTo({ top: 150, behavior: "smooth" });
      });
      card.appendChild(btnExplore);

      grid.appendChild(card);
    });
  }
}
