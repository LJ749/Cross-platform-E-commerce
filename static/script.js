document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const showPasswordCheckbox = document.getElementById("show-password");

    // Check if elements exist
    if (passwordInput && showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener("change", function () {
            passwordInput.setAttribute("type", this.checked ? "text" : "password");
        });
    }

    // Navbar toggle functionality
    const navToggler = document.querySelector("[data-nav-toggler]");
    const navbar = document.querySelector("[data-navbar]");
    const navbarLinks = document.querySelectorAll("[data-nav-link]");

    const toggleNavbar = function () {
        navbar.classList.toggle("active");
        navToggler.classList.toggle("active");
    };

    if (navToggler) {
        navToggler.addEventListener("click", toggleNavbar);
    }

    const closeNavbar = function () {
        navbar.classList.remove("active");
        navToggler.classList.remove("active");
    };

    navbarLinks.forEach(link => {
        link.addEventListener("click", closeNavbar);
    });

    // Active header on scroll
    const header = document.querySelector("[data-header]");
    const backTopBtn = document.querySelector("[data-back-top-btn]");

    const activeElemOnScroll = function () {
        if (window.scrollY > 1) {
            header.classList.add("active");
            backTopBtn.classList.add("active");
        } else {
            header.classList.remove("active");
            backTopBtn.classList.remove("active");
        }
    };

    window.addEventListener("scroll", activeElemOnScroll);
});

// Use strict mode
'use strict';

/**
 * Add event listener on element(s)
 */
const addEventOnElem = function (elem, type, callback) {
    if (NodeList.prototype.isPrototypeOf(elem) || Array.isArray(elem)) {
        elem.forEach(e => e.addEventListener(type, callback));
    } else {
        elem.addEventListener(type, callback);
    }
};

/**
 * Navbar toggle functionality
 */
const navToggler = document.querySelector("[data-nav-toggler]");
const navbar = document.querySelector("[data-navbar]");
const navbarLinks = document.querySelectorAll("[data-nav-link]");

const toggleNavbar = function () {
    navbar.classList.toggle("active");
    navToggler.classList.toggle("active");
};

addEventOnElem(navToggler, "click", toggleNavbar);

const closeNavbar = function () {
    navbar.classList.remove("active");
    navToggler.classList.remove("active");
};

addEventOnElem(navbarLinks, "click", closeNavbar);

/**
 * Active header on scroll
 */
const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

const activeElemOnScroll = function () {
    if (window.scrollY > 5) {
        header.classList.add("active");
        backTopBtn.classList.add("active");
    } else {
        header.classList.remove("active");
        backTopBtn.classList.remove("active");
    }
};

addEventOnElem(window, "scroll", activeElemOnScroll);

/**
 * Add product to cart
 */
