// FerreMix Script
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Auto-submit filters and cart quantity updates on change
    const autoSubmitForms = document.querySelectorAll('form[data-auto-submit="true"]');
    autoSubmitForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                form.submit();
            });
        });
    });

    const cartToggle = document.querySelector('[data-cart-toggle]');
    const cartPanel = document.querySelector('[data-cart-panel]');
    const cartCountEl = document.querySelector('[data-cart-count]');
    const cartItemsEl = document.querySelector('[data-cart-items]');
    const cartSubtotalEl = document.querySelector('[data-cart-subtotal]');

    const renderCartPanel = summary => {
        if (!cartItemsEl || !cartSubtotalEl || !cartCountEl) return;
        const count = summary.count || 0;
        const subtotal = summary.subtotal || 0;
        cartCountEl.textContent = count;
        cartCountEl.style.display = count > 0 ? 'inline-flex' : 'none';
        cartSubtotalEl.textContent = `RD$ ${subtotal.toFixed(2)}`;

        if (!summary.items || summary.items.length === 0) {
            cartItemsEl.innerHTML = '<p class="cart-panel-empty">Tu carrito está vacío.</p>';
            return;
        }

        cartItemsEl.innerHTML = summary.items
            .map(item => {
                const image = item.image_url || 'https://placehold.co/48x48';
                return `
                <div class="cart-panel-item">
                    <img src="${image}" alt="${item.name}">
                    <div>
                        <h4>${item.name}</h4>
                        <span>${item.quantity} x RD$ ${item.price.toFixed(2)}</span>
                    </div>
                </div>
            `;
            })
            .join('');
    };

    const fetchCartSummary = () =>
        fetch('/cart/summary', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(renderCartPanel)
            .catch(() => {});

    if (cartToggle && cartPanel) {
        cartToggle.addEventListener('click', event => {
            event.preventDefault();
            cartPanel.classList.toggle('active');
            if (cartPanel.classList.contains('active')) {
                fetchCartSummary();
            }
        });

        document.addEventListener('click', event => {
            if (!cartPanel.contains(event.target) && !cartToggle.contains(event.target)) {
                cartPanel.classList.remove('active');
            }
        });
    }

    fetchCartSummary();

    const ajaxAddForms = document.querySelectorAll('form[data-ajax-add]');
    ajaxAddForms.forEach(form => {
        form.addEventListener('submit', event => {
            event.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(async response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                        return null;
                    }
                    return response.json();
                })
                .then(summary => {
                    if (summary) {
                        renderCartPanel(summary);
                        if (cartPanel) {
                            cartPanel.classList.add('active');
                        }
                    }
                })
                .catch(() => {});
        });
    });

    // Simple hero slider (two images, 5s interval)
    const hero = document.querySelector('[data-hero-images]');
    if (hero) {
        const bg = hero.querySelector('.hero-bg');
        const images = hero.dataset.heroImages
            .split('|')
            .map(value => value.trim())
            .filter(Boolean);

        if (bg && images.length > 0) {
            let index = 0;
            bg.style.backgroundImage = `url('${images[index]}')`;

            if (images.length > 1) {
                setInterval(() => {
                    bg.classList.add('fade-out');
                    index = (index + 1) % images.length;
                    setTimeout(() => {
                        bg.style.backgroundImage = `url('${images[index]}')`;
                        bg.classList.remove('fade-out');
                    }, 300);
                }, 5000);
            }
        }
    }

    const confirmModal = document.getElementById('confirmModal');
    const confirmMessage = document.getElementById('confirmModalMessage');
    const confirmAccept = document.getElementById('confirmModalAccept');
    const confirmCloseItems = document.querySelectorAll('[data-modal-close]');
    let pendingForm = null;

    const openConfirmModal = message => {
        if (!confirmModal) return;
        confirmMessage.textContent = message || '¿Seguro que deseas continuar?';
        confirmModal.classList.add('active');
        confirmModal.setAttribute('aria-hidden', 'false');
    };

    const closeConfirmModal = () => {
        if (!confirmModal) return;
        confirmModal.classList.remove('active');
        confirmModal.setAttribute('aria-hidden', 'true');
        pendingForm = null;
    };

    if (confirmModal && confirmAccept) {
        document.querySelectorAll('form[data-confirm]').forEach(form => {
            form.addEventListener('submit', event => {
                event.preventDefault();
                pendingForm = form;
                openConfirmModal(form.dataset.confirm);
            });
        });

        confirmCloseItems.forEach(item => {
            item.addEventListener('click', closeConfirmModal);
        });

        confirmAccept.addEventListener('click', () => {
            if (pendingForm) {
                pendingForm.submit();
            }
            closeConfirmModal();
        });
    }
});
