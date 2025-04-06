import { createAccountModal } from './user-authentication.js';

const menuToggle = document.getElementById('menuToggle');
const mobileNav = document.getElementById('mobileNav');
const closeMenu = document.getElementById('closeMenu');
const body = document.body;

// Open Mobile Menu
menuToggle.addEventListener('click', () => {
    mobileNav.classList.add('active');
    body.style.overflow = 'hidden'; // Disable scroll
});

// Close Mobile Menu
closeMenu.addEventListener('click', () => {
    mobileNav.classList.remove('active');
    body.style.overflow = ''; // Enable scroll
});

document.addEventListener('DOMContentLoaded', async () => {
    await createAccountModal();
});