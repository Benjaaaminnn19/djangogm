// Funcionalidad de ordenamiento y filtros
document.addEventListener('DOMContentLoaded', function() {
    const productos = document.querySelectorAll('.producto-item');
    const container = document.getElementById('productos-container');
    
    // Funcionalidad de ordenamiento
    document.querySelectorAll('[data-sort]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const sortType = this.getAttribute('data-sort');
            sortProducts(sortType);
            
            // Actualizar texto del dropdown
            document.getElementById('sortDropdown').textContent = this.textContent;
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
                default:
                    return 0;
            }
        });
        
        // Reorganizar productos en el DOM
        productosArray.forEach(producto => {
            container.appendChild(producto);
        });
    }
    
    // Actualizar contador al cargar
    actualizarCarrito();
});

// Función para agregar al carrito
function agregarAlCarrito(nombre, precio, imagen, id) {
    console.log('Agregando al carrito desde Tienda.js:', { nombre, precio, imagen, id });
    
    // Obtener carrito del localStorage
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    // Buscar si el producto ya existe
    const productoExistente = carrito.find(item => item.nombre === nombre);
    
    if (productoExistente) {
        productoExistente.cantidad += 1;
        console.log('Producto existente, cantidad actualizada:', productoExistente.cantidad);
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
    
    // Guardar en localStorage
    localStorage.setItem('carrito', JSON.stringify(carrito));
    console.log('Carrito guardado:', carrito);
    
    // Mostrar notificación personalizada
    mostrarNotificacion(nombre);
    
    // Actualizar contador del carrito
    actualizarCarrito();
}

function mostrarNotificacion(nombre) {
    // Crear notificación personalizada
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
            <button class="notificacion-cerrar" onclick="cerrarNotificacion(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    // Mostrar animación
    setTimeout(() => {
        notificacion.classList.add('mostrar');
    }, 100);
    
    // Auto-cerrar después de 3 segundos
    setTimeout(() => {
        cerrarNotificacion(notificacion.querySelector('.notificacion-cerrar'));
    }, 3000);
}

function cerrarNotificacion(boton) {
    const notificacion = boton.closest('.notificacion-carrito');
    notificacion.classList.remove('mostrar');
    setTimeout(() => {
        notificacion.remove();
    }, 300);
}

function actualizarCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const contador = document.getElementById('carrito-contador');
    const totalProductos = carrito.reduce((total, item) => total + item.cantidad, 0);
    
    if (contador) {
        contador.textContent = totalProductos;
        contador.style.display = totalProductos > 0 ? 'block' : 'none';
    }
    
    console.log('Contador actualizado:', totalProductos);
}

// Animaciones suaves al cargar
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.producto-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}); 

// Función para ver el carrito
function verCarrito() {
    mostrarCarritoModal();
}

function mostrarCarritoModal() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    // Crear modal del carrito
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
    
    // Mostrar animación
    setTimeout(() => {
        modal.classList.add('mostrar');
    }, 100);
}

function generarListaCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
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
        // Asegurarse de que el precio sea un número
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
    actualizarCarrito();
    
    // Actualizar el modal si está abierto
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
    actualizarCarrito();
    
    // Actualizar el modal si está abierto
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
        modal.remove();
        mostrarCarritoModal();
    }
}

function cerrarCarritoModal() {
    const modal = document.querySelector('.carrito-modal-overlay');
    modal.classList.remove('mostrar');
    setTimeout(() => {
        modal.remove();
    }, 300);
}

function procederPago() {
    cerrarCarritoModal();
    mostrarCheckout();
}

