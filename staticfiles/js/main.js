// SkyBook — Main JS

// Smooth scroll to top on page load
window.addEventListener("load", () => {
  document.body.style.opacity = "0";
  document.body.style.transition = "opacity 0.4s ease";
  requestAnimationFrame(() => {
    document.body.style.opacity = "1";
  });
});

// Auto-dismiss alerts after 5 seconds
document.querySelectorAll(".alert").forEach((alert) => {
  setTimeout(() => {
    alert.style.transition = "all 0.5s ease";
    alert.style.opacity = "0";
    alert.style.transform = "translateY(-10px)";
    setTimeout(() => alert.remove(), 500);
  }, 5000);
});

// Add animation class to offer cards on scroll
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }, i * 60);
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.05 },
);

document
  .querySelectorAll(".offer-card, .feature-card, .booking-card")
  .forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition =
      "opacity 0.4s ease, transform 0.4s ease, border-color 0.25s ease, background 0.25s ease";
    observer.observe(card);
  });
