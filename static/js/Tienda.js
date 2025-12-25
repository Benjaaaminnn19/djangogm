/* ============================================================
   TIENDA.JS - LÓGICA UNIFICADA DE CARRITO Y FILTROS
   ============================================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. SELECTORES DE ELEMENTOS
    const productos = document.querySelectorAll('.producto-item');
    const container = document.getElementById('productos-container');
    const sortDropdown = document.getElementById('sortDropdown');

    // 2. FUNCIONALIDAD DE ORDENAMIENTO
    document.querySelectorAll('[data-sort]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const sortType = this.getAttribute('data-sort');
            sortProducts(sortType);
            if (sortDropdown) sortDropdown.textContent = this.textContent;
        });
    });

    function sortProducts(sortType) {
        const productosArray = Array.from(productos);
        productosArray.sort((a, b) => {
            switch(sortType) {
                case 'nombre':
                    return a.getAttribute('data-nombre').localeCompare(b.getAttribute('data-nombre'));
                case 'precio_asc':
                    return parseFloat(a.getAttribute('data-precio')) - parseFloat(b.getAttribute('data-precio'));
                case 'precio_desc':
                    return parseFloat(b.getAttribute('data-precio')) - parseFloat(a.getAttribute('data-precio'));
                case 'categoria':
                    return a.getAttribute('data-categoria').localeCompare(b.getAttribute('data-categoria'));
                default: return 0;
            }
        });
        productosArray.forEach(producto => container.appendChild(producto));
    }

    // 3. ANIMACIONES INICIALES
    const cards = document.querySelectorAll('.producto-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // 4. INICIALIZACIÓN DE COLOR POR SCROLL Y CARRITO
    initScrollColorChangeTienda();
    
    // ESTA LÍNEA ES VITAL: Sincroniza el carrito al entrar a la tienda
    actualizarCarrito();
});

/* ===============================
   GESTIÓN DEL CARRITO (PERSISTENCIA)
   =============================== */

function agregarAlCarrito(nombre, precio, imagen, id) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    // Buscamos por ID (más seguro que por nombre)
    const index = carrito.findIndex(item => item.id == id);
    
    if (index !== -1) {
        carrito[index].cantidad += 1;
    } else {
        carrito.push({
            id: id,
            nombre: nombre,
            precio: precio,
            imagen: imagen,
            cantidad: 1
        });
    }
    
    localStorage.setItem('carrito', JSON.stringify(carrito));
    mostrarNotificacion(nombre);
    actualizarCarrito();
}

function actualizarCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    // Actualizar Contador (Badge de la Navbar)
    const contador = document.getElementById('carrito-contador');
    const totalProductos = carrito.reduce((total, item) => total + item.cantidad, 0);
    
    if (contador) {
        contador.textContent = totalProductos;
        contador.style.display = totalProductos > 0 ? 'block' : 'none';
    }

    // Actualizar Badge secundario (si existe en otras vistas)
    const badgeCarrito = document.getElementById('badge-carrito');
    if (badgeCarrito) {
        badgeCarrito.textContent = totalProductos;
    }

    // Sincronizar el contenido del modal si está abierto
    const listaVisual = document.getElementById('carrito-lista');
    const totalVisual = document.getElementById('carrito-total');
    
    if (listaVisual) listaVisual.innerHTML = generarListaCarrito();
    if (totalVisual) totalVisual.textContent = calcularTotal();
}

function generarListaCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    if (carrito.length === 0) {
        return `
            <div class="carrito-vacio">
                <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                <p class="text-muted">Tu carrito está vacío</p>
            </div>`;
    }

    return carrito.map((item, index) => {
        const precioNumerico = typeof item.precio === 'string' 
            ? parseInt(item.precio.replace(/[$.]/g, '')) 
            : item.precio;
            
        return `
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
            </div>`;
    }).join('');
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
    if (carrito[index].cantidad <= 0) carrito.splice(index, 1);
    
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarCarrito();
    
    // Si la lista está vacía, el modal se actualiza solo por la función actualizarCarrito
}

function eliminarProducto(index) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito.splice(index, 1);
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarCarrito();
}

/* ===============================
   MODALES Y NOTIFICACIONES
   =============================== */

