document.addEventListener('DOMContentLoaded', async () => {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвратить стандартное действие формы

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = '/index';
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
