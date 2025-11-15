const API_BASE = 'http://localhost:8000';

//registro
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE}/registro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const result = await response.json();
        const resultDiv = document.getElementById('registerResult');
        
        if (response.ok) {
            resultDiv.className = 'success';
            resultDiv.textContent = '¡Registro exitoso! ' + (result.message || '');
        } else {
            resultDiv.className = 'error';
            resultDiv.textContent = 'Error: ' + (result.detail || 'No se pudo completar el registro');
        }
    } catch (error) {
        document.getElementById('registerResult').className = 'error';
        document.getElementById('registerResult').textContent = 'Error de conexión: ' + error.message;
    }
});

// Cargar términos y condiciones
document.getElementById('loadTerms').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/terminos`);
        const data = await response.json();
        document.getElementById('termsContent').innerHTML = `
            <h3 style="color: var(--red); margin-bottom: 20px;">${data.titulo}</h3>
            <div style="color: #333; line-height: 1.8; font-size: 1.1rem;">
                ${data.contenido}
            </div>
           
        `;
    } catch (error) {
        document.getElementById('termsContent').innerHTML = `
            <div style="color: var(--red); font-weight: 700; text-align: center;">
                Error al cargar los términos y condiciones: ${error.message}
            </div>
        `;
    }
});

// Cargar video
function loadVideoContent() {
    document.getElementById('loadVideo').click();
}

document.getElementById('loadVideo').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/video`);
        const data = await response.json();
        document.getElementById('videoContent').innerHTML = `
            <h3 style="color: var(--red); margin-bottom: 15px;">${data.titulo}</h3>
            <p style="color: #333; margin-bottom: 20px; font-size: 1.1rem;">${data.descripcion}</p>
            <video controls width="100%">
                <source src="${data.url}" type="video/mp4">
                Tu navegador no soporta el elemento video.
            </video>
        `;
    } catch (error) {
        document.getElementById('videoContent').innerHTML = `
            <div class="video-placeholder">
                Error al cargar el video: ${error.message}
            </div>
        `;
    }
});

// Cargar instrucciones de instalación
document.getElementById('loadInstall').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/instalacion`);
        const data = await response.json();
        document.getElementById('installContent').innerHTML = `
            <h3 style="color: var(--red); margin-bottom: 20px;">${data.titulo}</h3>
            <div style="color: #333;">
                <h4 style="color: var(--red); margin-bottom: 10px;">Requisitos del Sistema:</h4>
                <p style="margin-bottom: 20px; font-size: 1.1rem;">${data.requisitos}</p>
                
                <h4 style="color: var(--red); margin-bottom: 10px;">Pasos de Instalación:</h4>
                <ol>
                    ${data.pasos.map(paso => `<li style="margin-bottom: 10px; font-size: 1.1rem;">${paso}</li>`).join('')}
                </ol>
                
                ${data.nota ? `<p style="margin-top: 15px; font-style: italic; color: var(--red); font-weight: 700;">${data.nota}</p>` : ''}
            </div>
        `;
    } catch (error) {
        document.getElementById('installContent').innerHTML = `
            <div style="color: var(--red); font-weight: 700; text-align: center;">
                Error al cargar las instrucciones de instalación: ${error.message}
            </div>
        `;
    }
});

// Cargar instrucciones de uso
document.getElementById('loadUsage').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/uso`);
        const data = await response.json();
        document.getElementById('usageContent').innerHTML = `
            <h3 style="color: var(--red); margin-bottom: 20px;">${data.titulo}</h3>
            <p style="color: #333; margin-bottom: 20px; font-size: 1.1rem;">${data.descripcion}</p>
            <h4 style="color: var(--red); margin-bottom: 10px;">Cómo jugar:</h4>
            <ol>
                ${data.pasos.map(paso => `<li style="margin-bottom: 10px; font-size: 1.1rem;">${paso}</li>`).join('')}
            </ol>
        `;
    } catch (error) {
        document.getElementById('usageContent').innerHTML = `
            <div style="color: var(--red); font-weight: 700; text-align: center;">
                Error al cargar las instrucciones de uso: ${error.message}
            </div>
        `;
    }
});

// Smooth scroll para navegación
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});