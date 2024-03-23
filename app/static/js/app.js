(function () {
  let lostFocus = false;
  function checkDocumentFocus() {
    if (document.hasFocus()) {
      if (lostFocus) {
        lostFocus = false;
        htmx.trigger("#focus-loader", "focusTrigger", {});
      }
    } else {
      if (!lostFocus) {
        lostFocus = true;
      }
    }
  }
  setInterval(checkDocumentFocus, 300);
})();
