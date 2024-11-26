// Global variables
let currentPage = 1;
let cart = new Map();
let isAuthenticated = false;
let currentUser = null;
let currentOrder = null;

// DOM Elements
const authScreen = document.getElementById('auth-screen');
const orderOptions = document.getElementById('order-options');
const activeOrder = document.getElementById('active-order');
const signupForm = document.getElementById('signup-form');
const loginForm = document.getElementById('login-form');
const logoutBtn = document.getElementById('logout-btn');
const userNameDisplay = document.getElementById('user-name');

// View management
function showScreen(screenId) {
    // Hide all screens
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('order-options').classList.add('hidden');
    document.getElementById('active-order').classList.add('hidden');
    
    // Show the requested screen
    document.getElementById(screenId).classList.remove('hidden');
}

// Authentication Functions
async function handleSignup(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password')
    };

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (response.ok && responseData.success) {
            currentUser = responseData.user;
            isAuthenticated = true;
            showScreen('order-options');
            updateUserDisplay();
            event.target.reset();
        } else {
            alert(responseData.message || 'Signup failed');
        }
    } catch (error) {
        console.error('Error during signup:', error);
        alert('An error occurred during signup');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (response.ok && responseData.success) {
            currentUser = responseData.user;
            isAuthenticated = true;
            showScreen('order-options');
            updateUserDisplay();
            event.target.reset();
        } else {
            alert(responseData.message || 'Login failed');
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred during login');
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Clear any stored data
            updateCartDisplay([]);
            
            // Switch to auth screen
            showScreen('auth-screen');
            
            // Reset forms
            if (document.getElementById('signup-form')) {
                document.getElementById('signup-form').reset();
            }
            if (document.getElementById('login-form')) {
                document.getElementById('login-form').reset();
            }
            
            // Show success message
            if (data.message) {
                alert(data.message);
            }
        } else {
            alert(data.message || 'Failed to logout');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        alert('Failed to logout. Please try again.');
    }
}

function updateUserDisplay() {
    const userDisplayOptions = document.getElementById('user-display-options');
    const userDisplayActive = document.getElementById('user-display-active');
    
    if (currentUser) {
        const displayText = `Logged in as: ${currentUser.name}`;
        if (userDisplayOptions) userDisplayOptions.textContent = displayText;
        if (userDisplayActive) userDisplayActive.textContent = displayText;
    }
}

// Order Management Functions
async function createOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        name: formData.get('order-name')
    };

    try {
        const response = await fetch('/create_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (response.ok && responseData.success) {
            currentOrder = responseData.order;
            showScreen('active-order');
            updateOrderHeader();
            loadMenuItems();
            alert(`Order created! Share this PIN with others: ${responseData.pin}`);
            event.target.reset();
        } else {
            alert(responseData.message || 'Failed to create order');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        alert('An error occurred while creating the order');
    }
}

async function joinOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const pin = formData.get('order-pin');
    
    console.log('Attempting to join order with PIN:', pin);

    if (!pin) {
        alert('Please enter a PIN');
        return;
    }

    try {
        console.log('Sending join request...');
        const response = await fetch('/join_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pin: pin })
        });

        console.log('Response status:', response.status);
        const responseData = await response.json();
        console.log('Response data:', responseData);

        if (response.ok && responseData.success) {
            console.log('Successfully joined order:', responseData.order);
            currentOrder = responseData.order;
            showScreen('active-order');
            updateOrderHeader();
            loadMenuItems();
            event.target.reset();
        } else {
            console.error('Failed to join order:', responseData.message);
            alert(responseData.message || 'Failed to join order');
        }
    } catch (error) {
        console.error('Error joining order:', error);
        alert('An error occurred while joining the order');
    }
}

function updateOrderHeader() {
    const orderHeader = document.getElementById('order-header');
    if (orderHeader && currentOrder) {
        orderHeader.textContent = `Current Order: ${currentOrder.name} (PIN: ${currentOrder.pin})`;
    }
}

