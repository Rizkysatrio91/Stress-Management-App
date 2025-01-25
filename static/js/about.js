document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".slide-in");

  elements.forEach((el) => {
    el.style.opacity = 1;
    el.style.transform = "translateY(0)";
  });
});
