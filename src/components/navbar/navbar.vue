<template>
    <nav class="navbar">
    
      <ul class="navbar-links">
        <li><a href="/" class="navbar-link">Home</a></li>
        <li><a href="/about" class="navbar-link">About</a></li>
        <li><a href="/services" class="navbar-link">Services</a></li>
        <li><a href="/contact" class="navbar-link">Contact</a></li>
      </ul>
      <button class="navbar-toggle" @click="toggleMenu">
        ☰
      </button>
      <ul v-if="showMobileMenu" class="mobile-menu">
        <li><a href="/" @click="toggleMenu">Home</a></li>
        <li><a href="/about" @click="toggleMenu">About</a></li>
        <li><a href="/services" @click="toggleMenu">Services</a></li>
        <li><a href="/contact" @click="toggleMenu">Contact</a></li>
      </ul>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'Nav_bar',
    data() {
      return {
        showMobileMenu: false,
      };
    },
    methods: {
      toggleMenu() {
        this.showMobileMenu = !this.showMobileMenu;
      },
    },
  };
  </script>
  
  <style>
  .navbar {

    justify-content: space-between;
    align-items: center;
    background: #2c3e50;
    padding: 0.5rem 1rem;
    color: white;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .navbar-brand a {
    text-decoration: none;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
  }
  
  .navbar-brand a:hover {
    background-color: aqua;
  }

  .navbar-links {
    list-style: none;
    display: flex;
    gap: 1rem;
  }
  
  .navbar-links .navbar-link {
    text-decoration: none;
    color: white;
  }
  
  .navbar-toggle {
    display: none;
    background: transparent;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
  }
  
  .mobile-menu {
    display: none;
    list-style: none;
    position: absolute;
    background: #34495e;
    top: 50px;
    padding: 1rem;
    border-radius: 5px;
    flex-direction: column;
    gap: 1rem;
  }
  
  .mobile-menu a {
    text-decoration: none;
    color: white;
  }
  
  /* Media Queries for Mobile Screens */
  @media (max-width: 768px) {
    .navbar-links {
      display: none;
    }
    .navbar-toggle {
      display: block;
    }
    .mobile-menu {
      display: flex;
    }
  }
  </style>
  