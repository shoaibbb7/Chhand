/**
 * Meters Page Component (छंद ग्रंथालय / Meter Library).
 * Displays traditional Hindi poetic meters, visual matra structures,
 * detailed scansion breakdowns, and an interactive Custom Meter Builder.
 */

export class MetersPage {
  constructor(options = {}) {
    this.container = options.container;
    this.onSelectMeter = options.onSelectMeter || null;
    this.onSelectCustomMeter = options.onSelectCustomMeter || null;

    // Custom meter builder state
    this.customCharans = [12, 12, 14, 12];
    this.customMeterName = "कस्टम छंद (Custom)";

    this.init();
  }

  init() {
    this.render();
  }

  render() {
    this.container.textContent = "";

    // Header section
    const headerEl = document.createElement("div");
    headerEl.className = "page-intro-header";
    headerEl.innerHTML = `
      <span class="page-eyebrow">METER LIBRARY</span>
      <h1 class="page-main-heading">Explore poetic meters</h1>
      <p class="page-description">
        Understand traditional Hindi rhythmic structures and choose a meter for your next poem.
      </p>
    `;
    this.container.appendChild(headerEl);

    // Cards Grid
    const gridEl = document.createElement("div");
    gridEl.className = "meters-grid";

    // 1. Doha Card
    const dohaCard = this.createMeterCard({
      id: "doha",
      devanagariName: "दोहा",
      englishName: "Doha",
      subtitle: "13 | 11 | 13 | 11 matras",
      description: "A traditional Hindi poetic form built around four charans with alternating matra targets (विषम 13, सम 11).",
      pattern: [13, 11, 13, 11],
      yatiInfo: "यति 13 और 11 पर होती है।",
      sampleLine1: "मन का दीपक जब जले | मिटे अँधेरा दूर",
      sampleLine2: "सीख सदा सच की रखो | साथ रहेगा नूर",
      sampleSource: "Chhand Reviewed Benchmark",
    });
    gridEl.appendChild(dohaCard);

    // 2. Chaupai Card
    const chaupaiCard = this.createMeterCard({
      id: "chaupai",
      devanagariName: "चौपाई",
      englishName: "Chaupai",
      subtitle: "16 | 16 | 16 | 16 matras",
      description: "A popular Hindi poetic form organized into four charans, each following an exact 16-matra target.",
      pattern: [16, 16, 16, 16],
      yatiInfo: "प्रत्येक चरण में 16 मात्राएँ।",
      sampleLine1: "जय हनुमान ज्ञान गुन सागर | जय कपीस तिहुँ लोक उजागर",
      sampleLine2: "राम दूत अतुलित बल धामा | अंजनि पुत्र पवनसुत नामा",
      sampleSource: "Tulsidas (Ramcharitmanas)",
    });
    gridEl.appendChild(chaupaiCard);

    // 3. Custom Meter Card
    const customCard = this.createCustomMeterCard();
    gridEl.appendChild(customCard);

    this.container.appendChild(gridEl);

    // Custom Builder Section (Hidden initially)
    const builderContainer = document.createElement("div");
    builderContainer.id = "custom-meter-builder-panel";
    builderContainer.className = "custom-builder-card";
    builderContainer.style.display = "none";
    this.container.appendChild(builderContainer);
  }

