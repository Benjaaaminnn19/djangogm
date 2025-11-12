  document.querySelectorAll('a.nav-link[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const destino = document.querySelector(link.getAttribute('href'));
      if (destino) destino.scrollIntoView({ behavior: 'smooth' });
    });
  });



  document.querySelectorAll('a[href="tienda.html"]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      document.body.classList.add('fade-out');
      setTimeout(() => {
        window.location.href = this.href;
      }, 500); // tiempo igual al de la animación
    });
  });

        // Función para abrir el modal de agendar clase
        function abrirModalClase(nombreClase) {
            document.getElementById('nombreClase').value = nombreClase;
            
            // Establecer fecha mínima como hoy
            const hoy = new Date().toISOString().split('T')[0];
            document.getElementById('fechaClase').min = hoy;
            
            // Limpiar formulario
            document.getElementById('formAgendarClase').reset();
            document.getElementById('nombreClase').value = nombreClase;
            
            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalAgendarClase'));
            modal.show();
        }

        // Función para enviar la solicitud de clase
        function enviarSolicitudClase() {
            const form = document.getElementById('formAgendarClase');
            const formData = new FormData(form);
            
            // Validar formulario
            if (!form.checkValidity()) {
                form.classList.add('was-validated');
                return;
            }

            // Recopilar datos
            const datosClase = {
                clase: document.getElementById('nombreClase').value,
                fecha: document.getElementById('fechaClase').value,
                hora: document.getElementById('horaClase').value,
                plan: document.getElementById('planCliente').value,
                nombre: document.getElementById('nombreCliente').value,
                telefono: document.getElementById('telefonoCliente').value,
                email: document.getElementById('emailCliente').value,
                comentarios: document.getElementById('comentariosClase').value
            };

            // Simular envío (aquí podrías integrar con tu backend)
            console.log('Solicitud de clase:', datosClase);
            
            // Mostrar mensaje de confirmación
            alert('¡Solicitud enviada exitosamente!\n\nTe contactaremos pronto para confirmar tu reserva.\n\nGracias por elegir Leblon Fitness.');
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalAgendarClase'));
            modal.hide();
            
            // Limpiar formulario
            form.reset();
        }

        // Configurar fecha mínima cuando se abre el modal
        document.addEventListener('DOMContentLoaded', function() {
            const fechaInput = document.getElementById('fechaClase');
            if (fechaInput) {
                const hoy = new Date().toISOString().split('T')[0];
                fechaInput.min = hoy;
            }

            // Animaciones de scroll
            initScrollAnimations();
            
            // Efectos dinámicos adicionales
            initDynamicEffects();
        });

        // Función para animaciones de scroll
        function initScrollAnimations() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                    }
                });
            }, observerOptions);

            // Observar elementos con animación de scroll
            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                observer.observe(el);
            });
        }

        // Efectos dinámicos adicionales
        function initDynamicEffects() {
            // Efecto parallax en el header
            window.addEventListener('scroll', () => {
              const scrolled = window.pageYOffset;
              const header = document.querySelector('.spartan-hero-section');
              if (header) {
                header.style.backgroundPositionY = `${scrolled * 0.4}px`;
              }
            });

            // Scroll-based color change effect
            initScrollColorChange();
        }

        // Función para el efecto de cambio de color basado en scroll
        function initScrollColorChange() {
    // Colores de transición inspirados en el logo de Leblon Calama
            const colorConfig = {
        // Parte superior (inicio) - tonos cálidos naranjas
            start: {
                background: '#fff6e5',             // Fondo cálido claro
                navbar: 'rgba(255, 102, 0, 0.9)',  // Naranja brillante
                text: '#cc5200',                   // Naranja oscuro
                primary: '#ff6600',                // Naranja principal
                secondary: '#ff944d',              // Naranja suave
                accent: '#ffb366'                  // Detalle más claro
            },
        // Mitad del scroll - transición con blanco y turquesa
            middle: {
                background: '#f0fffb',             // Blanco con leve verde agua
                navbar: 'rgba(0, 179, 161, 0.9)',  // Turquesa fuerte
                text: '#009688',                   // Verde agua medio
                primary: '#00b3a1',                // Color principal del logo
                secondary: '#40c9ba',              // Más claro
                accent: '#80e0d4'                  // Suave y luminoso
            },
        // Final (abajo) - tonos más oscuros, elegantes
            end: {
                background: '#e6fdf9',             // Verde agua muy claro
                navbar: 'rgba(0, 90, 81, 0.9)',    // Turquesa oscuro / profundidad
                text: '#004d47',                   // Texto profundo
                primary: '#00796b',                // Verde azulado oscuro
                secondary: '#00695c',              // Complementario
                accent: '#00bfa5'                  // Toque final brillante
            }
        };

    // Aquí puedes seguir tu lógica de scroll, aplicando estos colores dinámicamente
        


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

                // Aplicar cambios de color
                applyColorChanges(currentColors);
            }, 8); // Aumentar a ~120fps para más fluidez

            // Función para aplicar los cambios de color - MÁS EXTENSIVA
            function applyColorChanges(colors) {
                // Cambiar color de fondo del body con transición suave
                document.body.style.backgroundColor = colors.background;
                document.body.style.transition = 'background-color 0.3s ease';

                // Cambiar color de fondo de secciones bg-light
                document.querySelectorAll('.bg-light').forEach(section => {
                    section.style.backgroundColor = colors.background + ' !important';
                    section.style.transition = 'background-color 0.3s ease';
                });

                // Cambiar color de fondo de secciones py-5
                document.querySelectorAll('section.py-5').forEach(section => {
                    section.style.backgroundColor = colors.background + ' !important';
                    section.style.transition = 'background-color 0.3s ease';
                });

                // Cambiar color del navbar con efecto suave
                const navbar = document.querySelector('.modern-navbar');
                if (navbar) {
                    navbar.style.background = colors.navbar;
                    navbar.style.transition = 'background 0.5s ease';
                    navbar.style.boxShadow = `0 2px 10px ${colors.primary}20`;
                }

                // Cambiar colores de texto en títulos principales
                document.querySelectorAll('h1, h2, h3, .section-title').forEach(title => {
                    title.style.color = colors.text;
                    title.style.transition = 'color 0.5s ease';
                    title.style.textShadow = `1px 1px 2px ${colors.primary}15`;
                });

                // Cambiar colores de botones primarios con gradientes suaves
                document.querySelectorAll('.btn-primary').forEach(btn => {
                    btn.style.background = colors.primary;
                    btn.style.borderColor = colors.secondary;
                    btn.style.boxShadow = `0 2px 8px ${colors.primary}30`;
                    btn.style.transition = 'all 0.5s ease';
                });

                // Cambiar colores de botones outline
                document.querySelectorAll('.btn-outline-primary').forEach(btn => {
                    btn.style.borderColor = colors.primary;
                    btn.style.color = colors.primary;
                    btn.style.boxShadow = `0 1px 4px ${colors.primary}20`;
                    btn.style.transition = 'all 0.5s ease';
                });

                // Cambiar colores de iconos principales con efectos suaves
                document.querySelectorAll('.feature-icon, .fas.fa-dumbbell').forEach(icon => {
                    icon.style.color = colors.primary;
                    icon.style.textShadow = `0 0 5px ${colors.accent}20`;
                    icon.style.transition = 'all 0.5s ease';
                });

                // Efecto especial en cards de productos suave
                document.querySelectorAll('.producto-promo').forEach(card => {
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

                // EFECTOS SUAVES Y ELEGANTES:
                
                // Cambiar color de las cards de planes
                document.querySelectorAll('.plan-card').forEach(card => {
                    card.style.boxShadow = `0 5px 15px ${colors.primary}20`;
                    card.style.transition = 'box-shadow 0.5s ease';
                });

                // Cambiar color de los headers de planes
                document.querySelectorAll('.plan-card .card-header').forEach(header => {
                    header.style.background = colors.primary;
                    header.style.transition = 'background 0.5s ease';
                });

                // Cambiar color del botón de WhatsApp
                const whatsappBtn = document.querySelector('.whatsapp-float');
                if (whatsappBtn) {
                    whatsappBtn.style.background = colors.primary;
                    whatsappBtn.style.boxShadow = `0 2px 10px ${colors.primary}30`;
                    whatsappBtn.style.transition = 'all 0.5s ease';
                }

                // Efecto suave en las tablas
                document.querySelectorAll('table thead').forEach(thead => {
                    thead.style.background = colors.primary;
                    thead.style.transition = 'background 0.5s ease';
                });

                // Cambiar color de los modales
                document.querySelectorAll('.modal-header').forEach(header => {
                    header.style.background = colors.primary;
                    header.style.transition = 'background 0.5s ease';
                });

                // NUEVOS EFECTOS PARA LA SECCIÓN DE CONTACTO:
                
                // Cambiar color de los iconos de contacto
                document.querySelectorAll('.contact-icon').forEach(icon => {
                    icon.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`;
                    icon.style.transition = 'background 0.5s ease';
                });

                // Cambiar color del header del formulario de contacto
                document.querySelectorAll('#contacto .card-header').forEach(header => {
                    header.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`;
                    header.style.transition = 'background 0.5s ease';
                });

                // Cambiar color de los botones en la sección de contacto
                document.querySelectorAll('#contacto .btn').forEach(btn => {
                    if (btn.classList.contains('btn-primary')) {
                        btn.style.background = colors.primary;
                        btn.style.borderColor = colors.secondary;
                        btn.style.transition = 'all 0.5s ease';
                    }
                    if (btn.classList.contains('btn-success')) {
                        btn.style.background = colors.accent;
                        btn.style.borderColor = colors.accent;
                        btn.style.transition = 'all 0.5s ease';
                    }
                });

                // Cambiar color del alert final
                const contactAlert = document.querySelector('#contacto .alert');
                if (contactAlert) {
                    contactAlert.style.background = `linear-gradient(135deg, ${colors.primary}20, ${colors.secondary}20)`;
                    contactAlert.style.transition = 'background 0.5s ease';
                }
            }

            // Agregar event listener para scroll
            window.addEventListener('scroll', handleScrollColorChange);

            // Aplicar colores iniciales
            handleScrollColorChange();
        }

            // Efecto de rotación en iconos al hacer hover
            document.querySelectorAll('.fas').forEach(icon => {
                icon.addEventListener('mouseenter', () => {
                    icon.style.animation = 'rotate 0.5s ease-in-out';
                });
                icon.addEventListener('animationend', () => {
                    icon.style.animation = '';
                });
            });

            // Efecto de pulso en botones
            document.querySelectorAll('.btn').forEach(btn => {
                btn.addEventListener('mouseenter', () => {
                    btn.style.animation = 'pulse 0.5s ease-in-out';
                });
                btn.addEventListener('mouseleave', () => {
                    btn.style.animation = '';
                });
            });

            // Efecto de glow en títulos
            document.querySelectorAll('h1, h2, h3').forEach(title => {
                title.addEventListener('mouseenter', () => {
                    title.classList.add('animate-text-glow');
                });
                title.addEventListener('mouseleave', () => {
                    title.classList.remove('animate-text-glow');
                });
            });
        
// Función para mostrar notificaciones personalizadas
        function mostrarNotificacion(mensaje, tipo = 'success') {
            const container = document.getElementById('notificationContainer');
            const notification = document.createElement('div');
            
            const bgColor = tipo === 'success' ? '#28a745' : '#dc3545';
            const icon = tipo === 'success' ? '✓' : '✗';
            
            notification.style.cssText = `
                background: ${bgColor};
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                margin-bottom: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(100%);
                transition: transform 0.3s ease;
                max-width: 350px;
                font-weight: 500;
            `;
            
            notification.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 10px; font-size: 1.2rem;">${icon}</span>
                    <span>${mensaje}</span>
                </div>
            `;
            
            container.appendChild(notification);
            
            // Animar entrada
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // Remover después de 5 segundos
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 5000);
        }

        // Función para enviar registro de lead
        async function enviarRegistroLead(event) {
            event.preventDefault();
            
            const nombre = document.getElementById('nombreLead').value.trim();
            const email = document.getElementById('emailLead').value.trim();
            
            if (!nombre || !email) {
                mostrarNotificacion('Por favor completa todos los campos', 'error');
                return;
            }
            
            if (!email.includes('@')) {
                mostrarNotificacion('Por favor ingresa un email válido', 'error');
                return;
            }
            
            try {
                const response = await fetch('/registrar-lead/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({
                        nombre: nombre,
                        email: email
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarNotificacion(data.message, 'success');
                    // Cerrar popup después de 2 segundos
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('popupRegistro'));
                        if (modal) {
                            modal.hide();
                        }
                    }, 2000);
                } else {
                    mostrarNotificacion(data.message, 'error');
                }
                
            } catch (error) {
                console.error('Error:', error);
                mostrarNotificacion('Error al enviar el registro. Intenta nuevamente.', 'error');
            }
        }

        // Mostrar popup después de 3 segundos de cargar la página
        document.addEventListener('DOMContentLoaded', function() {
            // Verificar si ya se mostró el popup en esta sesión
            const popupMostrado = sessionStorage.getItem('popupRegistroMostrado');
            
            if (!popupMostrado) {
                setTimeout(() => {
                    const popup = new bootstrap.Modal(document.getElementById('popupRegistro'));
                    popup.show();
                    sessionStorage.setItem('popupRegistroMostrado', 'true');
                }, 3000);
            }
            
            // Configurar formulario
            document.getElementById('formRegistroLead').addEventListener('submit', enviarRegistroLead);
            
            // Configurar formulario de contacto
            configurarFormularioContacto();
        });
        
        // Funcionalidad del Formulario de Contacto
        function configurarFormularioContacto() {
            const contactForm = document.getElementById('contactForm');
            
            if (contactForm) {
                contactForm.addEventListener('submit', function(event) {
                    event.preventDefault();
                    
                    // Validar formulario
                    if (!contactForm.checkValidity()) {
                        event.stopPropagation();
                        contactForm.classList.add('was-validated');
                        return;
                    }
                    
                    // Mostrar spinner
                    const submitBtn = contactForm.querySelector('button[type="submit"]');
                    const originalText = submitBtn.innerHTML;
                    
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviando... <span class="spinner-border spinner-border-sm ms-2" role="status"></span>';
                    
                    // Simular envío (aquí podrías integrar con tu backend)
                    setTimeout(() => {
                        // Mostrar mensaje de éxito
                        mostrarNotificacion('¡Mensaje enviado exitosamente! Te contactaremos pronto.', 'success');
                        
                        // Restaurar botón
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                        
                        // Limpiar formulario
                        contactForm.reset();
                        contactForm.classList.remove('was-validated');
                        
                        // Preparar mensaje para WhatsApp
                        const nombre = document.getElementById('nombre').value;
                        const telefono = document.getElementById('telefono').value;
                        const email = document.getElementById('email').value;
                        const asunto = document.getElementById('asunto').value;
                        const mensaje = document.getElementById('mensaje').value;
                        
                        const mensajeWhatsApp = `Hola! Me contacto desde la web del gimnasio:

*Nombre:* ${nombre}
*Teléfono:* ${telefono}
*Email:* ${email}
*Asunto:* ${asunto}

*Mensaje:* ${mensaje}

¡Espero su respuesta pronto!`;
                        
                        // Mostrar opción de WhatsApp
                        if (confirm('¿Te gustaría también enviar el mensaje por WhatsApp para una respuesta más rápida?')) {
                            window.open(`https://wa.me/56949531978?text=${encodeURIComponent(mensajeWhatsApp)}`, '_blank');
                        }
                        
                    }, 2000);
                });
            }
            
            // Animaciones de scroll para la sección de contacto
            const contactSection = document.getElementById('contacto');
            if (contactSection) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            // Activar animaciones
                            const containers = entry.target.querySelectorAll('.contact-form-container, .contact-info-container');
                            containers.forEach((container, index) => {
                                setTimeout(() => {
                                    container.style.animationPlayState = 'running';
                                }, index * 200);
                            });
                        }
                    });
                }, { threshold: 0.1 });
                
                observer.observe(contactSection);
            }
            
            // Efectos hover mejorados para las cards de contacto
            const contactCards = document.querySelectorAll('#contacto .card');
            contactCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
        }

        // Funciones para el modal de compra de plan
        function abrirModalPlan(nombrePlan, mensualidad, matricula) {
            // Establecer valores en el modal
            document.getElementById('planSeleccionado').value = nombrePlan;
            document.getElementById('planNombreModal').textContent = nombrePlan;
            document.getElementById('planMensualidad').textContent = '$' + mensualidad.toLocaleString('es-CL');
            document.getElementById('planMatricula').textContent = '$' + matricula.toLocaleString('es-CL');
            
            const total = mensualidad + matricula;
            document.getElementById('planTotal').textContent = '$' + total.toLocaleString('es-CL');
            
            // Limpiar formulario
            document.getElementById('formComprarPlan').reset();
            document.getElementById('planSeleccionado').value = nombrePlan;
            
            // Remover validación previa
            document.getElementById('formComprarPlan').classList.remove('was-validated');
        }

        async function enviarSolicitudPlan() {
            const form = document.getElementById('formComprarPlan');
            
            // Validar formulario
            if (!form.checkValidity()) {
                form.classList.add('was-validated');
                return;
            }
            
            // Recopilar datos
            const datosPlan = {
                plan: document.getElementById('planSeleccionado').value,
                nombre: document.getElementById('nombrePlan').value.trim(),
                telefono: document.getElementById('telefonoPlan').value.trim(),
                email: document.getElementById('emailPlan').value.trim(),
                mensaje: document.getElementById('mensajePlan').value.trim()
            };
            
            // Botón de envío
            const btnEnviar = document.querySelector('#modalComprarPlan .btn-primary');
            const textoOriginal = btnEnviar.innerHTML;
            btnEnviar.disabled = true;
            btnEnviar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            
            try {
                const response = await fetch('/comprar-plan/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(datosPlan)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarNotificacion(data.message, 'success');
                    // Cerrar modal después de 3 segundos
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalComprarPlan'));
                        if (modal) {
                            modal.hide();
                        }
                        form.reset();
                        form.classList.remove('was-validated');
                    }, 3000);
                } else {
                    mostrarNotificacion(data.message, 'error');
                    btnEnviar.disabled = false;
                    btnEnviar.innerHTML = textoOriginal;
                }
                
            } catch (error) {
                console.error('Error:', error);
                mostrarNotificacion('Error al enviar la solicitud. Intenta nuevamente.', 'error');
                btnEnviar.disabled = false;
                btnEnviar.innerHTML = textoOriginal;
            }
        }

        // Función auxiliar para obtener el token CSRF
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
     