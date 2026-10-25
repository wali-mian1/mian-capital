(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.08, rootMargin: '0px 0px -28px 0px' });
  function observeReveals() {
    document.querySelectorAll('.reveal:not([data-reveal-observed])').forEach((element) => {
      element.dataset.revealObserved = 'true';
      observer.observe(element);
    });
  }
  document.documentElement.classList.add('motion-ready');
  new MutationObserver(observeReveals).observe(document.documentElement, { childList: true, subtree: true });
  observeReveals();
})();
