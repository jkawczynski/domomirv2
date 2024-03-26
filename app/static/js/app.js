const initTinymce = () => {
  tinymce.remove("textarea");
  tinymce.init({
    selector: "textarea",
    menubar: false,
    statusbar: false,
    skin: "oxide-dark",
    content_css: "dark",
    setup: (editor) => editor.on("change", editor.save),
  });
};

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

  htmx.on("htmx:afterSettle", () => {
    if (document.getElementsByTagName("textarea").length) {
      setTimeout(initTinymce());
    }
  });
  htmx.on("htmx:load", () => {
    if (document.getElementsByTagName("textarea").length) {
      initTinymce();
    }
  });
})();
