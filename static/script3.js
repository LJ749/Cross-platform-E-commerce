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

const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
    if (this.checked) {
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark');
    }
});

// Data for the charts
document.addEventListener("DOMContentLoaded", function () {
    // Get data attributes for seller and buyer counts
    const chartDataDiv = document.getElementById("chartData");
    const sellerCount = parseInt(chartDataDiv.getAttribute("data-seller"));
    const buyerCount = parseInt(chartDataDiv.getAttribute("data-buyer"));

    // Data for Bar Chart
    const barData = {
        labels: ['Sellers', 'Buyers'],
        datasets: [{
            label: 'Count',
            data: [sellerCount, buyerCount],
            backgroundColor: [
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 99, 132, 0.2)'
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    };

    // Configuration for Bar Chart
    const barConfig = {
        type: 'bar',
        data: barData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Sellers and Buyers Bar Chart'
                }
            }
        }
    };

    // Initialize Bar Chart
    new Chart(document.getElementById('barChart'), barConfig);

    // Data for Pie Chart
    const pieData = {
        labels: ['Sellers', 'Buyers'],
        datasets: [{
            data: [sellerCount, buyerCount],
            backgroundColor: [
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 99, 132, 0.5)'
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    };

    // Configuration for Pie Chart
    const pieConfig = {
        type: 'pie',
        data: pieData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Sellers vs Buyers Pie Chart'
                }
            }
        }
    };

    // Initialize Pie Chart
    new Chart(document.getElementById('pieChart'), pieConfig);
});

// Get modal element and close button
const messageModal = document.getElementById('messageModal');
const closeModalBtn = document.querySelector('.modal .close');

// Show modal when 'Message' button is clicked
document.querySelectorAll('.btn-message').forEach(button => {
    button.addEventListener('click', () => {
        messageModal.style.display = 'flex';
    });
});

// Close modal when 'X' button is clicked
closeModalBtn.addEventListener('click', () => {
    messageModal.style.display = 'none';
});

// Close modal when clicking outside the modal content
window.addEventListener('click', (e) => {
    if (e.target === messageModal) {
        messageModal.style.display = 'none';
    }
});

socket.on('status_update', function(data) {
    // Find the row for the user with the given user_id and update the status.
    let statusElement = document.querySelector(`.status[data-user-id="${data.user_id}"]`);
    if (statusElement) {
        statusElement.textContent = data.status;  // Updates status to 'Active' or 'Offline'
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('feedbackModal');
    const feedbackMessage = document.getElementById('feedbackMessage');
    const closeModalButton = document.querySelector('.modal .close');

    window.showFeedback = function(message) {
        feedbackMessage.textContent = message;
        modal.style.display = 'block';
    }

    function closeModal() {
        modal.style.display = 'none';
    }

    closeModalButton.addEventListener('click', closeModal);

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
});

// Wait for the page to load
document.addEventListener('DOMContentLoaded', function() {
    // Select all rows in the table
    const rows = document.querySelectorAll('table tbody tr');
    
    // Loop through each row and calculate the commission
    rows.forEach(function(row) {
        // Get the price from the row
        const priceCell = row.querySelector('.price');
        const price = parseFloat(priceCell.textContent.replace('₱', '').trim());

        // Calculate the commission (3% of the price)
        const commission = price * 0.10;

        // Set the formatted price with the peso sign
        priceCell.textContent = `₱${price.toFixed(2)}`;

        // Find the commission cell and set the calculated commission with the peso sign
        const commissionCell = row.querySelector('.commission');
        commissionCell.textContent = `₱${commission.toFixed(2)}`;
    });
});

function banUser(userId) {
    if (confirm("Are you sure you want to ban this user?")) {
        fetch(`/ban_user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("User has been banned.");
                location.reload();
            } else {
                alert("Failed to ban user. Please try again.");
            }
        })
        .catch(error => console.error('Error:', error));
    }
}


// JavaScript to handle opening and closing of the Ban Modal
document.addEventListener("DOMContentLoaded", function() {
    // Get the modal and button elements
const banModal = document.getElementById("banModal");
const banButton = document.querySelector(".btn-ban");
const closeButton = document.querySelector(".modal-content .close");

// Show modal when 'Ban' button is clicked
banButton.addEventListener("click", function(event) {
    event.preventDefault();
    banModal.style.display = "flex"; // Show the modal with flex to center content
});

// Hide modal when close button is clicked
closeButton.addEventListener("click", function() {
    banModal.style.display = "none";
});

// Hide modal when clicking outside of the modal content
window.addEventListener("click", function(event) {
    if (event.target === banModal) {
        banModal.style.display = "none";
    }
});

});

document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
