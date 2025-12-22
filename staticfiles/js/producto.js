// ============================================
// SLIDER DE IMÁGENES CON ANIMACIONES
// ============================================

var currentImageIndex = 0;
var images = [];
var thumbnails = [];
var dots = [];
var totalImages = 0;

// Inicializar el slider cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del slider
    images = document.querySelectorAll('.product-image');
    thumbnails = document.querySelectorAll('.thumbnail');
    dots = document.querySelectorAll('.dot');
    totalImages = images.length;
    
    console.log('✅ Slider inicializado');
    console.log('Total de imágenes cargadas:', totalImages);
    
    // Actualizar contador del carrito al cargar
    actualizarContadorCarrito();
});

// Función para cambiar imagen con animación
function changeImage(index, direction = null) {
    if (totalImages === 0 || !images.length) {
        console.error('No hay imágenes disponibles');
        return;
    }

    console.log('Cambiando de imagen', currentImageIndex, 'a', index);

    if (direction === null) {
        direction = index > currentImageIndex ? 'right' : 'left';
    }

    images[currentImageIndex].classList.remove('active', 'slide-in-right', 'slide-in-left');
    if (thumbnails[currentImageIndex]) {
        thumbnails[currentImageIndex].classList.remove('active');
    }
    if (dots[currentImageIndex]) {
        dots[currentImageIndex].classList.remove('active');
    }

    currentImageIndex = index;

    const animationClass = direction === 'right' ? 'slide-in-right' : 'slide-in-left';
    images[currentImageIndex].classList.add('active', animationClass);
    if (thumbnails[currentImageIndex]) {
        thumbnails[currentImageIndex].classList.add('active');
    }
    if (dots[currentImageIndex]) {
        dots[currentImageIndex].classList.add('active');
    }

    setTimeout(() => {
        if (images[currentImageIndex]) {
            images[currentImageIndex].classList.remove('slide-in-right', 'slide-in-left');
        }
    }, 500);
}

function nextImage() {
    if (totalImages === 0) {
        console.error('No hay imágenes para avanzar');
        return;
    }
    const nextIndex = (currentImageIndex + 1) % totalImages;
    changeImage(nextIndex, 'right');
}

function previousImage() {
    if (totalImages === 0) {
        console.error('No hay imágenes para retroceder');
        return;
    }
    const prevIndex = (currentImageIndex - 1 + totalImages) % totalImages;
    changeImage(prevIndex, 'left');
}

// Navegación con teclado
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
        nextImage();
    } else if (e.key === 'ArrowLeft') {
        previousImage();
    }
});

// ============================================
// SISTEMA DE CARRITO (Compatible con Tienda.js)
// ============================================

// Manejar el botón de agregar al carrito
document.addEventListener('DOMContentLoaded', function() {
    const btnAgregar = document.getElementById('btn-agregar-carrito');
    
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productoNombre = this.getAttribute('data-nombre');
            const productoPrecio = parseFloat(this.getAttribute('data-precio'));
            const productoId = parseInt(this.getAttribute('data-id'));
            const productoImagen = this.getAttribute('data-imagen');
            
            console.log('Agregando producto desde detalle:', {
                nombre: productoNombre,
                precio: productoPrecio,
                id: productoId,
                imagen: productoImagen
            });
            
            agregarAlCarritoDetalle(productoNombre, productoPrecio, productoImagen, productoId);
        });
    }
});

function agregarAlCarritoDetalle(nombre, precio, imagen, id) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    console.log('Carrito actual antes de agregar:', carrito);
    
    const productoExistente = carrito.find(item => item.nombre === nombre);
    
    if (productoExistente) {
        productoExistente.cantidad += 1;
        console.log('Producto existente, nueva cantidad:', productoExistente.cantidad);
    } else {
        carrito.push({
            nombre: nombre,
            precio: precio,
            imagen: imagen,
            cantidad: 1,
            id: id
        });
        console.log('Producto nuevo agregado');
    }
    
    localStorage.setItem('carrito', JSON.stringify(carrito));
    console.log('Carrito guardado:', carrito);
    
    actualizarContadorCarrito();
    mostrarNotificacionCarrito(nombre);
}

function actualizarContadorCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    const contador = document.getElementById('carrito-contador');
    
    if (contador) {
        contador.textContent = totalItems;
        contador.style.display = totalItems > 0 ? 'block' : 'none';
        console.log('Contador actualizado:', totalItems);
    }
}