function addToCart(productId) {
    const quantity = document.getElementById('quantity').value;
    const selectedVariation = document.querySelector('input[name="selected-variation"]:checked');
    const selectedAttribute = document.querySelector('input[name="selected-attribute"]:checked');

    if (!selectedVariation || !selectedAttribute) {
        alert("Please select a variation and an attribute.");
        return;
    }

    const variationName = selectedVariation.value;
    const variationValue = selectedAttribute.value;

    // Get the price and stock from the selected attribute
    const selectedVariationPrice = selectedAttribute.getAttribute('data-price');
    const selectedVariationStock = selectedAttribute.getAttribute('data-stock');

    // Get the variation_id from the hidden input
    const variationIndex = selectedVariation.closest('.variation-group').querySelector('input[type="hidden"]').value;

    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            variation_name: variationName,
            variation_value: variationValue,
            price: selectedVariationPrice, // Send the price of the selected variation
            stock: selectedVariationStock, // Send the stock of the selected variation
            variation_id: variationIndex  // Send the variation_id from the hidden input
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI to reflect cart changes, e.g., update cart total items
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function buynow(productId) {
    const quantity = document.getElementById('quantity').value;
    const selectedVariation = document.querySelector('input[name="selected-variation"]:checked');
    const selectedAttribute = document.querySelector('input[name="selected-attribute"]:checked');

    if (!selectedVariation || !selectedAttribute) {
        alert("Please select a variation and an attribute.");
        return;
    }

    const variationName = selectedVariation.value;
    const variationValue = selectedAttribute.value;

    // Get the price and stock from the selected attribute
    const selectedVariationPrice = selectedAttribute.getAttribute('data-price');
    const selectedVariationStock = selectedAttribute.getAttribute('data-stock');

    // Get the variation_id from the hidden input
    const variationIndex = selectedVariation.closest('.variation-group').querySelector('input[type="hidden"]').value;

    fetch('/buy_now', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            variation_name: variationName,
            variation_value: variationValue,
            price: selectedVariationPrice, // Send the price of the selected variation
            stock: selectedVariationStock, // Send the stock of the selected variation
            variation_id: variationIndex  // Send the variation_id from the hidden input
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


/**
 * Handles the state of the increase and decrease buttons dynamically.
 */
function handleQuantityChange() {
    const quantityInput = document.getElementById('quantity');
    const decreaseBtn = document.getElementById('decrease-btn');
    const increaseBtn = document.getElementById('increase-btn');

    const currentQuantity = parseInt(quantityInput.value, 10);
    const maxQuantity = parseInt(quantityInput.max, 10);
    const minQuantity = parseInt(quantityInput.min, 10);

    // Disable the decrease button if at minimum quantity
    decreaseBtn.disabled = currentQuantity <= minQuantity;

    // Disable the increase button if at maximum quantity (stock)
    increaseBtn.disabled = currentQuantity >= maxQuantity;
}

/**
 * Update the quantity and refresh button states.
 * @param {string} action - Either 'increase' or 'decrease'.
 */
function updateQuantity(action) {
    const quantityInput = document.getElementById('quantity');
    let currentQuantity = parseInt(quantityInput.value, 10);
    const maxQuantity = parseInt(quantityInput.max, 10);
    const minQuantity = parseInt(quantityInput.min, 10);

    // Ensure currentQuantity is a valid number
    if (isNaN(currentQuantity)) {
        currentQuantity = minQuantity; // Default to minimum if invalid
    }

    if (action === 'increase' && currentQuantity < maxQuantity) {
        currentQuantity++;
    } else if (action === 'decrease' && currentQuantity > minQuantity) {
        currentQuantity--;
    }

    quantityInput.value = currentQuantity;

    // Refresh button states
    handleQuantityChange();
}

// Initialize button states on page load
document.addEventListener('DOMContentLoaded', handleQuantityChange);




/**
 * Validate quantity input
 */
function validateQuantity() {
    const quantityInput = document.getElementById('quantity');
    const maxQuantity = parseInt(quantityInput.max);
    const currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity > maxQuantity || currentQuantity < 1) {
        document.getElementById('error-message').textContent = 'Invalid quantity.';
        return false;
    }

    return true;
}

/**
 * Manage selected variations
 */
let selectedVariations = {};

function updateSelectedVariations() {
    const list = document.getElementById('selected-variations-list');
    list.innerHTML = ''; // Clear existing list

    for (const [key, value] of Object.entries(selectedVariations)) {
        const listItem = document.createElement('li');
        listItem.textContent = `${key}: ${value}`;
        list.appendChild(listItem);
    }
}

let selectedVariationName = null;
let selectedVariationValue = null;
let selectedVariationId = null; // Store the variation ID

function selectVariationName(button, attributeName, index) {
    // Reset the selected state for the previous selection
    if (selectedVariationName) {
        const previousButton = document.querySelector('.variation-name.selected');
        if (previousButton) {
            previousButton.classList.remove('selected');
            const previousIndex = previousButton.getAttribute('data-index');
            const previousButtonsContainer = document.getElementById(`buttons-${previousIndex}`);
            const previousVariationButtons = previousButtonsContainer.querySelectorAll('.variation-button');

            // Disable buttons of the previous selection
            previousVariationButtons.forEach(btn => {
                btn.disabled = true;
                btn.classList.remove('selected');
            });
        }
    }

    // Set the new selected variation name
    selectedVariationName = attributeName;
    button.classList.add('selected'); // Mark this button as selected

    // Enable corresponding buttons for the selected variation name
    const buttonsContainer = document.getElementById(`buttons-${index}`);
    const variationButtons = buttonsContainer.querySelectorAll('.variation-button');

    // Enable all buttons for the selected variation name
    variationButtons.forEach(btn => {
        btn.disabled = false; // Enable all buttons for the current variation
    });
}




function selectVariation(attributeName, attributeValue, attributePrice, attributeStock, imageUrl, variationId) {
    // Deselect the previously selected button if any
    const previousSelectedButton = document.querySelector('.variation-button.selected');
    if (previousSelectedButton) {
        previousSelectedButton.classList.remove('selected');
    }

    // Set the new selected variation details
    selectedVariationName = attributeName;
    selectedVariationValue = attributeValue;
    selectedVariationId = variationId;

    // Find the current button associated with the selected value
    const variationButtons = document.querySelectorAll('.variation-button');
    let currentButton = null;

    variationButtons.forEach((btn) => {
        const input = btn.querySelector('input');
        if (input && input.value === attributeValue) {
            currentButton = btn;
        }
    });

    if (!currentButton) {
        console.error(`Button for attribute value '${attributeValue}' not found.`);
        return; // Exit if no button is found
    }

    // Highlight the selected button
    currentButton.classList.add('selected');

    // Update product image preview, price, and stock
    const imagePreview = document.getElementById('image-preview');
    if (imagePreview) {
        imagePreview.src = imageUrl; // Update image preview
    }

    const productPriceElement = document.getElementById('product-price');
    const productQuantityElement = document.getElementById('product-quantity');
    if (productPriceElement) {
        productPriceElement.innerText = '₱ ' + attributePrice; // Update price
    }
    if (productQuantityElement) {
        productQuantityElement.innerText = 'Stock: ' + attributeStock; // Update stock
    }

    // Update quantity input max value and re-enable buttons in the same variation group
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.max = attributeStock; // Update max quantity based on stock
        if (parseInt(quantityInput.value, 10) > attributeStock) {
            quantityInput.value = attributeStock; // Reset quantity if it exceeds new stock
        }
        handleQuantityChange(); // Update quantity buttons
    }

    // Re-enable all buttons in the same variation group and disable non-selected ones
    const buttonsContainer = currentButton.closest('.variation-buttons');
    if (buttonsContainer) {
        const allButtons = buttonsContainer.querySelectorAll('.variation-button');
        allButtons.forEach((btn) => {
            const input = btn.querySelector('input');
            if (btn === currentButton) {
                input.disabled = false; // Keep the selected button enabled
            } else {
                input.disabled = false; // Disable other buttons in the same group
            }
        });
    }
}



function enableAttributeButtons(index) {
    // Hide and disable all attribute buttons first
    document.querySelectorAll('.variation-buttons').forEach(buttonGroup => {
        buttonGroup.style.display = 'none';
        buttonGroup.querySelectorAll('input[type="radio"]').forEach(button => {
            button.disabled = true;
            button.checked = false;
        });
    });

    // Show and enable only the selected variation's attribute buttons
    const selectedButtonsDiv = document.getElementById(`buttons-${index}`);
    selectedButtonsDiv.style.display = 'block';
    selectedButtonsDiv.querySelectorAll('input[type="radio"]').forEach(button => {
        button.disabled = false;
    });
}