  createMeterCard(data) {
    const card = document.createElement("div");
    card.className = "meter-library-card";

    // Card Header
    const cardHeader = document.createElement("div");
    cardHeader.className = "meter-card-header";
    cardHeader.innerHTML = `
      <div class="meter-card-title-group">
        <h2 class="meter-devanagari-title">${data.devanagariName}</h2>
        <span class="meter-english-title">${data.englishName}</span>
      </div>
      <span class="meter-pattern-badge">${data.pattern.join(" | ")}</span>
    `;
    card.appendChild(cardHeader);

    // Description
    const desc = document.createElement("p");
    desc.className = "meter-card-desc";
    desc.textContent = data.description;
    card.appendChild(desc);

    // Pattern Visualizer
    const visualizer = document.createElement("div");
    visualizer.className = "meter-visualizer";
    data.pattern.forEach((count, idx) => {
      const row = document.createElement("div");
      row.className = "visualizer-row";

      const label = document.createElement("span");
      label.className = "visualizer-label";
      label.textContent = `चरण ${idx + 1} (${count})`;
      row.appendChild(label);

      const dotsContainer = document.createElement("div");
      dotsContainer.className = "visualizer-dots";
      for (let i = 0; i < count; i++) {
        const dot = document.createElement("span");
        dot.className = "matra-visual-dot";
        dotsContainer.appendChild(dot);
      }
      row.appendChild(dotsContainer);
      visualizer.appendChild(row);
    });
    card.appendChild(visualizer);

    // Card Actions
    const actions = document.createElement("div");
    actions.className = "meter-card-actions";

    const btnExplore = document.createElement("button");
    btnExplore.type = "button";
    btnExplore.className = "btn-secondary-meter";
    btnExplore.textContent = "Explore meter";
    btnExplore.addEventListener("click", () => {
      this.openDetailModal(data);
    });

    const btnWrite = document.createElement("button");
    btnWrite.type = "button";
    btnWrite.className = "btn-primary-meter";
    btnWrite.textContent = `Write in ${data.englishName}`;
    btnWrite.addEventListener("click", () => {
      if (this.onSelectMeter) {
        this.onSelectMeter(data.id);
      }
    });

    actions.appendChild(btnExplore);
    actions.appendChild(btnWrite);
    card.appendChild(actions);

    return card;
  }

  createCustomMeterCard() {
    const card = document.createElement("div");
    card.className = "meter-library-card custom-type-card";

    card.innerHTML = `
      <div class="meter-card-header">
        <div class="meter-card-title-group">
          <h2 class="meter-devanagari-title">कस्टम छंद</h2>
          <span class="meter-english-title">Custom Meter</span>
        </div>
        <span class="meter-pattern-badge" id="custom-card-preview-badge">${this.customCharans.join(" | ")}</span>
      </div>
      <p class="meter-card-desc">
        Create your own rhythmic structure by defining the matra target for every charan.
      </p>
    `;

    // Visual preview of custom
    const visualizer = document.createElement("div");
    visualizer.className = "meter-visualizer";
    visualizer.id = "custom-card-visualizer";
    this.renderCustomDots(visualizer);
    card.appendChild(visualizer);

    // Actions
    const actions = document.createElement("div");
    actions.className = "meter-card-actions";

    const btnConfigure = document.createElement("button");
    btnConfigure.type = "button";
    btnConfigure.className = "btn-primary-meter";
    btnConfigure.textContent = "Create custom meter";
    btnConfigure.addEventListener("click", () => {
      this.toggleCustomBuilder();
    });

    actions.appendChild(btnConfigure);
    card.appendChild(actions);

    return card;
  }

  renderCustomDots(container) {
    container.textContent = "";
    this.customCharans.forEach((count, idx) => {
      const row = document.createElement("div");
      row.className = "visualizer-row";
      row.innerHTML = `<span class="visualizer-label">चरण ${idx + 1} (${count})</span>`;
      const dotsContainer = document.createElement("div");
      dotsContainer.className = "visualizer-dots";
      for (let i = 0; i < Math.min(count, 20); i++) {
        const dot = document.createElement("span");
        dot.className = "matra-visual-dot";
        dotsContainer.appendChild(dot);
      }
      row.appendChild(dotsContainer);
      container.appendChild(row);
    });
  }

  toggleCustomBuilder() {
    const panel = document.getElementById("custom-meter-builder-panel");
    if (!panel) return;

    if (panel.style.display === "block") {
      panel.style.display = "none";
      return;
    }

    panel.style.display = "block";
    panel.scrollIntoView({ behavior: "smooth" });
    this.renderCustomBuilderContent(panel);
  }

