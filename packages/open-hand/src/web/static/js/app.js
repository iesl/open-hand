/* Bundled App.js */


function initCollapsibles() {
  console.log("Initializing Collapsibles");
  var btns = document.getElementsByClassName("collapse");

  for (let i = 0; i < btns.length; i++) {
    let btn = btns[i];

    btn.addEventListener("click", function () {
      var content = this.nextElementSibling;
      content.classList.toggle("collapsed")
    });
  }

}

window.addEventListener("load", () => {
  initCollapsibles();
});
