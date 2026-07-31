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

// --- Date-targeted history reader (scroll-up collection) ---

function waDateKeyOf(sepText, now) {
  var t = (sepText || "").trim();
  var parts = t.split("/");
  if (parts.length === 3) {
    return (+parts[0]) + "/" + (+parts[1]) + "/" + (+parts[2]);
  }
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  var low = t.toLowerCase();
  if (low === "today") return today.getDate() + "/" + (today.getMonth() + 1) + "/" + today.getFullYear();
  if (low === "yesterday") {
    var y = new Date(today.getTime() - 86400000);
    return y.getDate() + "/" + (y.getMonth() + 1) + "/" + y.getFullYear();
  }
  var days = { sunday: 0, monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5, saturday: 6 };
  if (days[low] !== undefined) {
    var d = new Date(today.getTime() - 86400000 * 7);
    var diff = (d.getDay() - days[low] + 7) % 7;
    d = new Date(d.getTime() + diff * 86400000);
    return d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear();
  }
  return null;
}

window.stepStartHistoryRead = function (targetDate) {
  try {
    var container = document.querySelector('[data-testid="conversation-panel-messages"]')
      || document.querySelector('div[aria-label="Chat history"]')
      || document.querySelector('#main div[role="application"]');
    if (!container) return JSON.stringify({ error: "No message container" });
    var max = Math.max(0, container.scrollHeight - container.clientHeight);
    container.scrollTop = max;
    window.__msgStore = {};
    window.__seps = {};
    window.__targetDate = targetDate || "";
    window.__now = new Date();
    return JSON.stringify({ sh: container.scrollHeight, ch: container.clientHeight, st: container.scrollTop, max: max });
  } catch (e) { return JSON.stringify({ error: e.message }); }
};

window.stepScrollToBottom = function () {
  try {
    var container = document.querySelector('[data-testid="conversation-panel-messages"]')
      || document.querySelector('div[aria-label="Chat history"]')
      || document.querySelector('#main div[role="application"]');
    if (!container) return JSON.stringify({ error: "No message container" });
    var max = Math.max(0, container.scrollHeight - container.clientHeight);
    container.scrollTop = max;
    return JSON.stringify({ st: container.scrollTop, atBottom: container.scrollTop >= max - 5 });
  } catch (e) { return JSON.stringify({ error: e.message }); }
};


