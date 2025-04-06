// Singleton Coding Style https://refactoring.guru/design-patterns/singleton alongside css-in-js style for modularity and maintainability

export async function createAccountModal() {
    const css = `
        /* Button hover effects */
        #log-in-button, #register-button {
            cursor: pointer;
        }
  
        /* Dimming Background */
        #account-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            /* Start invisible and unclickable by default */
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }
  
        /* Account Modal Container */
        #account-modal-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.95);
            background-color: #fff;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            z-index: 1001;
            max-width: 90%;
            width: 400px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease, transform 0.2s ease;
        }

        #account-modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
            transition: opacity 0.5s ease;
        }

        #account-modal-container.active {
            opacity: 1;
            pointer-events: auto;
            transform: translate(-50%, -50%) scale(1);
        }
        `;

  
    const styleId = 'account-modal';
    const styleExists = document.getElementById(styleId);

    // Singleton CSS injection
    if (!styleExists) {
      const modalStyle = document.createElement('style');
      modalStyle.id = styleId;
      modalStyle.appendChild(document.createTextNode(css));
      document.head.appendChild(modalStyle);
    }
  
    const overlay = document.createElement('div');
    overlay.id = 'account-modal-overlay';
  
    const modal = document.createElement('div');
    modal.id = 'account-modal-container';

    document.body.appendChild(overlay);
    document.body.appendChild(modal);

    function attachFormSubmission(modal, action) {
        const form = modal.querySelector('form');
        if (!form) return;
    
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(form);
    
            const submitResponse = await fetch('/' + action, {
                method: 'POST',
                body: formData
            });
    
            const updatedHtml = await submitResponse.text();
            modal.innerHTML = updatedHtml;

            attachFormSubmission(modal, action);
        });
    }

    async function showModal(action) {
        const reponse = await fetch('/' + action)
        const html = await reponse.text()
        modal.innerHTML = html;
        attachFormSubmission(modal, action);

        overlay.classList.add('active');
        modal.classList.add('active');
    }
  
    function hideModal() {
        overlay.classList.remove('active');
        modal.classList.remove('active');
    }

    const loginButton = document.getElementById('log-in-button');
    const registerButton = document.getElementById('register-button');
    
    loginButton.addEventListener('click', () => showModal(loginButton.dataset.login));
    registerButton.addEventListener('click', () => showModal(registerButton.dataset.register));

    overlay.addEventListener('click', hideModal);
}
  