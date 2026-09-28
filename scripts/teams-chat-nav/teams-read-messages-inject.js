// teams-read-messages-inject.js — Browser JS: extract messages from Teams chat
(function () {
  var items = document.querySelectorAll('.fui-unstable-ChatItem');
  var result = [];
  var dayLabel = '';

  items.forEach(function (item) {
    var txt = item.textContent.trim();

    // Date separators
    if (/^\d{1,2}\s+(July|August|June|May|April|March)/.test(txt)) return;
    if (txt === 'Today' || txt === 'Yesterday') { dayLabel = txt; return; }
    if (/^\d{2}-\d{2}$/.test(txt)) return;

    // Body container
    var bodyEl = item.querySelector('.fui-ChatMessage__body');
    if (!bodyEl) return;

    // Sender: first fz5stix (fz5s variant)
    var senderEl = item.querySelector('.fz5stix, .fz5s');
    var sender = senderEl ? senderEl.textContent.trim() : null;
    if (!sender) {
      var match = txt.match(/by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)/);
      if (match) sender = match[1];
    }

    // Timestamp: find span/time with HH:MM
    var timeText = '';
    var timeEls = bodyEl.querySelectorAll('span, time');
    for (var i = 0; i < timeEls.length; i++) {
      var t = timeEls[i].textContent.trim();
      if (/^\d{2}:\d{2}$/.test(t)) { timeText = t; break; }
    }
    if (!timeText && dayLabel === 'Yesterday') timeText = dayLabel;

    // Action label: Updated, etc.
    var actionLabel = '';
    var actionEl = item.querySelector('.fui-ChatMessage__details');
    if (actionEl) actionLabel = actionEl.textContent.trim();

    // Body text up to card boundary
    var bodyText = '';
    var childNodes = bodyEl.childNodes;
    for (var i = 0; i < childNodes.length; i++) {
      var node = childNodes[i];
      if (node.nodeType === 3) {
        bodyText += node.textContent;
      } else if (node.nodeType === 1) {
        var cls = node.className || '';
        if (cls.includes('ac-') || cls.includes('adaptive')) break;
        if (node.tagName === 'SPAN' || node.tagName === 'A' || node.tagName === 'P' || cls.includes('StyledText')) {
          bodyText += node.textContent;
        } else {
          break;
        }
      }
    }
    bodyText = bodyText.trim();

    // Mentions
    var bodyWithMentions = bodyText;
    var mentionEls = item.querySelectorAll('[class*="mention" i]');
    if (mentionEls.length > 0) {
      mentionEls.forEach(function (m) {
        var name = m.textContent.trim();
        if (name) bodyWithMentions = bodyWithMentions.replace(name, '@' + name);
      });
    }

    // Jira card
    var jira = null;
    var card = bodyEl.querySelector('.ac-container.ac-adaptiveCard');
    if (!card) card = bodyEl.querySelector('.ac-container');
    if (card) {
      var blocks = card.querySelectorAll('.ac-textBlock');
      var jiraNumber = '', jiraTitle = '', jiraAssignee = '', jiraStatus = '';
      blocks.forEach(function (b) {
        var bt = b.textContent.trim();
        if (/^[A-Z]+-\d+$/.test(bt) && bt.length < 15) jiraNumber = bt;
        else if (bt.startsWith('Assigned to')) jiraAssignee = bt;
        else if (/^(High|Medium|Low)$/.test(bt) || /^(IN PROGRESS|DEV COMPLETE|IN REVIEW|TO DO|DONE)$/.test(bt)) {
          jiraStatus = jiraStatus ? jiraStatus + ' · ' + bt : bt;
        } else if (bt && bt.length > 10 && !/Jira|Notify|Comment|Edit/.test(bt) && bt !== jiraNumber) {
          jiraTitle = bt;
        }
      });
      if (jiraNumber) {
        jira = { number: jiraNumber, title: jiraTitle, assignee: jiraAssignee, status: jiraStatus };
      }
    }

    result.push({
      day: dayLabel,
      sender: sender,
      time: timeText,
      action: actionLabel,
      body: bodyWithMentions,
      jira: jira
    });
  });

  return JSON.stringify(result, null, 2);
})();