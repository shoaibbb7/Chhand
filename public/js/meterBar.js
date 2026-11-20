/**
 * Scansion renderer: Laghu (•) and Guru (—) marks, matra pills, and beginner-friendly status badges.
 */

export function renderScansionMarks(syllables, breakPositions) {
  const container = document.createElement("div");
  container.className = "scansion-marks-charan";

  if (!syllables || syllables.length === 0) {
    const emptySpan = document.createElement("span");
    emptySpan.style.color = "var(--color-ink-soft)";
    emptySpan.textContent = "—";
    container.appendChild(emptySpan);
    return container;
  }

  const breakSet = new Set(breakPositions || []);

  syllables.forEach((s, idx) => {
    const unit = document.createElement("span");
    const isOver = breakSet.has(idx);
    unit.className = `mark-unit ${s.classification} ${isOver ? "overflow" : ""}`;
    unit.textContent = s.classification === "guru" ? "—" : "•";
    unit.title = `${s.text}: ${s.classification === "guru" ? "Guru (2 matras)" : "Laghu (1 matra)"} · ${s.reason}`;
    container.appendChild(unit);
  });

  return container;
}

export function formatLineStatusBadge(status, difference, actual, target, isEmpty = false) {
  const badge = document.createElement("span");

  if (isEmpty || (actual === 0 && (!status || status === "under" || status === "not-started"))) {
    badge.className = "meter-badge not-started";
    badge.textContent = "Not started";
    return badge;
  }

  badge.className = `meter-badge ${status}`;

  if (status === "matched") {
    badge.textContent = `✓ In meter (${actual}/${target})`;
  } else if (status === "over") {
    const extra = Math.abs(difference);
    badge.textContent = `✗ ${extra} extra matra${extra > 1 ? "s" : ""} (${actual}/${target})`;
  } else if (status === "under") {
    const missing = Math.abs(difference);
    badge.textContent = `${missing} matra${missing > 1 ? "s" : ""} needed (${actual}/${target})`;
  } else if (status === "ambiguous") {
    badge.textContent = "⚠ Needs review";
  } else if (status === "invalid") {
    badge.textContent = "✗ Invalid characters";
  } else {
    badge.className = "meter-badge not-started";
    badge.textContent = "Not started";
  }

  return badge;
}

export function renderDetailedScansionGrid(syllables, breakPositions) {
  const container = document.createElement("div");
  container.className = "detailed-scansion-grid";

  if (!syllables || syllables.length === 0) {
    container.innerHTML = '<span class="empty-detail-note">Type in this section to view akshara-by-akshara matra breakdown.</span>';
    return container;
  }

  const breakSet = new Set(breakPositions || []);

  syllables.forEach((s, idx) => {
    const cell = document.createElement("div");
    const isOver = breakSet.has(idx);
    cell.className = `akshara-detail-cell ${s.classification} ${isOver ? "overflow" : ""}`;

    const textEl = document.createElement("div");
    textEl.className = "cell-akshara-text";
    textEl.textContent = s.text;
    cell.appendChild(textEl);

    const markEl = document.createElement("div");
    markEl.className = "cell-mark";
    markEl.textContent = s.classification === "guru" ? "— (guru)" : "• (laghu)";
    cell.appendChild(markEl);

    const weightEl = document.createElement("div");
    weightEl.className = "cell-weight";
    weightEl.textContent = `+${s.weight} matra`;
    cell.appendChild(weightEl);

    if (s.cumulative !== undefined && s.cumulative !== null) {
      const cumEl = document.createElement("div");
      cumEl.className = "cell-cumulative";
      cumEl.textContent = `Sum: ${s.cumulative}`;
      cell.appendChild(cumEl);
    }

    container.appendChild(cell);
  });

  return container;
}
