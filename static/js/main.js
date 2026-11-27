(function () {
  'use strict';

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Booking form: client-side validation on name + email, AJAX submit to
  // Netlify Forms, inline success state (no navigation away).
  var form = document.querySelector('form[data-booking-form]');
  if (form) {
    var successEl = document.querySelector('.form-success');

    function fieldError(field, message) {
      clearFieldError(field);
      if (!message) return;
      var err = document.createElement('div');
      err.className = 'form-error';
      err.textContent = message;
      field.insertAdjacentElement('afterend', err);
    }
    function clearFieldError(field) {
      var next = field.nextElementSibling;
      if (next && next.classList.contains('form-error')) next.remove();
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var name = form.querySelector('#name');
      var email = form.querySelector('#email');
      var valid = true;

      if (!name.value.trim()) {
        fieldError(name, 'Please enter your name.');
        valid = false;
      } else {
        clearFieldError(name);
      }

      var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email.value.trim() || !emailPattern.test(email.value.trim())) {
        fieldError(email, 'Please enter a valid email.');
        valid = false;
      } else {
        clearFieldError(email);
      }

      if (!valid) return;

      var submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = true;

      var data = new FormData(form);
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(data).toString()
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Form submit failed: ' + res.status);
          form.classList.add('is-hidden');
          if (successEl) successEl.classList.add('is-visible');
        })
        .catch(function () {
          submitBtn.disabled = false;
          fieldError(email, 'Something went wrong sending this — please text or call instead.');
        });
    });
  }
})();