window.stepCollectVisible = function () {
  try {
    var container = document.querySelector('[data-testid="conversation-panel-messages"]')
      || document.querySelector('div[aria-label="Chat history"]')
      || document.querySelector('#main div[role="application"]');
    if (!container) return JSON.stringify({ error: "No message container" });
    window.__batch = window.__batch === undefined ? 0 : window.__batch - 1;
    var batch = window.__batch;

    var sepRe = /^(today|yesterday|(mon|tue|wed|thu|fri|sat|sun)day|\d{1,2}\/\d{1,2}\/\d{4})$/i;
    var seps = container.querySelectorAll("div, span");
    for (var s = 0; s < seps.length; s++) {
      var st = (seps[s].textContent || "").trim();
      if (st.length < 20 && sepRe.test(st)) {
        var rect = seps[s].getBoundingClientRect();
        var key = Math.round(rect.top) + "|" + st;
        if (!window.__seps[key]) window.__seps[key] = { top: rect.top, text: st, key: waDateKeyOf(st, window.__now) };
      }
    }

    var rows = container.querySelectorAll('[data-testid^="conv-msg-"]');
    var added = 0;
    var crossedBefore = false;
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var id = row.getAttribute("data-id") || row.getAttribute("data-testid");
      if (!id || window.__msgStore[id]) continue;

      var preEl = row.querySelector("[data-pre-plain-text]");
      var pre = preEl ? preEl.getAttribute("data-pre-plain-text") : "";
      var m = pre.match(/\[(\d{1,2}):(\d{1,2}),\s*(\d{1,2})\/(\d{1,2})\/(\d{4})\]/);
      var dateKey = null;
      var sender = "";
      var h = 0, min = 0;
      if (m) {
        h = +m[1]; min = +m[2];
        dateKey = (+m[3]) + "/" + (+m[4]) + "/" + (+m[5]);
        var rest = pre.substring(pre.indexOf("]") + 1).trim();
        var colon = rest.indexOf(":");
        sender = colon !== -1 ? rest.substring(0, colon).trim() : rest.trim();
      } else {
        var rrect = row.getBoundingClientRect();
        var best = null;
        for (var k in window.__seps) {
          var se = window.__seps[k];
          if (se.top <= rrect.top + 1 && se.key && (!best || se.top > best.top)) best = se;
        }
        if (best) dateKey = best.key;
      }

      var rowIndex = i;
      var isTailOut = row.querySelector('[data-testid="tail-out"]');
      var isTailIn = row.querySelector('[data-testid="tail-in"]');
      var myNames = /^(baneeishaque|\+91 81369 47512)$/i;
      var direction = isTailOut ? "out" : isTailIn ? "in" : (myNames.test(sender) ? "out" : "in");
      var bodyEl = row.querySelector("span.selectable-text") || row.querySelector("span.copyable-text");
      var body = bodyEl ? bodyEl.textContent.trim() : "";
      if (!body) {
        var lbl = row.querySelector("[aria-label]");
        if (lbl) {
          body = lbl.getAttribute("aria-label")
            .replace(/^\+?[\d ]+:\s*/, "")
            .replace(/\s+\d{1,2}:\d{2}\s*(Read|Delivered|Pending).*$/i, "").trim();
        }
      }
      var timeStr = m ? ("00" + h).slice(-2) + ":" + ("00" + min).slice(-2) : "";
      if (!timeStr) {
        var metaEl = row.querySelector("[data-testid=msg-meta]");
        if (metaEl) {
          var mt = (metaEl.textContent || "").match(/\d{1,2}:\d{2}/);
          if (mt) timeStr = mt[0];
        }
      }

      window.__msgStore[id] = { order: batch * 1000000 + rowIndex, dateKey: dateKey, time: timeStr, sender: sender, direction: direction, text: body };
      added++;

      if (dateKey && window.__targetDate) {
        var p = window.__targetDate.split("/");
        var td = +p[0], tmo = +p[1], ty = +p[2];
        var q = dateKey.split("/");
        var qd = +q[0], qmo = +q[1], qy = +q[2];
        if (qy < ty || (qy === ty && (qmo < tmo || (qmo === tmo && qd < td)))) crossedBefore = true;
      }
    }
    var keyCount = 0;
    for (var kk in window.__msgStore) keyCount++;
    return JSON.stringify({ added: added, total: keyCount, crossedBefore: crossedBefore,
      st: container.scrollTop, sh: container.scrollHeight, ch: container.clientHeight });
  } catch (e) { return JSON.stringify({ error: e.message }); }
};


window.stepFinishHistoryRead = function (maxMessages) {
  try {
    var p = (window.__targetDate || "").split("/");
    var td = +p[0], tmo = +p[1], ty = +p[2];
    var out = [];
    var ids = Object.keys(window.__msgStore);
    for (var i = 0; i < ids.length; i++) {
      var msg = window.__msgStore[ids[i]];
      if (!msg.dateKey) continue;
      var q = msg.dateKey.split("/");
      if (+q[0] === td && +q[1] === tmo && +q[2] === ty) {
        out.push({ order: msg.order, time: msg.time, sender: msg.sender, direction: msg.direction, text: msg.text });
      }
    }
    out.sort(function (a, b) { return a.order - b.order; });
    if (out.length > maxMessages) out = out.slice(0, maxMessages);
    return JSON.stringify({ count: out.length, messages: out });
  } catch (e) { return JSON.stringify({ error: e.message, count: 0, messages: [] }); }
};

window.stepScrollUpBy = function (pixels) {
  try {
    var container = document.querySelector('[data-testid="conversation-panel-messages"]')
      || document.querySelector('div[aria-label="Chat history"]')
      || document.querySelector('#main div[role="application"]');
    if (!container) return JSON.stringify({ error: "No message container" });
    container.scrollTop = Math.max(0, container.scrollTop - pixels);
    return JSON.stringify({ st: container.scrollTop, atTop: container.scrollTop <= 0 });
  } catch (e) { return JSON.stringify({ error: e.message }); }
};
