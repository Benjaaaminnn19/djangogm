// Carrito de compras
let carrito = [];

// Cargar carrito desde localStorage al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarCarrito();
    actualizarContadorCarrito();
});

function agregarAlCarrito(nombre, precio, imagen, productoId) {
    // Buscar si el producto ya está en el carrito
    const itemExistente = carrito.find(item => item.id === productoId);
    
    if (itemExistente) {
        itemExistente.cantidad++;
    } else {
        carrito.push({
            id: productoId,
            nombre: nombre,
            precio: precio,
            imagen: imagen,
            cantidad: 1
        });
    }
    
    guardarCarrito();
    actualizarContadorCarrito();
    mostrarNotificacion('Producto agregado al carrito');
}

function eliminarDelCarrito(productoId) {
    carrito = carrito.filter(item => item.id !== productoId);
    guardarCarrito();
    actualizarContadorCarrito();
    mostrarCarrito();
}

function cambiarCantidad(productoId, nuevaCantidad) {
    const item = carrito.find(item => item.id === productoId);
    if (item) {
        item.cantidad = Math.max(1, nuevaCantidad);
        guardarCarrito();
        mostrarCarrito();
    }
}

function calcularTotal() {
    return carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0);
}

function guardarCarrito() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
}

function cargarCarrito() {
    const carritoGuardado = localStorage.getItem('carrito');
    if (carritoGuardado) {
        carrito = JSON.parse(carritoGuardado);
    }
}

function actualizarContadorCarrito() {
    const contador = document.getElementById('carrito-contador');
    if (contador) {
        const totalItems = carrito.reduce((total, item) => total + item.cantidad, 0);
        contador.textContent = totalItems;
    }
}

function formatearPrecio(precio) {
    return '$' + precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function mostrarNotificacion(mensaje) {
    // Crear notificación temporal
    const notif = document.createElement('div');
    notif.className = 'notificacion-carrito';
    notif.textContent = mensaje;
    notif.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 25px;
        border-radius: 5px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.remove();
    }, 2000);
}

function verCarrito() {
    mostrarCarrito();
}

function mostrarCarrito() {
    // Crear modal del carrito
    const modalHTML = `
        <div class="modal fade" id="carritoModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Carrito de Compras</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${carrito.length === 0 ? 
                            '<p class="text-center">El carrito está vacío</p>' : 
                            generarHTMLCarrito()
                        }
                    </div>
                    <div class="modal-footer">
                        <div class="w-100">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5>Total:</h5>
                                <h5>${formatearPrecio(calcularTotal())}</h5>
                            </div>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Seguir Comprando</button>
                            ${carrito.length > 0 ? 
                                '<button type="button" class="btn btn-primary" onclick="procederAlPago()">Proceder al Pago</button>' : 
                                ''
                            }
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Eliminar modal anterior si existe
    const modalExistente = document.getElementById('carritoModal');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('carritoModal'));
    modal.show();
}

function generarHTMLCarrito() {
    return `
        <div class="carrito-items">
            ${carrito.map(item => `
                <div class="carrito-item d-flex align-items-center mb-3 p-3 border rounded">
                    <img src="${item.imagen}" alt="${item.nombre}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;">
                    <div class="flex-grow-1 ms-3">
                        <h6 class="mb-1">${item.nombre}</h6>
                        <p class="mb-1 text-muted">${formatearPrecio(item.precio)}</p>
                        <div class="d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${item.id}, ${item.cantidad - 1})">-</button>
                            <span class="mx-3">${item.cantidad}</span>
                            <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${item.id}, ${item.cantidad + 1})">+</button>
                        </div>
                    </div>
                    <div class="text-end">
                        <p class="mb-2 fw-bold">${formatearPrecio(item.precio * item.cantidad)}</p>
                        <button class="btn btn-sm btn-danger" onclick="eliminarDelCarrito(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function procederAlPago() {
    // Cerrar modal del carrito
    const modal = bootstrap.Modal.getInstance(document.getElementById('carritoModal'));
    modal.hide();
    
    // Mostrar modal de checkout
    mostrarCheckout();
}

function mostrarCheckout() {
    const checkoutHTML = `
        <div class="modal fade" id="checkoutModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Finalizar Compra</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="/tienda/pago/iniciar/" id="formCheckout">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="emailCheckout" class="form-label">Email *</label>
                                <input type="email" class="form-control" id="emailCheckout" name="email" required>
                                <small class="text-muted">Enviaremos la confirmación de tu compra a este email</small>
                            </div>
                            
                            <div class="mb-3">
                                <label for="nombreCheckout" class="form-label">Nombre Completo (Opcional)</label>
                                <input type="text" class="form-control" id="nombreCheckout" name="nombre">
                            </div>
                            
                            <input type="hidden" name="total" value="${calcularTotal()}">
                            <input type="hidden" name="productos" value='${JSON.stringify(carrito)}'>
                            
                            <div class="alert alert-info">
                                <strong>Total a pagar: ${formatearPrecio(calcularTotal())}</strong>
                            </div>
                            
                            <p class="text-muted small">
                                Serás redirigido a Flow para completar el pago de forma segura.
                            </p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-lock me-2"></i>Pagar con Flow
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Eliminar modal anterior si existe
    const modalExistente = document.getElementById('checkoutModal');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', checkoutHTML);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('checkoutModal'));
    modal.show();
    
    // Agregar CSRF token al formulario
    const form = document.getElementById('formCheckout');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken && form) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }
}