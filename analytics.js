(function () {
  function track(eventName, title) {
    if (!eventName || typeof window.goatcounter === 'undefined' || typeof window.goatcounter.count !== 'function') return;
    window.goatcounter.count({ path: eventName, title: title || eventName, event: true });
  }

  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-analytics-event]');
    if (!target) return;
    track(target.getAttribute('data-analytics-event'), target.getAttribute('data-analytics-title'));
  });
}());
