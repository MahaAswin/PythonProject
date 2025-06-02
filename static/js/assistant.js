document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const startButton = document.getElementById('startButton');
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('status');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                username: document.getElementById('loginUsername').value,
                password: document.getElementById('loginPassword').value
            };

            try {
                const response = await fetch('/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (response.ok) {
                    window.location.reload();
                } else {
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                showNotification('An error occurred during login', 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                username: document.getElementById('registerUsername').value,
                email: document.getElementById('registerEmail').value,
                password: document.getElementById('registerPassword').value
            };

            try {
                const response = await fetch('/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (response.ok) {
                    window.location.reload();
                } else {
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                showNotification('An error occurred during registration', 'error');
            }
        });
    }

    if (startButton) {
        startButton.addEventListener('click', async function() {
            try {
                startButton.disabled = true;
                startButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Listening...';
                statusDiv.textContent = 'Listening for your command...';

                const response = await fetch('/process-command/', {
                    method: 'POST',
                });

                const data = await response.json();
                if (response.ok) {
                    const newResult = document.createElement('div');
                    newResult.className = 'mb-4';
                    newResult.innerHTML = `
                        <p class="font-bold">You said: ${data.command}</p>
                        <p class="text-gray-600">JARVIS: ${data.response}</p>
                    `;
                    resultDiv.innerHTML = '';
                    resultDiv.appendChild(newResult);
                    statusDiv.textContent = '';
                    showNotification('Command processed successfully', 'success');
                } else {
                    statusDiv.textContent = data.error;
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                statusDiv.textContent = 'An error occurred while processing your command';
                showNotification('An error occurred while processing your command', 'error');
            } finally {
                startButton.disabled = false;
                startButton.innerHTML = '<i class="fas fa-microphone mr-2"></i>Start Listening';
            }
        });
    }
});

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg transition-opacity duration-500 ${
        type === 'error' ? 'bg-red-500' :
        type === 'success' ? 'bg-green-500' :
        'bg-blue-500'
    } text-white`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
} 