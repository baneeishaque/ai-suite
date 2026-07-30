// teams-chat-nav-inject.js — Browser JS injected into Teams web page
(function () {
  var chatName = CHAT_NAME_PLACEHOLDER;
  var items = document.querySelectorAll('[role="treeitem"]');
  var found = null;
  items.forEach(function (el) {
    if (el.textContent.includes(chatName)) {
      found = el;
    }
  });
  if (found) {
    found.click();
    return "Clicked: " + chatName;
  }
  return "Chat not found: " + chatName;
})();