function mostrarNotificacion(nombre) {
    const notificacion = document.createElement('div');
    notificacion.className = 'notificacion-carrito';
    notificacion.innerHTML = `
        <div class="notificacion-contenido">
            <div class="notificacion-icono"><i class="fas fa-check-circle"></i></div>
            <div class="notificacion-texto">
                <strong>¡Producto agregado!</strong><br><small>${nombre}</small>
            </div>
            <button class="notificacion-cerrar" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>`;
    document.body.appendChild(notificacion);
    setTimeout(() => notificacion.classList.add('mostrar'), 100);
    setTimeout(() => {
        notificacion.classList.remove('mostrar');
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}

function mostrarCarritoModal() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const modal = document.createElement('div');
    modal.className = 'carrito-modal-overlay';
    modal.innerHTML = `
        <div class="carrito-modal">
            <div class="carrito-modal-header">
                <h4><i class="fas fa-shopping-cart me-2"></i>Mi Carrito</h4>
                <button class="carrito-cerrar" onclick="cerrarCarritoModal()"><i class="fas fa-times"></i></button>
            </div>
            <div class="carrito-modal-body">
                <div class="carrito-lista" id="carrito-lista">${generarListaCarrito()}</div>
            </div>
            <div class="carrito-modal-footer">
                <div class="carrito-total"><strong>Total: $<span id="carrito-total">${calcularTotal()}</span></strong></div>
                <div class="carrito-botones">
                    <button class="btn btn-secondary" onclick="cerrarCarritoModal()">Seguir Comprando</button>
                    <button class="btn btn-primary" onclick="procederPago()">Proceder al Pago</button>
                </div>
            </div>
        </div>`;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('mostrar'), 100);
}

function cerrarCarritoModal() {
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
        modal.classList.remove('mostrar');
        setTimeout(() => modal.remove(), 300);
    }
}

function verCarrito() {
    mostrarCarritoModal();
}

/* ===============================
   FILTROS DE PRODUCTOS
   =============================== */

function aplicarFiltros() {
    const productos = document.querySelectorAll('.producto-item');
    const categorias = Array.from(document.querySelectorAll('.filtro-opcion input:checked')).map(cb => cb.value);
    const min = parseInt(document.getElementById('precio-min')?.value) || 0;
    const max = parseInt(document.getElementById('precio-max')?.value) || Infinity;

    let visibles = 0;
    productos.forEach(producto => {
        const categoria = producto.dataset.categoria;
        const precio = parseInt(producto.dataset.precio);
        const cumpleCategoria = categorias.length === 0 || categorias.includes(categoria);
        const cumplePrecio = precio >= min && precio <= max;

        if (cumpleCategoria && cumplePrecio) {
            producto.style.display = 'block';
            visibles++;
        } else {
            producto.style.display = 'none';
        }
    });
    actualizarTextoResultados(visibles);
}

function limpiarFiltros() {
    document.querySelectorAll('.filtro-opcion input').forEach(cb => cb.checked = false);
    if(document.getElementById('precio-min')) document.getElementById('precio-min').value = '';
    if(document.getElementById('precio-max')) document.getElementById('precio-max').value = '';
    document.querySelectorAll('.producto-item').forEach(p => p.style.display = 'block');
    actualizarTextoResultados();
}

function actualizarTextoResultados(cantidad = null) {
    const info = document.getElementById('resultados-info');
    if (!info) return;
    const visibles = cantidad !== null ? cantidad : document.querySelectorAll('.producto-item[style="display: block;"]').length;
    info.textContent = `Mostrando ${visibles} producto${visibles !== 1 ? 's' : ''}`;
}

/* ===============================
   EFECTO SCROLL COLOR (RESUMIDO)
   =============================== */

function initScrollColorChangeTienda() {
    const colorConfig = {
        start: { background: '#f8f9fa', navbar: 'rgba(139, 69, 19, 0.9)', primary: '#8B4513' },
        end: { background: '#f0fff0', navbar: 'rgba(34, 139, 34, 0.9)', primary: '#228B22' }
    };

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;
        const factor = Math.min(scrollTop / 1000, 1);
        
        // Cambio básico de fondo para ejemplo
        document.body.style.backgroundColor = factor > 0.5 ? colorConfig.end.background : colorConfig.start.background;
        const navbar = document.querySelector('.navbar-custom');
        if (navbar) navbar.style.background = factor > 0.5 ? colorConfig.end.navbar : colorConfig.start.navbar;
    });
}

// FUNCIONES DE PAGO (STUBS)
function procederPago() {
    cerrarCarritoModal();
    // Aquí llamarías a tu lógica de Checkout existente
    alert("Redirigiendo al pago...");
}