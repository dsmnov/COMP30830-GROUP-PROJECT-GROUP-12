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
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }

        #account-modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
            transition: opacity 0.3s ease;
        }
  
        /* Account Modal Container */
        #account-modal-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.95);
            background-color: #fff;
            padding: 20px;
            border-radius: 20px;
            z-index: 1001;
            width: 400px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease, transform 0.2s ease;
        }

        #account-modal-container.active {
            opacity: 1;
            pointer-events: auto;
            transform: translate(-50%, -50%) scale(1);
        }

        /* Modal content styling */
        #account-modal-container h2 {
            position: absolute;
            top: -3px;
            left: 0;
            right: 0;
            font-family: 'ProximaNova-Bold', sans-serif;
            background-color: #334;
            color: #fff;
            padding: 20px;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            text-align: center;
            margin: 0;
        }

        #account-modal-container form {
            font-family: 'ProximaNova-regular', sans-serif;
            display: flex;
            flex-direction: column;
            margin-top: 60px;
        }

        #account-modal-container form input[type = 'text'],
        #account-modal-container form input[type = 'password'],
        #account-modal-container form textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        #account-modal-container form input[type = 'submit'],
        #account-modal-container form button {
            font-family: 'ProximaNova-Bold', sans-serif;
            padding: 10px 15px;
            border: none;
            background-color: #334;
            color: #fff;
            border-radius: 15px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        #account-modal-container form input[type = 'submit']:hover,
        #account-modal-container form button:hover {
            background-color: #23234a;
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

    function attachLoginForm(modal, action) {
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

            attachLoginForm(modal, action);
        });
    }

    async function showModal(action) {
        const reponse = await fetch('/' + action)
        const html = await reponse.text()
        modal.innerHTML = html;
        attachLoginForm(modal, action);

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
  