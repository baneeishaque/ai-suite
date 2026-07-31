// wa-chat-read-inject.js — window functions for sequential JXA execution

window.stepSearchBox = function () {
  var selectors = [
    'input[role="textbox"][data-tab="3"]',
    'input[aria-label="Search or start a new chat"]',
    'div[contenteditable="true"][data-tab="3"]',
    'div[data-testid="chat-list-search-container"] input'
  ];
  for (var i = 0; i < selectors.length; i++) {
    var el = document.querySelector(selectors[i]);
    if (el) {
      el.focus();
      var tag = el.tagName.toLowerCase();
      var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      if (tag === "input") { setter.call(el, ""); }
      else { el.textContent = ""; }
      el.dispatchEvent(new Event("input", { bubbles: true }));
      return "cleared";
    }
  }
  return "not_found";
};

window.stepTypeQuery = function (query) {
  var selectors = [
    'input[role="textbox"][data-tab="3"]',
    'input[aria-label="Search or start a new chat"]'
  ];
  for (var i = 0; i < selectors.length; i++) {
    var el = document.querySelector(selectors[i]);
    if (el) {
      var tag = el.tagName.toLowerCase();
      var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      if (tag === "input") { setter.call(el, query); }
      else { el.textContent = query; }
      el.dispatchEvent(new Event("input", { bubbles: true }));
      return "typed";
    }
  }
  return "not_found";
};

window.stepGetResults = function () {
  var sections = [];
  var currentSection = null;
  var itemIndex = 0;

  var rows = document.querySelectorAll('#pane-side [role="row"]');
  var sectionNames = { chats: 1, contacts: 1, "groups in common": 1, messages: 1 };

  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var titleEl = row.querySelector('[data-testid="cell-frame-title"]');
    var text = row.textContent.replace(/\s+/g, " ").trim();

    if (!titleEl) {
      var tLower = text.toLowerCase();
      if (sectionNames[tLower]) {
        currentSection = { name: text, items: [] };
        sections.push(currentSection);
      }
      continue;
    }

    if (!currentSection) continue;

    var secondaryEl = row.querySelector('[data-testid="cell-frame-secondary"]');
    var primaryEl = row.querySelector('[data-testid="cell-frame-primary-detail"]');
    var tertiaryEl = row.querySelector('[data-testid="cell-frame-tertiary"]');

    var labels = [];
    var labelEls = row.querySelectorAll('[data-testid^="label-pill-"]');
    for (var j = 0; j < labelEls.length; j++) {
      labels.push(labelEls[j].textContent.trim());
    }

    currentSection.items.push({
      idx: itemIndex,
      title: titleEl.textContent.trim(),
      secondary: secondaryEl ? secondaryEl.textContent.replace(/\s+/g, " ").trim() : "",
      primary: primaryEl ? primaryEl.textContent.trim() : "",
      tertiary: tertiaryEl ? tertiaryEl.textContent.replace(/\s+/g, " ").trim() : "",
      labels: labels
    });
    itemIndex++;
  }

  return JSON.stringify({ sections: sections, total: itemIndex });
};

window.stepOpenResultByKeyboard = function (resultIndex) {
  var input = document.querySelector('input[role="textbox"][data-tab="3"]')
           || document.querySelector('input[aria-label="Search or start a new chat"]');
  if (!input) return "no_search_box";
  input.focus();

  var sendKey = function (key, code, keyCode) {
    var opts = { key: key, code: code, keyCode: keyCode, which: keyCode, bubbles: true, cancelable: true };
    input.dispatchEvent(new KeyboardEvent("keydown", opts));
    input.dispatchEvent(new KeyboardEvent("keypress", opts));
    input.dispatchEvent(new KeyboardEvent("keyup", opts));
  };

  var presses = resultIndex + 1;
  for (var i = 0; i < presses; i++) {
    sendKey("ArrowDown", "ArrowDown", 40);
  }
  sendKey("Enter", "Enter", 13);
  return "sent_" + presses + "_downs_and_enter";
};

window.stepGetMessages = function (maxMessages) {
  try {
    var containerSelectors = [
      '[data-testid="conversation-panel-messages"]',
      'div[aria-label="Chat history"]',
      '#main div[role="application"]',
      '#main > div'
    ];
    var container = null;
    for (var i = 0; i < containerSelectors.length; i++) {
      container = document.querySelector(containerSelectors[i]);
      if (container) break;
    }
    if (!container) return JSON.stringify({ error: "No message container", count: 0, messages: [] });

    for (var s = 0; s < 3; s++) {
      container.scrollTop = 0;
    }

    var messages = [];
    var seen = {};

    var bodies = container.querySelectorAll('[data-testid="conversation-panel-message-body"]');
    for (var i = 0; i < bodies.length; i++) {
      var text = bodies[i].textContent.trim();
      if (text && !seen[text]) { seen[text] = true; messages.push(text); }
    }

    if (messages.length === 0) {
      var spans = container.querySelectorAll('span.selectable-text, span.copyable-text');
      for (var i = 0; i < spans.length; i++) {
        var text = spans[i].textContent.trim();
        if (text && !seen[text]) { seen[text] = true; messages.push(text); }
      }
    }

    messages.reverse();
    if (messages.length > maxMessages) messages = messages.slice(0, maxMessages);

    return JSON.stringify({ count: messages.length, messages: messages });
  } catch (e) {
    return JSON.stringify({ error: e.message, count: 0, messages: [] });
  }
};
