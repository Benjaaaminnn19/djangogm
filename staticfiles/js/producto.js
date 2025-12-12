
        // Cambiar imagen principal
        function changeImage(src) {
            document.getElementById('main-image').src = src;
            
            // Actualizar thumbnails activos
            document.querySelectorAll('.thumbnail').forEach(thumb => {
                thumb.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        // Control de cantidad
        function increaseQuantity() {
            const input = document.getElementById('quantity');
            if (parseInt(input.value) < 10) {
                input.value = parseInt(input.value) + 1;
            }
        }
        
        function decreaseQuantity() {
            const input = document.getElementById('quantity');
            if (parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
            }
        }
        
        // Agregar al carrito
        function addToCart() {
            const quantity = document.getElementById('quantity').value;
            const productName = "{{ producto.nombre }}";
            
            alert(`${productName} agregado al carrito (Cantidad: ${quantity})`);
            
            // Aquí podrías agregar la lógica real del carrito
            console.log('Producto agregado:', {
                id: {{ producto.id }},
                nombre: productName,
                cantidad: quantity,
                precio: {{ producto.precio }}
            });
        }
        
        // Opciones de color y talla
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                // Remover active de todos los botones del mismo grupo
                const group = this.parentElement;
                group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
                
                // Agregar active al botón clickeado
                this.classList.add('active');
            });
        });
