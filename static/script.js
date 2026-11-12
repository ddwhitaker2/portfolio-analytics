// Remember the theme when moving between pages.
const themeToggle = document.getElementById('theme-toggle');
let savedTheme = 'light';
try {
    savedTheme = localStorage.getItem('portfolio-theme') || 'light';
} catch (error) {
    // The toggle still works if browser storage is unavailable.
}
function applyTheme(dark) {
    document.body.classList.toggle('dark', dark);
    themeToggle.setAttribute('aria-pressed', String(dark));
    themeToggle.textContent = dark ? 'Light/Dark Mode: Dark' : 'Light/Dark Mode: Light';
}
applyTheme(savedTheme === 'dark');
themeToggle.addEventListener('click', function () {
    const dark = !document.body.classList.contains('dark');
    applyTheme(dark);
    try {
        localStorage.setItem('portfolio-theme', dark ? 'dark' : 'light');
    } catch (error) {
        // Keep the selected theme for this page even without storage.
    }
});

// The guide can be hidden and reopened using the same button.
const guideToggle = document.getElementById('guide-toggle');
const guide = document.getElementById('getting-started');
if (guideToggle && guide) {
    guideToggle.addEventListener('click', function () {
        guide.hidden = !guide.hidden;
        guideToggle.setAttribute('aria-expanded', String(!guide.hidden));
        guideToggle.textContent = guide.hidden ? 'Show Getting Started' : 'Hide Getting Started';
    });
}

// Reuse the existing Flask forms inside a native, keyboard-accessible popup.
const actionDialog = document.getElementById('action-dialog');
const popupContent = document.getElementById('popup-content');
let popupOpener;
function closePopup() {
    actionDialog.close();
}
function showPopup(content, opener) {
    popupOpener = opener;
    popupContent.replaceChildren(content);
    // Keep labels unique when the portfolio page still contains its hidden form.
    popupContent.querySelectorAll('input[id], select[id]').forEach(input => {
        const oldId = input.id;
        popupContent.querySelectorAll('label').forEach(label => {
            if (label.htmlFor === oldId) label.htmlFor = 'popup-' + oldId;
        });
        input.id = 'popup-' + oldId;
    });
    const title = popupContent.querySelector('h1, h2');
    title.id = 'popup-title';
    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.textContent = 'Cancel';
    cancel.className = 'secondary';
    cancel.addEventListener('click', closePopup);
    const form = popupContent.querySelector('form');
    if (form) {
        // Cancel closes the popup without sending any changes.
        form.querySelectorAll('a').forEach(link => link.remove());
        form.append(' ', cancel);
        addCostPreview(form);
    } else {
        popupContent.append(cancel);
    }
    actionDialog.showModal();
}
actionDialog.addEventListener('close', function () {
    if (popupOpener) popupOpener.focus();
    popupContent.replaceChildren();
});

async function openForm(url, opener) {
    opener.setAttribute('aria-busy', 'true');
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Unable to load form');
        const page = new DOMParser().parseFromString(await response.text(), 'text/html');
        let content = page.querySelector('#portfolio-create') || page.querySelector('main section');
        if (!content || !content.querySelector('form')) throw new Error('Form not found');
        content = document.importNode(content, true);
        content.hidden = false;
        showPopup(content, opener);
    } catch (error) {
        // The normal page remains available if loading the popup fails.
        window.location.href = url;
    } finally {
        opener.removeAttribute('aria-busy');
    }
}
document.querySelectorAll('a[data-popup]').forEach(link => {
    link.addEventListener('click', function (event) {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        openForm(link.href, link);
    });
});
const portfolioCreate = document.getElementById('portfolio-create');
const portfolioOpen = document.getElementById('portfolio-open');
if (portfolioCreate && portfolioOpen) {
    portfolioCreate.hidden = true;
    portfolioOpen.hidden = false;
    portfolioOpen.addEventListener('click', function () {
        const content = portfolioCreate.cloneNode(true);
        content.removeAttribute('id');
        content.hidden = false;
        showPopup(content, portfolioOpen);
    });
}

function money(value) {
    return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}
function addCostPreview(form) {
    const shares = form.elements.namedItem('shares');
    const price = form.elements.namedItem('purchase_price');
    if (!shares || !price) return;
    const savedCost = Number(shares.defaultValue) * Number(price.defaultValue);
    const editing = form.action.includes('/edit');
    const preview = document.createElement('p');
    preview.className = 'cost-preview';
    form.insertBefore(preview, form.querySelector('button'));
    if (editing) {
        [shares, price, form.elements.namedItem('ticker'), form.elements.namedItem('current_price')].forEach(input => {
            const saved = document.createElement('small');
            saved.textContent = 'Saved: ' + input.defaultValue;
            input.parentElement.append(document.createElement('br'), saved);
        });
    }
    function updatePreview() {
        const cost = Number(shares.value) * Number(price.value);
        if (!shares.value || !price.value || !Number.isFinite(cost) || cost < 0) {
            preview.textContent = 'Enter valid shares and purchase price to preview the recorded cost.';
            return;
        }
        preview.textContent = editing
            ? 'Saved recorded cost: ' + money(savedCost) + '. After saving: ' + money(cost) + '. Portfolio cost change: ' + money(cost - savedCost) + '.'
            : 'Recorded cost after adding: ' + money(cost) + '.';
    }
    form.addEventListener('input', updatePreview);
    updatePreview();
}

// Removal explains the affected record and cost before the user confirms.
document.querySelectorAll('form[data-delete]').forEach(form => {
    form.removeAttribute('onsubmit');
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const content = document.createElement('div');
        const title = document.createElement('h2');
        title.textContent = 'Remove Holding';
        const warning = document.createElement('p');
        warning.textContent = 'Remove ' + form.dataset.ticker + ' from ' + form.dataset.portfolio + '? This permanently deletes its saved purchase information and cannot be undone. You would have to enter it again.';
        const record = document.createElement('p');
        const cost = Number(form.dataset.shares) * Number(form.dataset.price);
        record.textContent = 'Selected holding: ' + form.dataset.ticker + '. Shares: ' + form.dataset.shares + '. Purchase price: ' + money(Number(form.dataset.price)) + '. Recorded cost: ' + money(cost) + '.';
        const impact = document.createElement('p');
        impact.textContent = 'Portfolio recorded cost will go from ' + money(Number(form.dataset.total)) + ' to ' + money(Number(form.dataset.total) - cost) + '.';
        const confirmation = document.createElement('form');
        confirmation.method = 'post';
        confirmation.action = form.action;
        const remove = document.createElement('button');
        remove.type = 'submit';
        remove.textContent = 'Remove Holding';
        confirmation.append(remove);
        content.append(title, warning, record, impact, confirmation);
        showPopup(content, form.querySelector('button'));
        confirmation.querySelector('.secondary').focus();
    });
});

const welcomeDialog = document.getElementById('welcome-dialog');
if (welcomeDialog) {
    document.getElementById('welcome-open').addEventListener('click', () => welcomeDialog.showModal());
    document.getElementById('welcome-close').addEventListener('click', () => welcomeDialog.close());
    let seenWelcome = false;
    try { seenWelcome = localStorage.getItem('portfolio-welcome-seen') === 'true'; } catch (error) {}
    if (!seenWelcome) welcomeDialog.showModal();
    welcomeDialog.addEventListener('close', function () {
        try { localStorage.setItem('portfolio-welcome-seen', 'true'); } catch (error) {}
        document.getElementById('welcome-open').focus();
    });
}
