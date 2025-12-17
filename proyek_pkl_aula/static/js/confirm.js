// static/js/confirm.js
// Global confirm modal handler (dipanggil dari base.html)
// Pastikan ada modal dengan id="appConfirmModal" di base.html

(function () {
  const modalEl = document.getElementById('appConfirmModal');
  if (!modalEl) return;

  const bsModal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: false });
  const msgEl = document.getElementById('appConfirmMessage');
  const okBtn = document.getElementById('appConfirmOk');
  const cancelBtn = document.getElementById('appConfirmCancel');

  let pendingForm = null;
  let pendingSubmitter = null;

  function resetActiveButtons(form) {
    try {
      const active = document.activeElement;
      if (active && form && form.contains(active)) active.blur();
    } catch (e) { /* ignore */ }

    // bersihkan state visual tombol
    try {
      form.querySelectorAll('button, input[type="submit"], a').forEach(el => {
        el.classList.remove('active');
        el.style.boxShadow = '';
        el.style.backgroundColor = '';
      });
    } catch (e) { /* ignore */ }
  }

  function attachConfirmHandlers() {
    document.querySelectorAll('form.needs-confirm').forEach(form => {
      if (form.dataset.confirmBound === '1') return;
      form.dataset.confirmBound = '1';

      form.addEventListener('submit', function (ev) {
        // jika sudah di-skip (OK ditekan), biarkan submit normal
        if (form.dataset.confirmSkip === '1') return;

        ev.preventDefault();
        pendingForm = form;
        const submitter = ev.submitter || null;
        pendingSubmitter = submitter;

        let message = form.dataset.confirmMessage || 'Yakin ingin melanjutkan aksi ini?';
        if (submitter && submitter.dataset && submitter.dataset.confirmMessage) {
          message = submitter.dataset.confirmMessage;
        }

        if (msgEl) msgEl.textContent = message;

        const okText = form.dataset.confirmOkText || (submitter && submitter.dataset.confirmOkText) || 'Ya, Lanjutkan';
        const okClass = form.dataset.confirmOkClass || (submitter && submitter.dataset.confirmOkClass) || 'btn-danger';

        okBtn.className = 'btn ' + okClass;
        okBtn.textContent = okText;

        bsModal.show();
      });
    });
  }

  okBtn.addEventListener('click', function () {
    if (!pendingForm) {
      bsModal.hide();
      return;
    }

    pendingForm.dataset.confirmSkip = '1';
    resetActiveButtons(pendingForm);
    bsModal.hide();

    setTimeout(() => {
      try {
        pendingForm.submit();
      } catch (e) {
        console.error('Gagal submit form via JS:', e);
      } finally {
        delete pendingForm.dataset.confirmSkip;
        pendingForm = null;
        pendingSubmitter = null;
      }
    }, 200);
  });

  cancelBtn.addEventListener('click', function () {
    if (pendingForm) {
      resetActiveButtons(pendingForm);
      pendingForm = null;
      pendingSubmitter = null;
    }
    bsModal.hide();
  });

  modalEl.addEventListener('hidden.bs.modal', function () {
    if (pendingForm) {
      resetActiveButtons(pendingForm);
      pendingForm = null;
      pendingSubmitter = null;
    }
  });

  attachConfirmHandlers();

  // MutationObserver supaya form yang ditambahkan dinamis juga kebind
  const mo = new MutationObserver(() => attachConfirmHandlers());
  mo.observe(document.body, { childList: true, subtree: true });

})();
