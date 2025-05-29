'use strict';

document.addEventListener("DOMContentLoaded", function () {
  const quantityInputs = document.querySelectorAll('.quantity-input');

  quantityInputs.forEach(input => {
      input.addEventListener('input', function () {
          const itemRow = this.closest('tr');
          const price = parseFloat(itemRow.querySelector('.item-price').innerText);
          const quantity = parseInt(this.value);
          const itemTotal = itemRow.querySelector('.item-total');

          // Update the item's total
          itemTotal.innerText = (price * quantity).toFixed(2);

          // Update overall totals
          updateCartSummary();
      });
  });
});

// Function to update the cart summary
// Function to update the cart summary
function updateCartSummary() {
  const itemTotals = document.querySelectorAll('.item-total');
  let subtotal = 0;

  itemTotals.forEach(total => {
      const itemValue = parseFloat(total.innerText) || 0; // Fallback to 0 if parsing fails
      subtotal += itemValue;
  });

  const shipping = 50; // Example fixed shipping fee
  const total = subtotal;

  const subtotalElement = document.querySelector('.cart-summary .subtotal span');
  const totalElement = document.querySelector('.cart-summary .total span');

  // Check if elements exist before updating
  if (subtotalElement) {
      subtotalElement.innerText = subtotal.toFixed(2);
  } else {
      console.warn('Subtotal element not found.');
  }

  if (totalElement) {
      totalElement.innerText = total.toFixed(2);
  } else {
      console.warn('Total element not found.');
  }
}



function removeItem(itemId) {
  fetch('/remove_from_cart', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ item_id: itemId })
  })
  .then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
          // Fetch the updated cart contents
          return fetch('/cart'); // Assuming '/cart' endpoint returns the updated cart view
      } else {
          alert(data.message); // Show error message
      }
  })
  .then(response => response.text())
  .then(html => {
      // Replace the cart contents in the DOM with the updated HTML
      const cartContainer = document.querySelector('.cart-container'); // Make sure this matches your HTML structure
      cartContainer.innerHTML = html; // Update the cart content
  })
  .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while removing the item.');
  });
}




/**
 * add event on element
 */

const addEventOnElem = function (elem, type, callback) {
  if (elem.length > 1) {
    for (let i = 0; i < elem.length; i++) {
      elem[i].addEventListener(type, callback);
    }
  } else {
    elem.addEventListener(type, callback);
  }
}



/**
 * navbar toggle
 */

const navToggler = document.querySelector("[data-nav-toggler]");
const navbar = document.querySelector("[data-navbar]");
const navbarLinks = document.querySelectorAll("[data-nav-link]");

const toggleNavbar = function () {
  navbar.classList.toggle("active");
  navToggler.classList.toggle("active");
}

addEventOnElem(navToggler, "click", toggleNavbar);


const closeNavbar = function () {
  navbar.classList.remove("active");
  navToggler.classList.remove("active");
}

addEventOnElem(navbarLinks, "click", closeNavbar);



/**
 * active header when window scroll down to 100px
 */

const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

const activeElemOnScroll = function () {
  if (window.scrollY > 100) {
    header.classList.add("active");
    backTopBtn.classList.add("active");
  } else {
    header.classList.remove("active");
    backTopBtn.classList.remove("active");
  }
}

addEventOnElem(window, "scroll", activeElemOnScroll);

function addToCart(productId) {
  // Implement the logic to add the product to the cart
  console.log(`Product ${productId} added to cart.`);
  alert(`Product ${productId} added to cart!`); // For demonstration purposes
}

function buyNow(productId) {
  // Implement the logic to proceed to checkout with the selected product
  console.log(`Buying product ${productId}.`);
  alert(`Proceeding to buy product ${productId}.`); // For demonstration purposes
}

const quantityInputs = document.querySelectorAll('.quantity-input');

quantityInputs.forEach(input => {
    input.addEventListener('input', function () {
        const itemRow = this.closest('tr');
        const price = parseFloat(itemRow.querySelector('.item-price').innerText.replace('₱', '').replace(',', ''));
        const quantity = parseInt(this.value);
        const itemTotal = itemRow.querySelector('.item-total');

        // Update the item's total
        itemTotal.innerText = (price * quantity).toFixed(2); // Update individual item's total

        // Update overall totals
        updateCartSummary(); // Call to recalculate subtotal and total
    });
});

document.getElementById('search-btn').addEventListener('click', function() {
  const searchBar = document.getElementById('search-bar');
  
  // Toggle visibility
  if (searchBar.classList.contains('visible')) {
    searchBar.classList.remove('visible');
  } else {
    searchBar.classList.add('visible');
    searchBar.focus(); // Automatically focus on the search bar when it appears
  }
});

function toggleDropdown() {
  var dropdown = document.getElementById('userDropdown');
  dropdown.classList.toggle('show');  // Toggle the display of the dropdown
}

function toggleDropdown() {
  // Get the header element
  var header = document.querySelector('.header');
  
  // Check if the header has the "active" class
  if (header.classList.contains('active')) {
    var dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');  // Toggle the display of the dropdown
  }
}

// Optionally, close the dropdown if the user clicks anywhere outside it
window.addEventListener('click', function(event) {
  var header = document.querySelector('.header');
  var dropdown = document.getElementById('userDropdown');
  var button = document.querySelector('.action-btn.user');
  
  // Check if the click is outside the header and the dropdown
  if (!header.contains(event.target) && !dropdown.contains(event.target) && !button.contains(event.target)) {
    dropdown.classList.remove('show');  // Close the dropdown
  }
});









