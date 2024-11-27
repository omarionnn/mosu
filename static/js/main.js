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

async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            // Clear session
            currentUser = null;
            cart.clear();
            // Show success message
            showMessage('Logged out successfully');
            // Switch to auth screen
            showScreen('auth-screen');
        } else {
            showError('Failed to logout');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to logout');
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
        order_name: formData.get('order-name')
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
            // Update order display
            document.getElementById('order-name-display').textContent = `Order: ${responseData.order.name}`;
            document.getElementById('order-pin-display').textContent = `PIN: ${responseData.order.pin}`;
            
            currentOrder = responseData.order;
            showScreen('active-order');
            loadMenuItems();
            showMessage(`Order created! Share this PIN with others: ${responseData.order.pin}`);
            event.target.reset();
        } else {
            showError(responseData.message || 'Failed to create order');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showError('An error occurred while creating the order');
    }
}

async function joinOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const pin = formData.get('order-pin');

    try {
        const response = await fetch('/join_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pin })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Update order display
            document.getElementById('order-name-display').textContent = `Order: ${data.order.name}`;
            document.getElementById('order-pin-display').textContent = `PIN: ${data.order.pin}`;
            
            currentOrder = data.order;
            showScreen('active-order');
            loadMenuItems();
            showMessage('Successfully joined order!');
            event.target.reset();
        } else {
            showError(data.message || 'Failed to join order');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to join order');
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
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load menu items');
        }

        const menuContainer = document.getElementById('menu-categories');
        menuContainer.innerHTML = '';

        // Group items by category
        const categories = {};
        data.menu_items.forEach(item => {
            if (!categories[item.category]) {
                categories[item.category] = [];
            }
            categories[item.category].push(item);
        });

        // Create category sections
        Object.entries(categories).forEach(([category, items]) => {
            const categorySection = document.createElement('div');
            categorySection.className = 'category-section mb-8';
            categorySection.innerHTML = `
                <h2 class="text-2xl font-bold mb-4">${category}</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${items.map(item => `
                        <div class="menu-item bg-white p-4 rounded-lg shadow">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="text-lg font-semibold">${item.name}</h3>
                                    <p class="text-gray-600">${item.description || ''}</p>
                                    <p class="text-lg font-bold text-indigo-600 mt-2">$${item.price.toFixed(2)}</p>
                                </div>
                                <button 
                                    class="add-to-cart-btn bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                                    data-item-name="${item.name}"
                                    data-item-price="${item.price}">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            menuContainer.appendChild(categorySection);
        });
    } catch (error) {
        console.error('Error loading menu items:', error);
        showError('Failed to load menu items');
    }
}

// Cart Management
async function addToCart(itemName, price) {
    if (!currentUser) {
        showError('Please log in first');
        return;
    }

    try {
        const response = await fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_name: itemName,
                price: parseFloat(price)
            })
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            updateCartDisplay(data.cart_items);
            showMessage('Item added to cart');
        } else {
            showError(data.message || 'Failed to add item to cart');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to add item to cart');
    }
}

function updateCartDisplay(cartItems) {
    const cartDiv = document.getElementById('cart-items');
    cartDiv.innerHTML = '';
    
    if (cartItems && cartItems.length > 0) {
        let total = 0;
        
        cartItems.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item flex justify-between items-center p-2 border-b';
            const itemTotal = item.price * item.quantity;
            total += itemTotal;
            
            itemDiv.innerHTML = `
                <div class="item-info flex-1">
                    <span class="font-semibold">${item.name}</span>
                    <div class="quantity-controls flex items-center mt-1">
                        <button onclick="updateQuantity('${item.name}', ${item.quantity - 1})" 
                                class="bg-gray-200 px-2 py-1 rounded hover:bg-gray-300"
                                ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                        <span class="mx-2">${item.quantity}</span>
                        <button onclick="updateQuantity('${item.name}', ${item.quantity + 1})" 
                                class="bg-gray-200 px-2 py-1 rounded hover:bg-gray-300">+</button>
                    </div>
                </div>
                <div class="item-actions flex items-center ml-4">
                    <span class="font-bold mr-4">$${itemTotal.toFixed(2)}</span>
                    <button onclick="removeFromCart('${item.name}')" class="text-red-600 hover:text-red-800">
                        Remove
                    </button>
                </div>
            `;
            cartDiv.appendChild(itemDiv);
        });
        
        const totalDiv = document.getElementById('cart-total');
        if (totalDiv) {
            totalDiv.textContent = `Total: $${total.toFixed(2)}`;
        }
    } else {
        cartDiv.innerHTML = '<p class="text-gray-500 text-center py-4">Your cart is empty</p>';
        const totalDiv = document.getElementById('cart-total');
        if (totalDiv) {
            totalDiv.textContent = 'Total: $0.00';
        }
    }
}

