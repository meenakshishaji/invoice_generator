// static/js/script.js

// Function to toggle password visibility
function togglePassword() {
  const passwordField = document.getElementById("id_password");
  const icon = document.querySelector(".input-group-text i");

  if (passwordField.type === "password") {
    passwordField.type = "text";
    icon.classList.remove("bi-eye");
    icon.classList.add("bi-eye-slash");
  } else {
    passwordField.type = "password";
    icon.classList.remove("bi-eye-slash");
    icon.classList.add("bi-eye");
  }
}



//-------------------dashboard---------//

// Add this to your existing script.js file

// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Calculate invoice totals
function calculateInvoiceTotal() {
    // Get all invoice items
    const rows = document.querySelectorAll('.invoice-item-row');
    let subtotal = 0;
    
    // Calculate each row amount and subtotal
    rows.forEach(row => {
        const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
        const rate = parseFloat(row.querySelector('.item-rate').value) || 0;
        const amount = quantity * rate;
        
        // Update amount field
        row.querySelector('.item-amount').textContent = '$' + amount.toFixed(2);
        
        // Add to subtotal
        subtotal += amount;
    });
    
    // Update subtotal field
    document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
    
    // Get tax, shipping, and discount
    const tax = parseFloat(document.getElementById('id_tax').value) || 0;
    const shipping = parseFloat(document.getElementById('id_shipping').value) || 0;
    const discount = parseFloat(document.getElementById('id_discount').value) || 0;
    
    // Calculate total
    const total = subtotal + tax + shipping - discount;
    document.getElementById('total').textContent = '$' + total.toFixed(2);
    
    // Calculate balance due
    const amountPaid = parseFloat(document.getElementById('id_amount_paid').value) || 0;
    const balanceDue = total - amountPaid;
    document.getElementById('balance-due').textContent = '$' + balanceDue.toFixed(2);
}

// Add invoice item row
function addInvoiceItemRow() {
    // Clone the last row
    const lastRow = document.querySelector('.invoice-item-row:last-child');
    const newRow = lastRow.cloneNode(true);
    
    // Clear the input values
    newRow.querySelectorAll('input').forEach(input => {
        input.value = '';
    });
    
    // Reset the amount display
    newRow.querySelector('.item-amount').textContent = '$0.00';
    
    // Add the new row to the table
    document.querySelector('#invoice-items-table tbody').appendChild(newRow);
    
    // Update the form management
    updateFormsetManagement();
    
    // Recalculate totals
    calculateInvoiceTotal();
}

// Update formset management fields when adding/removing rows
function updateFormsetManagement() {
    const totalForms = document.querySelector('.invoice-item-row').length;
    document.querySelector('#id_items-TOTAL_FORMS').value = totalForms;
}

// Add event listeners when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add invoice item button
    const addItemButton = document.querySelector('#add-line-item');
    if (addItemButton) {
        addItemButton.addEventListener('click', addInvoiceItemRow);
    }
    
    // Calculate totals on input changes
    document.querySelectorAll('.invoice-item-row input, #id_tax, #id_shipping, #id_discount, #id_amount_paid')
        .forEach(input => {
            input.addEventListener('change', calculateInvoiceTotal);
            input.addEventListener('keyup', calculateInvoiceTotal);
        });
    
    // Initial calculation
    calculateInvoiceTotal();
});