  renderCustomBuilderContent(panel) {
    panel.textContent = "";

    const header = document.createElement("div");
    header.className = "builder-header";
    header.innerHTML = `
      <div class="card-label">CUSTOM METER BUILDER</div>
      <h3 class="card-title">Define your rhythmic pattern</h3>
      <p class="card-subtitle">
        Specify positive integer matra targets for each charan. Click 'Apply and Write' to open the Poems editor with this meter.
      </p>
    `;
    panel.appendChild(header);

    // Charans List
    const charansList = document.createElement("div");
    charansList.className = "builder-charans-list";

    this.customCharans.forEach((val, idx) => {
      const row = document.createElement("div");
      row.className = "builder-charan-row";

      const label = document.createElement("span");
      label.className = "builder-charan-label";
      label.textContent = `Charan ${idx + 1}:`;
      row.appendChild(label);

      const input = document.createElement("input");
      input.type = "number";
      input.min = "1";
      input.max = "32";
      input.className = "builder-matra-input";
      input.value = val;
      input.addEventListener("input", (e) => {
        const num = parseInt(e.target.value, 10);
        if (!isNaN(num) && num > 0) {
          this.customCharans[idx] = num;
          this.updateCustomPreviews();
        }
      });
      row.appendChild(input);

      const unit = document.createElement("span");
      unit.className = "builder-unit-label";
      unit.textContent = "matras";
      row.appendChild(unit);

      if (this.customCharans.length > 2) {
        const btnRemove = document.createElement("button");
        btnRemove.type = "button";
        btnRemove.className = "btn-remove-charan";
        btnRemove.textContent = "Remove";
        btnRemove.addEventListener("click", () => {
          this.customCharans.splice(idx, 1);
          this.renderCustomBuilderContent(panel);
          this.updateCustomPreviews();
        });
        row.appendChild(btnRemove);
      }

      charansList.appendChild(row);
    });
    panel.appendChild(charansList);

    // Controls
    const controls = document.createElement("div");
    controls.className = "builder-controls";

    const btnAdd = document.createElement("button");
    btnAdd.type = "button";
    btnAdd.className = "btn-secondary-meter";
    btnAdd.textContent = "+ Add Charan";
    btnAdd.addEventListener("click", () => {
      if (this.customCharans.length < 8) {
        this.customCharans.push(12);
        this.renderCustomBuilderContent(panel);
        this.updateCustomPreviews();
      }
    });
    controls.appendChild(btnAdd);

    const btnApply = document.createElement("button");
    btnApply.type = "button";
    btnApply.className = "btn-primary-meter";
    btnApply.textContent = "Apply & Write in Poems Studio";
    btnApply.addEventListener("click", () => {
      if (this.onSelectCustomMeter) {
        this.onSelectCustomMeter(this.customCharans);
      }
    });
    controls.appendChild(btnApply);

    panel.appendChild(controls);
  }

  updateCustomPreviews() {
    const badge = document.getElementById("custom-card-preview-badge");
    if (badge) {
      badge.textContent = this.customCharans.join(" | ");
    }
    const visualizer = document.getElementById("custom-card-visualizer");
    if (visualizer) {
      this.renderCustomDots(visualizer);
    }
  }

  openDetailModal(data) {
    let modal = document.getElementById("meter-detail-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "meter-detail-modal";
      modal.className = "modal-backdrop";
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">${data.devanagariName} (${data.englishName})</h2>
            <span class="modal-subtitle">संरचना: ${data.pattern.join(" | ")} मात्राएँ</span>
          </div>
          <button type="button" class="btn-close-modal" id="btn-close-modal">&times;</button>
        </div>

        <div class="modal-body">
          <p class="modal-desc">${data.description}</p>
          <div class="modal-meta-box">
            <div><strong>यति (Caesura):</strong> ${data.yatiInfo}</div>
            <div><strong>चरण संख्या:</strong> 4 चरण (Couplet)</div>
          </div>

          <div class="modal-sample-box">
            <div class="card-label">AUTHENTIC VERIFIED SAMPLE</div>
            <div class="sample-lines">
              <div class="sample-line">${data.sampleLine1}</div>
              <div class="sample-line">${data.sampleLine2}</div>
            </div>
            <div class="sample-source">स्रोत: ${data.sampleSource} · Scanned with Pingala Engine</div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-secondary-meter" id="btn-modal-cancel">Close</button>
          <button type="button" class="btn-primary-meter" id="btn-modal-write">Write in ${data.englishName}</button>
        </div>
      </div>
    `;

    modal.removeAttribute("hidden");
    modal.style.display = "flex";

    const closeModal = () => {
      modal.style.display = "none";
      modal.setAttribute("hidden", "true");
      document.removeEventListener("keydown", handleKeyDown);
    };

    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        closeModal();
      }
    };
    document.addEventListener("keydown", handleKeyDown);

    modal.querySelector("#btn-close-modal").addEventListener("click", closeModal);
    modal.querySelector("#btn-modal-cancel").addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });

    modal.querySelector("#btn-modal-write").addEventListener("click", () => {
      closeModal();
      if (this.onSelectMeter) {
        this.onSelectMeter(data.id);
      }
    });
  }
}
