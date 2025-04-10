import { createAccountModal } from './user-authentication.js';

// Ensures dom content is loaded before user authentication code attaches itself to appropriate buttons/ actions
// Also handles the logout logic
document.addEventListener('DOMContentLoaded', async () => {
    const logInButton = document.getElementById('log-in-button');
    if ( logInButton ) {
        await createAccountModal();
    }

    const logOutButton = document.getElementById('log-out-button');
    if ( logOutButton ) {
        logOutButton.addEventListener('click', async () => {
            const response = await fetch('/logout', { 
                method: 'POST',
                credentials: 'same-origin' 
            });

            if (response.ok) {
                location.reload();
            } else {
                console.error('Logout failed');
            }
        });
    }
});