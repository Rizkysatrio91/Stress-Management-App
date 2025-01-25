document.addEventListener("DOMContentLoaded", function () {
  const image = document.querySelector(".img-fluid");
  image.addEventListener("mouseenter", function () {
    image.style.filter = "brightness(1.2)";
  });
  image.addEventListener("mouseleave", function () {
    image.style.filter = "brightness(1)";
  });

  const listItems = document.querySelectorAll(".highlight-list li");
  listItems.forEach((item) => {
    item.addEventListener("click", function () {
      item.style.color = "#27ae60";
      item.style.fontWeight = "bold";
    });
  });
});
