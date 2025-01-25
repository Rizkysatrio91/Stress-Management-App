// Menghapus pesan flash setelah beberapa detik
setTimeout(() => {
  const flashMessage = document.getElementById("flash-message");
  if (flashMessage) {
    flashMessage.classList.remove("show");
    flashMessage.classList.add("hide");
  }
}, 5000);
