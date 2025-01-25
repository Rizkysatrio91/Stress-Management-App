// Animasi untuk jarum meteran stres
document.addEventListener("DOMContentLoaded", () => {
  // Pilih elemen jarum berdasarkan kelas "needle"
  const needle = document.querySelector(".needle");

  // Cek apakah elemen jarum ditemukan di halaman
  if (needle) {
    // Tambahkan transisi animasi pada properti transform jarum
    // Animasi ini mengontrol kehalusan pergerakan jarum saat berubah posisi
    needle.style.transition = "transform 0.5s ease-out";
    // Durasi animasi adalah 0.5 detik dengan efek easing "ease-out" untuk gerakan lebih alami
  }
});
