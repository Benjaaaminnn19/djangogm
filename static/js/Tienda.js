
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
        });
        
        // Variable global para el carrito
        let carrito = [];

        // Función para agregar al carrito
        function agregarAlCarrito(nombre) {
            // Buscar el producto en la lista de productos
            const producto = encontrarProducto(nombre);
            if (producto) {
                // Verificar si ya existe en el carrito
                const productoExistente = carrito.find(item => item.nombre === nombre);
                if (productoExistente) {
                    productoExistente.cantidad += 1;
                } else {
                    carrito.push({
                        nombre: producto.nombre,
                        precio: producto.precio,
                        imagen: producto.imagen,
                        cantidad: 1
                    });
                }
                
                // Mostrar notificación personalizada
                mostrarNotificacion(nombre);
                
                // Actualizar contador del carrito
                actualizarCarrito();
                
                console.log('Producto agregado:', nombre);
            }
        }

        function encontrarProducto(nombre) {
            // Buscar el producto en los elementos del DOM
            const productos = document.querySelectorAll('.producto-item');
            for (let producto of productos) {
                const nombreProducto = producto.querySelector('.producto-nombre').textContent;
                if (nombreProducto === nombre) {
                    const precio = producto.querySelector('.producto-precio').textContent.replace('$', '');
                    const imagen = producto.querySelector('.producto-imagen').src;
                    return {
                        nombre: nombreProducto,
                        precio: parseFloat(precio),
                        imagen: imagen
                    };
                }
            }
            return null;
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
            const contador = document.getElementById('carrito-contador');
            const totalProductos = carrito.reduce((total, item) => total + item.cantidad, 0);
            contador.textContent = totalProductos;
            contador.style.display = totalProductos > 0 ? 'block' : 'none';
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
                html += `
                    <div class="carrito-item">
                        <img src="${item.imagen}" alt="${item.nombre}" class="carrito-item-img">
                        <div class="carrito-item-info">
                            <div class="carrito-item-nombre">${item.nombre}</div>
                            <div class="carrito-item-precio">$${item.precio.toLocaleString()}</div>
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
            return carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0).toLocaleString();
        }

        function cambiarCantidad(index, cambio) {
            carrito[index].cantidad += cambio;
            if (carrito[index].cantidad <= 0) {
                carrito.splice(index, 1);
            }
            actualizarCarrito();
            // Actualizar el modal si está abierto
            const modal = document.querySelector('.carrito-modal-overlay');
            if (modal) {
                mostrarCarritoModal();
                modal.remove();
            }
        }

        function eliminarProducto(index) {
            carrito.splice(index, 1);
            actualizarCarrito();
            // Actualizar el modal si está abierto
            const modal = document.querySelector('.carrito-modal-overlay');
            if (modal) {
                mostrarCarritoModal();
                modal.remove();
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
            alert('¡Redirigiendo al proceso de pago!');
        }


    
   
        // Función para el efecto de cambio de color basado en scroll en la tienda
        function initScrollColorChangeTienda() {
            // Configuración de colores para la transición - SUAVES Y ELEGANTES
            const colorConfig = {
                // Colores iniciales (top) - GRIS CLARO CON TONOS CÁLIDOS
                start: {
                    background: '#f8f9fa',
                    navbar: 'rgba(139, 69, 19, 0.9)',
                    text: '#6c757d',
                    primary: '#8B4513',
                    secondary: '#A0522D',
                    accent: '#D2691E'
                },
                // Colores intermedios (middle) - AZUL SUAVE
                middle: {
                    background: '#f0f8ff',
                    navbar: 'rgba(70, 130, 180, 0.9)',
                    text: '#4682B4',
                    primary: '#4682B4',
                    secondary: '#5F9EA0',
                    accent: '#87CEEB'
                },
                // Colores finales (bottom) - VERDE SUAVE
                end: {
                    background: '#f0fff0',
                    navbar: 'rgba(34, 139, 34, 0.9)',
                    text: '#228B22',
                    primary: '#228B22',
                    secondary: '#32CD32',
                    accent: '#90EE90'
                }
            };

            // Función para interpolar entre colores
            function interpolateColor(color1, color2, factor) {
                // Convertir colores hex a RGB
                function hexToRgb(hex) {
                    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                    return result ? {
                        r: parseInt(result[1], 16),
                        g: parseInt(result[2], 16),
                        b: parseInt(result[3], 16)
                    } : null;
                }

                // Convertir RGB a hex
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

            // Función para interpolar colores rgba
            function interpolateRgbaColor(color1, color2, factor) {
                // Extraer valores rgba de las cadenas
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

            // Throttle function para optimizar rendimiento
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

            // Función principal del efecto de scroll - MÁS SENSIBLE
            const handleScrollColorChange = throttle(() => {
                const scrollTop = window.pageYOffset;
                const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
                // Hacer el efecto más sensible - empezar más temprano
                const scrollProgress = Math.min(scrollTop / (documentHeight * 0.8), 1);

                // Determinar qué fase de color estamos en con transiciones más bruscas
                let currentColors;
                if (scrollProgress < 0.4) {
                    // Primera fase: transición de start a middle (más rápida)
                    const factor = Math.pow(scrollProgress / 0.4, 0.7); // Curva más pronunciada
                    currentColors = {
                        background: interpolateColor(colorConfig.start.background, colorConfig.middle.background, factor),
                        navbar: interpolateRgbaColor(colorConfig.start.navbar, colorConfig.middle.navbar, factor),
                        text: interpolateColor(colorConfig.start.text, colorConfig.middle.text, factor),
                        primary: interpolateColor(colorConfig.start.primary, colorConfig.middle.primary, factor),
                        secondary: interpolateColor(colorConfig.start.secondary, colorConfig.middle.secondary, factor),
                        accent: interpolateColor(colorConfig.start.accent, colorConfig.middle.accent, factor)
                    };
                } else {
                    // Segunda fase: transición de middle a end (más rápida)
                    const factor = Math.pow((scrollProgress - 0.4) / 0.6, 0.7); // Curva más pronunciada
                    currentColors = {
                        background: interpolateColor(colorConfig.middle.background, colorConfig.end.background, factor),
                        navbar: interpolateRgbaColor(colorConfig.middle.navbar, colorConfig.end.navbar, factor),
                        text: interpolateColor(colorConfig.middle.text, colorConfig.end.text, factor),
                        primary: interpolateColor(colorConfig.middle.primary, colorConfig.end.primary, factor),
                        secondary: interpolateColor(colorConfig.middle.secondary, colorConfig.end.secondary, factor),
                        accent: interpolateColor(colorConfig.middle.accent, colorConfig.end.accent, factor)
                    };
                }

                // Aplicar cambios de color específicos para la tienda
                applyColorChangesTienda(currentColors);
            }, 8); // Aumentar a ~120fps para más fluidez

            // Función para aplicar los cambios de color específicos de la tienda
            function applyColorChangesTienda(colors) {
                // Cambiar color de fondo del body con transición suave
                document.body.style.backgroundColor = colors.background;
                document.body.style.transition = 'background-color 0.3s ease';

                // Cambiar color del navbar de la tienda
                const navbar = document.querySelector('.navbar-custom');
                if (navbar) {
                    navbar.style.background = colors.navbar;
                    navbar.style.transition = 'background 0.5s ease';
                    navbar.style.boxShadow = `0 2px 10px ${colors.primary}20`;
                    navbar.style.borderBottom = `2px solid ${colors.accent}`;
                }

                // Cambiar colores de texto en títulos principales
                document.querySelectorAll('h1, h2, h3, .header-badge').forEach(title => {
                    title.style.color = colors.text;
                    title.style.transition = 'color 0.5s ease';
                    title.style.textShadow = `1px 1px 2px ${colors.primary}15`;
                });

                // Cambiar colores de botones primarios con gradientes suaves
                document.querySelectorAll('.btn-primary, .btn-success').forEach(btn => {
                    btn.style.background = colors.primary;
                    btn.style.borderColor = colors.secondary;
                    btn.style.boxShadow = `0 2px 8px ${colors.primary}30`;
                    btn.style.transition = 'all 0.5s ease';
                });

                // Cambiar colores de botones outline
                document.querySelectorAll('.btn-outline-primary, .btn-outline-secondary').forEach(btn => {
                    btn.style.borderColor = colors.primary;
                    btn.style.color = colors.primary;
                    btn.style.boxShadow = `0 1px 4px ${colors.primary}20`;
                    btn.style.transition = 'all 0.5s ease';
                });

                // Cambiar colores de iconos principales con efectos suaves
                document.querySelectorAll('.fas, .fa').forEach(icon => {
                    icon.style.color = colors.primary;
                    icon.style.textShadow = `0 0 5px ${colors.accent}20`;
                    icon.style.transition = 'all 0.5s ease';
                });

                // Efecto especial en cards de productos suave
                document.querySelectorAll('.producto-card').forEach(card => {
                    card.style.borderLeft = `3px solid ${colors.primary}`;
                    card.style.boxShadow = `0 4px 15px ${colors.primary}15`;
                    card.style.transition = 'all 0.5s ease';
                });

                // Cambiar colores de enlaces de navegación
                document.querySelectorAll('.nav-link').forEach(link => {
                    if (!link.classList.contains('active')) {
                        link.style.color = colors.text + ' !important';
                        link.style.transition = 'color 0.3s ease';
                    }
                });

                // EFECTOS SUAVES ESPECÍFICOS DE LA TIENDA:
                
                // Cambiar color del header badge
                const headerBadge = document.querySelector('.header-badge');
                if (headerBadge) {
                    headerBadge.style.background = colors.primary;
                    headerBadge.style.borderColor = colors.accent;
                    headerBadge.style.transition = 'all 0.5s ease';
                }

                // Cambiar color del carrito flotante
                const carritoFlotante = document.querySelector('.carrito-flotante');
                if (carritoFlotante) {
                    carritoFlotante.style.background = colors.primary;
                    carritoFlotante.style.boxShadow = `0 4px 15px ${colors.primary}30`;
                    carritoFlotante.style.transition = 'all 0.5s ease';
                }

                // Cambiar color de los badges de categoría
                document.querySelectorAll('.badge').forEach(badge => {
                    badge.style.background = colors.accent;
                    badge.style.transition = 'background 0.5s ease';
                });

                // Cambiar color de los precios
                document.querySelectorAll('.precio').forEach(precio => {
                    precio.style.color = colors.primary;
                    precio.style.transition = 'color 0.5s ease';
                });

                // Cambiar color de los filtros
                document.querySelectorAll('.filtro-boton').forEach(filtro => {
                    filtro.style.borderColor = colors.primary;
                    filtro.style.color = colors.primary;
                    filtro.style.transition = 'all 0.5s ease';
                });

                // Efecto suave en las cards de productos con hover
                document.querySelectorAll('.producto-card').forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-5px)';
                        this.style.boxShadow = `0 8px 20px ${colors.primary}25`;
                    });
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = `0 4px 15px ${colors.primary}15`;
                    });
                });
            }

            // Agregar event listener para scroll
            window.addEventListener('scroll', handleScrollColorChange);

            // Aplicar colores iniciales
            handleScrollColorChange();
        }

        // Inicializar el efecto cuando se carga la página
        document.addEventListener('DOMContentLoaded', function() {
            initScrollColorChangeTienda();
            cargarProductosDestacados();
            configurarNewsletter();
            configurarAnimacionesScroll();
        });

        // Cargar productos destacados dinámicamente
        function cargarProductosDestacados() {
            const productosDestacados = document.getElementById('productos-destacados');
            if (!productosDestacados) return;

            // Simular productos destacados (en una app real vendría del backend)
            const productos = [
                {
                    nombre: "Proteína Whey Gold Standard",
                    precio: "45.990",
                    imagen: "{% static 'img/img5.png' %}",
                    categoria: "Suplementos"
                },
                {
                    nombre: "Camiseta Deportiva Premium",
                    precio: "12.990",
                    imagen: "{% static 'img/img6.jpg' %}",
                    categoria: "Ropa"
                },
                {
                    nombre: "Guantes de Gimnasio",
                    precio: "8.990",
                    imagen: "{% static 'img/img7.jpg' %}",
                    categoria: "Accesorios"
                },
                {
                    nombre: "Creatina Monohidrato",
                    precio: "18.990",
                    imagen: "{% static 'img/img5.png' %}",
                    categoria: "Suplementos"
                }
            ];

            productosDestacados.innerHTML = productos.map(producto => `
                <div class="col-lg-3 col-md-6 mb-4">
                    <div class="producto-card animate-fade-in">
                        <img src="${producto.imagen}" alt="${producto.nombre}" class="producto-imagen">
                        <div class="producto-info">
                            <h4 class="producto-nombre">${producto.nombre}</h4>
                            <div class="producto-marca">${producto.categoria}</div>
                            <div class="producto-precio">$${producto.precio}</div>
                            <button class="btn btn-comprar" onclick="agregarAlCarrito('${producto.nombre}')">
                                <i class="fas fa-shopping-cart me-1"></i>AGREGAR
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        // Configurar newsletter
        function configurarNewsletter() {
            const newsletterForm = document.querySelector('.newsletter-form');
            if (!newsletterForm) return;

            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const email = this.querySelector('input[type="email"]').value;
                
                if (email) {
                    mostrarNotificacion('¡Gracias por suscribirte! Te enviaremos las mejores ofertas.', 'success');
                    this.reset();
                }
            });
        }

        // Configurar animaciones de scroll
        function configurarAnimacionesScroll() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.animationPlayState = 'running';
                    }
                });
            }, { threshold: 0.1 });

            // Observar todas las nuevas secciones
            document.querySelectorAll('.categoria-card, .oferta-card, .testimonio-card, .blog-card').forEach(card => {
                observer.observe(card);
            });
        }

        // Función para filtrar por categoría
        function filtrarPorCategoria(categoria) {
            // Activar el checkbox correspondiente
            const checkbox = document.getElementById(`filtro-${categoria}`);
            if (checkbox) {
                checkbox.checked = true;
                aplicarFiltros();
            }
            
            // Scroll hacia los productos
            document.getElementById('productos').scrollIntoView({ behavior: 'smooth' });
        }

        // Función para mostrar notificaciones
        function mostrarNotificacion(mensaje, tipo = 'info') {
            // Crear elemento de notificación
            const notificacion = document.createElement('div');
            notificacion.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
            notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            notificacion.innerHTML = `
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            document.body.appendChild(notificacion);

            // Auto-remover después de 5 segundos
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.parentNode.removeChild(notificacion);
                }
            }, 5000);
        }

