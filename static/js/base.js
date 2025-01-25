document.addEventListener("DOMContentLoaded", function () {
  const burgerMenu = document.getElementById("burgerMenu");
  const sidebarMenu = document.getElementById("sidebarMenu");

  burgerMenu.addEventListener("click", function () {
    sidebarMenu.classList.toggle("show");
    burgerMenu.classList.toggle("cross");
  });
});
