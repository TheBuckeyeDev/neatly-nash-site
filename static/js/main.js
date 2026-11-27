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
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !nav.classList.contains('is-open')) return;
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
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
    var submitBtn = form.querySelector('button[type="submit"]');

    function fieldError(field, message) {
      clearFieldError(field);
      var err = document.createElement('div');
      err.className = 'form-error';
      err.id = field.id + '-error';
      err.textContent = message;
      field.insertAdjacentElement('afterend', err);
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', err.id);
    }
    function clearFieldError(field) {
      var next = field.nextElementSibling;
      if (next && next.classList.contains('form-error')) next.remove();
      field.removeAttribute('aria-invalid');
      field.removeAttribute('aria-describedby');
    }
    function clearSubmitError() {
      var next = submitBtn.nextElementSibling;
      if (next && next.classList.contains('form-error')) next.remove();
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearSubmitError();

      var name = form.querySelector('#name');
      var email = form.querySelector('#email');
      var invalid = [];

      if (!name.value.trim()) {
        fieldError(name, 'Please enter your name.');
        invalid.push(name);
      } else {
        clearFieldError(name);
      }

      var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email.value.trim() || !emailPattern.test(email.value.trim())) {
        fieldError(email, 'Please enter a valid email.');
        invalid.push(email);
      } else {
        clearFieldError(email);
      }

      if (invalid.length) {
        invalid[0].focus();
        return;
      }

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
          if (successEl) {
            successEl.classList.add('is-visible');
            var heading = successEl.querySelector('h3');
            heading.setAttribute('tabindex', '-1');
            heading.focus();
          }
        })
        .catch(function () {
          submitBtn.disabled = false;
          var err = document.createElement('div');
          err.className = 'form-error';
          err.setAttribute('role', 'alert');
          err.textContent = 'Something went wrong sending this. Please text or call (615) 555-0148 instead.';
          submitBtn.insertAdjacentElement('afterend', err);
        });
    });
  }
})();