function mostrarNotificacionCarrito(nombre) {
    const notificacion = document.createElement('div');
    notificacion.className = 'notificacion-carrito';
    notificacion.innerHTML = `
        <div class="notificacion-contenido">
            <div class="notificacion-icono">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="notificacion-texto">
                <strong>¡Producto agregado!</strong><br>
                <small>${nombre}</small>
            </div>
            <button class="notificacion-cerrar" onclick="cerrarNotificacionCarrito(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.classList.add('mostrar');
    }, 100);
    
    setTimeout(() => {
        cerrarNotificacionCarrito(notificacion.querySelector('.notificacion-cerrar'));
    }, 3000);
}

function cerrarNotificacionCarrito(boton) {
    const notificacion = boton.closest('.notificacion-carrito');
    if (notificacion) {
    notificacion.classList.remove('mostrar');
    setTimeout(() => {
    notificacion.remove();
    }, 300);
    }
    }

// ============================================
// MODAL DEL CARRITO
// ============================================
function verCarrito() {
    mostrarCarritoModal();
    }
    function mostrarCarritoModal() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const modal = document.createElement('div');
    modal.className = 'carrito-modal-overlay';
    modal.innerHTML = `
        <div class="carrito-modal">
            <div class="carrito-modal-header">
                <h4><i class="fas fa-shopping-cart me-2"></i>Mi Carrito (${carrito.length} productos)</h4>
                <button class="carrito-cerrar" onclick="cerrarCarritoModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="carrito-modal-body">
                <div class="carrito-lista" id="carrito-lista">
                    ${generarListaCarrito()}
                </div>
            </div>
            <div class="carrito-modal-footer">
                <div class="carrito-total">
                    <strong>Total: $<span id="carrito-total">${calcularTotal()}</span></strong>
                </div>
                <div class="carrito-botones">
                    <button class="btn btn-secondary" onclick="cerrarCarritoModal()">Seguir Comprando</button>
                    <button class="btn btn-primary" onclick="procederPago()">Proceder al Pago</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    setTimeout(() => {
        modal.classList.add('mostrar');
    }, 100);
    }
    function generarListaCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    console.log('Generando lista con carrito:', carrito);
    
    if (carrito.length === 0) {
        return `
            <div class="carrito-vacio">
                <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                <p class="text-muted">Tu carrito está vacío</p>
                <small class="text-muted">Agrega algunos productos para comenzar</small>
            </div>
        `;
    }
    
    let html = '';
    carrito.forEach((item, index) => {
        const precioNumerico = typeof item.precio === 'string' 
            ? parseInt(item.precio.replace(/[$.]/g, '')) 
            : item.precio;
            
        html += `
            <div class="carrito-item">
                <img src="${item.imagen}" alt="${item.nombre}" class="carrito-item-img">
                <div class="carrito-item-info">
                    <div class="carrito-item-nombre">${item.nombre}</div>
                    <div class="carrito-item-precio">$${precioNumerico.toLocaleString('es-CL')}</div>
                </div>
                <div class="carrito-item-cantidad">
                    <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${index}, -1)">-</button>
                    <span class="mx-2">${item.cantidad}</span>
                    <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad(${index}, 1)">+</button>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="eliminarProducto(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    return html;
    }
    function calcularTotal() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const total = carrito.reduce((total, item) => {
    const precioNumerico = typeof item.precio === 'string'
    ? parseInt(item.precio.replace(/[$.]/g, ''))
    : item.precio;
    return total + (precioNumerico * item.cantidad);
    }, 0);
    return total.toLocaleString('es-CL');
    }
    function cambiarCantidad(index, cambio) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito[index].cantidad += cambio;
    if (carrito[index].cantidad <= 0) {
        carrito.splice(index, 1);
    }
    
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContadorCarrito();
    
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
        modal.remove();
        mostrarCarritoModal();
    }
    }
    function eliminarProducto(index) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito.splice(index, 1);
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContadorCarrito();
    
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
        modal.remove();
        mostrarCarritoModal();
    }
    }
    function cerrarCarritoModal() {
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
    modal.classList.remove('mostrar');
    setTimeout(() => {
    modal.remove();
    }, 300);
    }
    }
    function procederPago() {
    cerrarCarritoModal();
    window.location.href = '/tienda/pago/iniciar/';
    }
    // ============================================
    // FUNCIONES OPCIONALES
    // ============================================
    function increaseQuantity() {
    const input = document.getElementById('quantity');
    if (input && parseInt(input.value) < 10) {
    input.value = parseInt(input.value) + 1;
    }
    }
    function decreaseQuantity() {
    const input = document.getElementById('quantity');
    if (input && parseInt(input.value) > 1) {
    input.value = parseInt(input.value) - 1;
    }
    }
    document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.option-btn').forEach(btn => {
    btn.addEventListener('click', function() {
    const group = this.parentElement;
    group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    });
    });
    });