// Menu Items Management
async function loadMenuItems() {
    try {
        const response = await fetch('/menu_items');
        if (response.ok) {
            const data = await response.json();
            const menuContainer = document.getElementById('menu-categories');
            menuContainer.innerHTML = '';
            
            Object.entries(data.categories).forEach(([category, items]) => {
                const categoryElement = document.createElement('div');
                categoryElement.className = 'bg-white rounded-lg shadow-lg p-6';
                categoryElement.innerHTML = `
                    <h3 class="text-2xl font-bold mb-6 text-gray-800">${category}</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        ${items.map(item => `
                            <div class="bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                                <div class="flex justify-between items-start">
                                    <div class="flex-1">
                                        <h4 class="text-lg font-semibold text-gray-800">${item.name}</h4>
                                        ${item.description ? 
                                            `<p class="text-gray-600 text-sm mt-1 mb-3">${item.description}</p>` : 
                                            '<div class="mb-3"></div>'}
                                        <span class="text-lg font-bold text-indigo-600">$${item.price.toFixed(2)}</span>
                                    </div>
                                    <button 
                                        class="add-to-cart-btn ml-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 
                                               transition-colors duration-200 flex items-center"
                                        data-menu-item-id="${item.id}">
                                        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                                        </svg>
                                        Add
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                menuContainer.appendChild(categoryElement);
            });
        }
    } catch (error) {
        console.error('Error loading menu items:', error);
    }
}

// Cart Management
async function addToCart(menuItemId) {
    if (!menuItemId) {
        console.error('Menu item ID is missing');
        return;
    }
    
    try {
        const response = await fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ menu_item_id: parseInt(menuItemId) })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Update cart display with the new items
            updateCartDisplay(data.cart_items);
            
            // Show success message
            if (data.message) {
                console.log(data.message);
            }
        } else {
            alert(data.message || 'Failed to add item to cart');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Failed to add item to cart. Please try again.');
    }
}

function updateCartDisplay(cartItems) {
    const cartList = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    let total = 0;
    
    // Clear current cart display
    cartList.innerHTML = '';
    
    // Add each item to the cart display
    cartItems.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'flex justify-between items-center p-2 border-b';
        itemElement.innerHTML = `
            <div>
                <h4 class="font-semibold">${item.name}</h4>
                <p class="text-gray-600">$${item.price.toFixed(2)} x ${item.quantity}</p>
            </div>
            <div class="text-right">
                <p class="font-semibold">$${item.total.toFixed(2)}</p>
            </div>
        `;
        cartList.appendChild(itemElement);
        total += item.total;
    });
    
    // Update total
    cartTotal.textContent = `Total: $${total.toFixed(2)}`;
}

async function leaveOrder() {
    if (!confirm('Are you sure you want to leave this order?')) {
        return;
    }
    
    try {
        const response = await fetch('/leave_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Clear cart display
            updateCartDisplay([]);
            
            // Switch back to order options screen
            showScreen('order-options');
            
            // Show success message
            if (data.message) {
                alert(data.message);
            }
        } else {
            alert(data.message || 'Failed to leave order');
        }
    } catch (error) {
        console.error('Error leaving order:', error);
        alert('Failed to leave order. Please try again.');
    }
}