async function updateQuantity(itemName, newQuantity) {
    if (newQuantity < 1) return;
    
    try {
        const response = await fetch('/update_quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_name: itemName,
                quantity: newQuantity
            })
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            updateCartDisplay(data.cart_items);
        } else {
            showError(data.message || 'Failed to update quantity');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to update quantity');
    }
}

async function removeFromCart(itemName) {
    try {
        const response = await fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_name: itemName
            })
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            updateCartDisplay(data.cart_items);
            showMessage('Item removed from cart');
        } else {
            showError(data.message || 'Failed to remove item');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to remove item from cart');
    }
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
            // Clear cart and local state
            cart.clear();
            updateCartDisplay([]);
            showMessage('Successfully left the order');
            
            // Update UI
            document.getElementById('order-name-display').textContent = '';
            document.getElementById('order-pin-display').textContent = '';
            
            // Switch to order options screen
            showScreen('order-options');
            
            // Clear any active order info
            document.getElementById('active-order-info').style.display = 'none';
        } else {
            showError(data.message || 'Failed to leave order');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to leave order');
    }
}

async function generateReceipt() {
    try {
        const response = await fetch('/generate_receipt');
        const data = await response.json();

        if (data.success) {
            const modal = document.getElementById('receipt-modal');
            const content = document.getElementById('receipt-content');
            
            let receiptHtml = `
                <div class="text-center mb-6">
                    <h2 class="text-2xl font-bold mb-2">${data.order_name}</h2>
                    <p class="text-gray-600">PIN: ${data.order_pin}</p>
                </div>
            `;

            // Add each user's order
            Object.values(data.user_orders).forEach(userOrder => {
                receiptHtml += `
                    <div class="mb-6 border-b pb-4">
                        <h3 class="text-xl font-semibold mb-3">${userOrder.name}'s Order</h3>
                        <table class="w-full">
                            <thead>
                                <tr class="text-left">
                                    <th class="pb-2">Item</th>
                                    <th class="pb-2">Qty</th>
                                    <th class="pb-2">Price</th>
                                    <th class="pb-2 text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                userOrder.items.forEach(item => {
                    receiptHtml += `
                        <tr>
                            <td class="py-1">${item.name}</td>
                            <td class="py-1">${item.quantity}</td>
                            <td class="py-1">$${item.price.toFixed(2)}</td>
                            <td class="py-1 text-right">$${item.total.toFixed(2)}</td>
                        </tr>
                    `;
                });

                receiptHtml += `
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" class="pt-2 text-right font-semibold">Subtotal:</td>
                                    <td class="pt-2 text-right font-semibold">$${userOrder.subtotal.toFixed(2)}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            });

            // Add grand total
            receiptHtml += `
                <div class="text-right text-xl font-bold mt-4">
                    Grand Total: $${data.grand_total.toFixed(2)}
                </div>
            `;

            content.innerHTML = receiptHtml;
            modal.style.display = 'block';
        } else {
            showError(data.message || 'Failed to generate receipt');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to generate receipt');
    }
}

function showMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg z-50';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
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
        const addToCartBtn = e.target.closest('.add-to-cart-btn');
        if (addToCartBtn) {
            const itemName = addToCartBtn.dataset.itemName;
            const itemPrice = addToCartBtn.dataset.itemPrice;
            if (itemName && itemPrice) {
                addToCart(itemName, parseFloat(itemPrice));
            }
        }
    });
    
    // Generate receipt button
    document.getElementById('generate-receipt-btn')?.addEventListener('click', generateReceipt);
    
    // Logout buttons
    const logoutBtnOptions = document.getElementById('logout-btn-options');
    const logoutBtnActive = document.getElementById('logout-btn-active');
    
    if (logoutBtnOptions) {
        logoutBtnOptions.addEventListener('click', logout);
    }
    if (logoutBtnActive) {
        logoutBtnActive.addEventListener('click', logout);
    }
    
    // Leave order button
    const leaveOrderBtn = document.getElementById('leave-order-btn');
    if (leaveOrderBtn) {
        leaveOrderBtn.addEventListener('click', leaveOrder);
    }
});
