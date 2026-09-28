// swh-save-inject.js — Page-side logic for SWH "Save code now" submissions.
//
// Injected into https://archive.softwareheritage.org/save/ via swh-save.jxa
// (Chrome tab.execute). Runs with page cookies, so the Anubis PoW clearance
// and any SWH session apply to fetch calls.
//
// ORIGINS_PLACEHOLDER -> JSON array literal (e.g. ["https://github.com/..."])

(function () {
  var origins = ORIGINS_PLACEHOLDER;
  var API_ROOT = "https://archive.softwareheritage.org/api/1";

  function saveViaApi(origin) {
    var url =
      API_ROOT + "/origin/save/git/url/" + encodeURIComponent(origin) + "/";
    return fetch(url, {
      method: "POST",
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    }).then(function (resp) {
      return resp.json().then(function (body) {
        return {
          origin: origin,
          method: "api",
          http_status: resp.status,
          id: body.id || null,
          save_request_status: body.save_request_status || null,
          save_task_status: body.save_task_status || null,
          snapshot_swhid: body.snapshot_swhid || null,
          request_url: body.request_url || null,
          visit_date: body.visit_date || null,
          note: body.note || null,
        };
      });
    });
  }

  function saveViaForm(origin) {
    // Best-effort DOM fallback: selectors cover known Save-form variants.
    var typeSelect =
      document.querySelector("select#visit-type, select[name='visit_type']");
    var urlInput = document.querySelector(
      "input#origin-url, input[name='origin_url'], input[type='url']"
    );
    var submitBtn = document.querySelector(
      "form button[type='submit'], form input[type='submit']"
    );
    if (!typeSelect || !urlInput || !submitBtn) {
      return Promise.resolve({
        origin: origin,
        method: "form",
        error: "save-form-elements-not-found",
      });
    }
    typeSelect.value = "git";
    typeSelect.dispatchEvent(new Event("change", { bubbles: true }));
    urlInput.value = origin;
    urlInput.dispatchEvent(new Event("input", { bubbles: true }));
    urlInput.dispatchEvent(new Event("change", { bubbles: true }));
    submitBtn.click();
    return new Promise(function (resolve) {
      setTimeout(function () {
        fetch(
          API_ROOT + "/origin/save/?visit_type=git&origin_url=" +
            encodeURIComponent(origin),
          { headers: { Accept: "application/json" }, credentials: "same-origin" }
        )
          .then(function (resp) { return resp.json(); })
          .then(function (body) {
            var latest = Array.isArray(body) ? body[body.length - 1] : body;
            resolve({
              origin: origin,
              method: "form",
              id: (latest && latest.id) || null,
              save_request_status: (latest && latest.save_request_status) || null,
              save_task_status: (latest && latest.save_task_status) || null,
              snapshot_swhid: (latest && latest.snapshot_swhid) || null,
              request_url: (latest && latest.request_url) || null,
              note: (latest && latest.note) || null,
            });
          })
          .catch(function (e) {
            resolve({ origin: origin, method: "form", error: "post-submit-poll-failed: " + e.message });
          });
      }, 4000);
    });
  }

  return Promise.all(
    origins.map(function (origin) {
      return saveViaApi(origin).catch(function () {
        return saveViaForm(origin);
      });
    })
  )
    .then(function (results) {
      return JSON.stringify(results);
    })
    .catch(function (e) {
      return JSON.stringify([{ error: "inject-failed: " + e.message }]);
    });
})();