function mostrarCheckout() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    
    // Crear modal de checkout
    const modal = document.createElement('div');
    modal.className = 'carrito-modal-overlay';
    modal.innerHTML = `
        <div class="carrito-modal" style="max-width: 500px;">
            <div class="carrito-modal-header">
                <h4><i class="fas fa-lock me-2"></i>Finalizar Compra</h4>
                <button class="carrito-cerrar" onclick="cerrarCheckoutModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <form method="POST" action="/tienda/pago/iniciar/" id="formCheckout">
                <div class="carrito-modal-body">
                    <div class="mb-3">
                        <label for="emailCheckout" class="form-label">Email *</label>
                        <input type="email" class="form-control" id="emailCheckout" name="email" required>
                        <small class="text-muted">Enviaremos la confirmación a este email</small>
                    </div>
                    
                    <div class="mb-3">
                        <label for="nombreCheckout" class="form-label">Nombre Completo</label>
                        <input type="text" class="form-control" id="nombreCheckout" name="nombre">
                    </div>
                    
                    <input type="hidden" name="total" value="${carrito.reduce((total, item) => {
                        const precioNumerico = typeof item.precio === 'string' 
                            ? parseInt(item.precio.replace(/[$.]/g, '')) 
                            : item.precio;
                        return total + (precioNumerico * item.cantidad);
                    }, 0)}">
                    <input type="hidden" name="productos" value='${JSON.stringify(carrito)}'>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Total a pagar: $${calcularTotal()}</strong>
                    </div>
                    
                    <p class="text-muted small">
                        <i class="fas fa-shield-alt me-1"></i>
                        Pago seguro procesado por Flow
                    </p>
                </div>
                <div class="carrito-modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="cerrarCheckoutModal()">Cancelar</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-credit-card me-2"></i>Pagar con Flow
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Obtener CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        const form = modal.querySelector('#formCheckout');
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }
    
    // Mostrar animación
    setTimeout(() => {
        modal.classList.add('mostrar');
    }, 100);
}

function cerrarCheckoutModal() {
    const modal = document.querySelector('.carrito-modal-overlay');
    if (modal) {
        modal.classList.remove('mostrar');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}   

// Función para el efecto de cambio de color basado en scroll en la tienda
function initScrollColorChangeTienda() {
    // Configuración de colores para la transición - SUAVES Y ELEGANTES
    const colorConfig = {
        start: {
            background: '#f8f9fa',
            navbar: 'rgba(139, 69, 19, 0.9)',
            text: '#6c757d',
            primary: '#8B4513',
            secondary: '#A0522D',
            accent: '#D2691E'
        },
        middle: {
            background: '#f0f8ff',
            navbar: 'rgba(70, 130, 180, 0.9)',
            text: '#4682B4',
            primary: '#4682B4',
            secondary: '#5F9EA0',
            accent: '#87CEEB'
        },
        end: {
            background: '#f0fff0',
            navbar: 'rgba(34, 139, 34, 0.9)',
            text: '#228B22',
            primary: '#228B22',
            secondary: '#32CD32',
            accent: '#90EE90'
        }
    };

    function interpolateColor(color1, color2, factor) {
        function hexToRgb(hex) {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        }

        function rgbToHex(r, g, b) {
            return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
        }

        const rgb1 = hexToRgb(color1);
        const rgb2 = hexToRgb(color2);

        if (!rgb1 || !rgb2) return color1;

        const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor);
        const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor);
        const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor);

        return rgbToHex(r, g, b);
    }

    function interpolateRgbaColor(color1, color2, factor) {
        function parseRgba(rgbaString) {
            const match = rgbaString.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
            if (match) {
                return {
                    r: parseInt(match[1]),
                    g: parseInt(match[2]),
                    b: parseInt(match[3]),
                    a: parseFloat(match[4])
                };
            }
            return null;
        }

        const rgba1 = parseRgba(color1);
        const rgba2 = parseRgba(color2);

        if (!rgba1 || !rgba2) return color1;

        const r = Math.round(rgba1.r + (rgba2.r - rgba1.r) * factor);
        const g = Math.round(rgba1.g + (rgba2.g - rgba1.g) * factor);
        const b = Math.round(rgba1.b + (rgba2.b - rgba1.b) * factor);
        const a = rgba1.a + (rgba2.a - rgba1.a) * factor;

        return `rgba(${r}, ${g}, ${b}, ${a})`;
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    const handleScrollColorChange = throttle(() => {
        const scrollTop = window.pageYOffset;
        const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollProgress = Math.min(scrollTop / (documentHeight * 0.8), 1);

        let currentColors;
        if (scrollProgress < 0.4) {
            const factor = Math.pow(scrollProgress / 0.4, 0.7);
            currentColors = {
                background: interpolateColor(colorConfig.start.background, colorConfig.middle.background, factor),
                navbar: interpolateRgbaColor(colorConfig.start.navbar, colorConfig.middle.navbar, factor),
                text: interpolateColor(colorConfig.start.text, colorConfig.middle.text, factor),
                primary: interpolateColor(colorConfig.start.primary, colorConfig.middle.primary, factor),
                secondary: interpolateColor(colorConfig.start.secondary, colorConfig.middle.secondary, factor),
                accent: interpolateColor(colorConfig.start.accent, colorConfig.middle.accent, factor)
            };
        } else {
            const factor = Math.pow((scrollProgress - 0.4) / 0.6, 0.7);
            currentColors = {
                background: interpolateColor(colorConfig.middle.background, colorConfig.end.background, factor),
                navbar: interpolateRgbaColor(colorConfig.middle.navbar, colorConfig.end.navbar, factor),
                text: interpolateColor(colorConfig.middle.text, colorConfig.end.text, factor),
                primary: interpolateColor(colorConfig.middle.primary, colorConfig.end.primary, factor),
                secondary: interpolateColor(colorConfig.middle.secondary, colorConfig.end.secondary, factor),
                accent: interpolateColor(colorConfig.middle.accent, colorConfig.end.accent, factor)
            };
        }

        applyColorChangesTienda(currentColors);
    }, 8);

    function applyColorChangesTienda(colors) {
        document.body.style.backgroundColor = colors.background;
        document.body.style.transition = 'background-color 0.3s ease';

        const navbar = document.querySelector('.navbar-custom');
        if (navbar) {
            navbar.style.background = colors.navbar;
            navbar.style.transition = 'background 0.5s ease';
            navbar.style.boxShadow = `0 2px 10px ${colors.primary}20`;
            navbar.style.borderBottom = `2px solid ${colors.accent}`;
        }

        document.querySelectorAll('h1, h2, h3, .header-badge').forEach(title => {
            title.style.color = colors.text;
            title.style.transition = 'color 0.5s ease';
            title.style.textShadow = `1px 1px 2px ${colors.primary}15`;
        });

        document.querySelectorAll('.btn-primary, .btn-success').forEach(btn => {
            btn.style.background = colors.primary;
            btn.style.borderColor = colors.secondary;
            btn.style.boxShadow = `0 2px 8px ${colors.primary}30`;
            btn.style.transition = 'all 0.5s ease';
        });

        document.querySelectorAll('.producto-card').forEach(card => {
            card.style.borderLeft = `3px solid ${colors.primary}`;
            card.style.boxShadow = `0 4px 15px ${colors.primary}15`;
            card.style.transition = 'all 0.5s ease';
        });

        const carritoFlotante = document.querySelector('.carrito-flotante');
        if (carritoFlotante) {
            carritoFlotante.style.background = colors.primary;
            carritoFlotante.style.boxShadow = `0 4px 15px ${colors.primary}30`;
            carritoFlotante.style.transition = 'all 0.5s ease';
        }
    }

    window.addEventListener('scroll', handleScrollColorChange);
    handleScrollColorChange();
}

// Inicializar el efecto cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    initScrollColorChangeTienda();
});

/* ===============================
   FILTROS DE PRODUCTOS
   =============================== */

function aplicarFiltros() {
    const productos = document.querySelectorAll('.producto-item');
    const categorias = Array.from(
        document.querySelectorAll('.filtro-opcion input:checked')
    ).map(cb => cb.value);

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
    document.querySelectorAll('.filtro-opcion input').forEach(cb => {
        cb.checked = false;
    });

    document.getElementById('precio-min').value = '';
    document.getElementById('precio-max').value = '';

    document.querySelectorAll('.producto-item').forEach(producto => {
        producto.style.display = 'block';
    });

    actualizarTextoResultados();
}

function actualizarTextoResultados(cantidad = null) {
    const info = document.getElementById('resultados-info');
    if (!info) return;

    const productos = document.querySelectorAll('.producto-item');
    const visibles = cantidad !== null
        ? cantidad
        : Array.from(productos).filter(p => p.style.display !== 'none').length;

    info.textContent = `Mostrando ${visibles} producto${visibles !== 1 ? 's' : ''}`;
}