async function generateReceipt() {
    try {
        const response = await fetch('/generate_receipt');
        const data = await response.json();

        if (response.ok && data.success) {
            const receipt = data.receipt;
            const modal = document.getElementById('receipt-modal');
            const modalContent = document.getElementById('receipt-content');

            // Create receipt HTML
            let receiptHtml = `
                <div class="text-lg font-bold mb-4">Order Receipt</div>
                <div class="mb-2">Order: ${receipt.order_name}</div>
                <div class="mb-4">PIN: ${receipt.order_pin}</div>
                <div class="mb-4">Time: ${receipt.timestamp}</div>
            `;

            // Add items for each user
            for (const [userName, userOrder] of Object.entries(receipt.user_orders)) {
                receiptHtml += `
                    <div class="mt-4 mb-2 font-semibold text-indigo-600">${userName}'s Order:</div>
                    <div class="border-t border-gray-200 mb-2"></div>
                `;

                // Add items
                userOrder.items.forEach(item => {
                    receiptHtml += `
                        <div class="flex justify-between mb-1">
                            <span>${item.quantity}x ${item.name}</span>
                            <span>$${(item.total).toFixed(2)}</span>
                        </div>
                    `;
                });

                // Add user subtotal
                receiptHtml += `
                    <div class="flex justify-between mt-2 font-semibold">
                        <span>Subtotal</span>
                        <span>$${userOrder.subtotal.toFixed(2)}</span>
                    </div>
                    <div class="border-b border-gray-200 mb-4"></div>
                `;
            }

            // Add total amount
            receiptHtml += `
                <div class="flex justify-between mt-4 text-lg font-bold">
                    <span>Total Amount</span>
                    <span>$${receipt.total_amount.toFixed(2)}</span>
                </div>
            `;

            modalContent.innerHTML = receiptHtml;
            modal.classList.remove('hidden');
        } else {
            alert(data.message || 'Failed to generate receipt');
        }
    } catch (error) {
        console.error('Error generating receipt:', error);
        alert('Failed to generate receipt. Please try again.');
    }
}

// Check authentication status on page load
async function checkAuth() {
    try {
        const response = await fetch('/check_auth');
        const data = await response.json();
        
        if (response.ok && data.authenticated) {
            isAuthenticated = true;
            currentUser = data.user;
            
            // Update user display
            updateUserDisplay();
            
            // Check if user has an active order
            if (data.active_order) {
                currentOrder = data.active_order;
                showScreen('active-order');
                updateOrderHeader();
                loadMenuItems();
            } else {
                showScreen('order-options');
            }
        } else {
            showScreen('auth-screen');
        }
    } catch (error) {
        console.error('Error checking auth:', error);
        showScreen('auth-screen');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication status
    checkAuth();
    
    // Form submissions
    document.getElementById('signup-form')?.addEventListener('submit', handleSignup);
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('create-order-form')?.addEventListener('submit', createOrder);
    document.getElementById('join-order-form')?.addEventListener('submit', joinOrder);
    
    // Auth tab switching
    document.querySelectorAll('[data-auth-tab]').forEach(tab => {
        tab.addEventListener('click', () => {
            const targetForm = tab.dataset.authTab === 'signup' ? 'signup-form' : 'login-form';
            document.getElementById('signup-form').classList.toggle('hidden', targetForm !== 'signup-form');
            document.getElementById('login-form').classList.toggle('hidden', targetForm !== 'login-form');
            
            // Update tab styles
            document.querySelectorAll('[data-auth-tab]').forEach(t => {
                t.classList.toggle('border-indigo-600', t === tab);
                t.classList.toggle('text-indigo-600', t === tab);
                t.classList.toggle('border-transparent', t !== tab);
                t.classList.toggle('text-gray-500', t !== tab);
            });
        });
    });
    
    // Menu item click handling
    document.addEventListener('click', (e) => {
        if (e.target.closest('.add-to-cart-btn')) {
            const button = e.target.closest('.add-to-cart-btn');
            const menuItemId = button.dataset.menuItemId;
            if (menuItemId) {
                addToCart(menuItemId);
            }
        }
    });
    
    // Generate receipt button
    document.getElementById('generate-receipt-btn')?.addEventListener('click', generateReceipt);
    
    // Logout buttons
    document.getElementById('logout-btn-options')?.addEventListener('click', handleLogout);
    document.getElementById('logout-btn-active')?.addEventListener('click', handleLogout);
    
    // Leave order button
    document.getElementById('leave-order-btn')?.addEventListener('click', leaveOrder);
    
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    });
});
