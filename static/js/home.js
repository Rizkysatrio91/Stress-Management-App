document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".profile-card");

  cards.forEach((card, index) => {
    card.style.animationDelay = `${0.3 + index * 0.2}s`;
  });
});
