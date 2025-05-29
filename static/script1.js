// Handle sidebar menu active class
const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item => {
    const li = item.parentElement;

    item.addEventListener('click', function () {
        allSideMenu.forEach(i => {
            i.parentElement.classList.remove('active');
        });
        li.classList.add('active');
    });
});

// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
    sidebar.classList.toggle('hide');
});

// Handle search button on smaller screens
const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
    if (window.innerWidth < 576) {
        e.preventDefault();
        searchForm.classList.toggle('show');
        if (searchForm.classList.contains('show')) {
            searchButtonIcon.classList.replace('bx-search', 'bx-x');
        } else {
            searchButtonIcon.classList.replace('bx-x', 'bx-search');
        }
    }
});

// Hide sidebar on smaller screens
if (window.innerWidth < 768) {
    sidebar.classList.add('hide');
} else if (window.innerWidth > 576) {
    searchButtonIcon.classList.replace('bx-x', 'bx-search');
    searchForm.classList.remove('show');
}

window.addEventListener('resize', function () {
    if (this.innerWidth > 576) {
        searchButtonIcon.classList.replace('bx-x', 'bx-search');
        searchForm.classList.remove('show');
    }
});

// Switch between dark and light mode
const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
    document.body.classList.toggle('dark', this.checked);
});

// Modal handling for adding and editing inventory
function showInventoryForm() {
    const modal = new bootstrap.Modal(document.getElementById('inventoryModal'));
    modal.show();
}

function closeInventoryForm() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('inventoryModal'));
    modal.hide();
}

function populateEditModal(id, name, price, quantity, category, details) {
    document.getElementById('editProductId').value = id;
    document.getElementById('editProductName').value = name;
    document.getElementById('editPrice').value = price;
    document.getElementById('editQuantity').value = quantity;
    document.getElementById('editCategory').value = category;
    document.getElementById('editDetails').value = details;

    document.getElementById('editProductForm').action = `/seller/edit_product/${id}`;
}

// Close the modal if the user clicks anywhere outside of it (for the add modal)
window.onclick = function (event) {
    const modal = document.getElementById("inventoryModal");
    if (event.target == modal) {
        closeInventoryForm();
    }
};


