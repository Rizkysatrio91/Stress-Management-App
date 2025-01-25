document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebarMenu");
  const toggleButton = document.getElementById("toggleSidebar");

  toggleButton.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
});
