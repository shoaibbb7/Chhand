/**
 * AI Suggestions renderer and interaction handler.
 * Renders verified rewrite cards and rhyme pills safely using DOM APIs.
 */

export function renderSuggestions(
  suggestions,
  containerEl,
  onAccept,
  onSkip
) {
  containerEl.textContent = "";

  if (!suggestions || suggestions.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No verified rewrite candidates available. Click 'Fit This Meter' to generate.";
    containerEl.appendChild(empty);
    return;
  }

  suggestions.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "suggestion-item";

    // 1. Text of suggested Hindi line
    const textEl = document.createElement("div");
    textEl.className = "suggestion-text";
    textEl.textContent = item.suggested_line;
    card.appendChild(textEl);

    // 2. Meta: count, verification badge, and note
    const metaEl = document.createElement("div");
    metaEl.className = "suggestion-meta";

    const countSpan = document.createElement("span");
    countSpan.className = "suggestion-matras";
    countSpan.textContent = `${item.target_matra_count} | ${item.calculated_matra_count}`;
    metaEl.appendChild(countSpan);

    if (item.verified_status) {
      const verifiedBadge = document.createElement("span");
      verifiedBadge.className = "suggestion-verified-badge";
      verifiedBadge.textContent = "✓ Verified";
      metaEl.appendChild(verifiedBadge);
    }

    if (item.meaning_note) {
      const noteSpan = document.createElement("span");
      noteSpan.className = "suggestion-meaning-note";
      noteSpan.textContent = `· ${item.meaning_note}`;
      metaEl.appendChild(noteSpan);
    }
    card.appendChild(metaEl);

    // 3. Actions: Accept and Reject
    const actionsEl = document.createElement("div");
    actionsEl.className = "suggestion-actions";

    const acceptBtn = document.createElement("button");
    acceptBtn.type = "button";
    acceptBtn.className = "btn-accept";
    acceptBtn.textContent = "Accept";
    acceptBtn.setAttribute("aria-label", `Accept rewrite: ${item.suggested_line}`);
    acceptBtn.addEventListener("click", () => {
      onAccept(item.suggested_line);
      card.remove();
    });

    const rejectBtn = document.createElement("button");
    rejectBtn.type = "button";
    rejectBtn.className = "btn-skip btn-reject";
    rejectBtn.textContent = "Reject";
    rejectBtn.setAttribute("aria-label", `Reject rewrite: ${item.suggested_line}`);
    rejectBtn.addEventListener("click", () => {
      onSkip(index);
      card.remove();
    });

    actionsEl.appendChild(acceptBtn);
    actionsEl.appendChild(rejectBtn);
    card.appendChild(actionsEl);

    containerEl.appendChild(card);
  });
}

export function renderRhymePills(rhymes, containerEl, onSelectWord) {
  containerEl.textContent = "";

  if (!rhymes || rhymes.length === 0) {
    const empty = document.createElement("span");
    empty.className = "empty-state";
    empty.textContent = "No rhyming words found.";
    containerEl.appendChild(empty);
    return;
  }

  rhymes.forEach(word => {
    const pill = document.createElement("button");
    pill.type = "button";
    pill.className = "rhyme-pill";
    pill.textContent = word;
    pill.addEventListener("click", () => {
      if (onSelectWord) {
        onSelectWord(word);
      }
    });
    containerEl.appendChild(pill);
  });
}
