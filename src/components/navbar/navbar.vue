<template>
  <nav class="navbar">
    <div class="brand">MealVision</div>
    <ul class="navbar-links" v-show="!showMobileMenu">
      <li><router-link class="nav_li" to="/">Home</router-link></li>
      <li><router-link class="nav_li" to="/about">About</router-link></li>
      <li><router-link class="nav_li" to="/contact">Contact</router-link></li>
      <li><router-link class="nav_li" to="/signIn">Sign-In</router-link></li>
      <li><router-link class="nav_li" to="/signUp">Sign-Up</router-link></li>
      <li><router-link class="nav_li" to="/model">Model</router-link></li>
    </ul>
    <button class="navbar-toggle" @click="toggleMenu" aria-label="Toggle menu">
      <span class="hamburger-box">
        <span class="hamburger-inner" :class="{ 'is-active': showMobileMenu }"></span>
      </span>
    </button>
    <transition name="slide-down">
      <ul v-if="showMobileMenu" class="mobile-menu">
        <li><router-link to="/" @click="toggleMenu">Home</router-link></li>
        <li><router-link to="/about" @click="toggleMenu">About</router-link></li>
        <li><router-link to="/contact" @click="toggleMenu">Contact</router-link></li>
        <li><router-link to="/signIn" @click="toggleMenu">Sign-In</router-link></li>
        <li><router-link to="/signUp" @click="toggleMenu">Sign-Up</router-link></li>
        <li><router-link to="/model" @click="toggleMenu">Model</router-link></li>
      </ul>
    </transition>
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

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #191b31;
  padding: 1rem 2rem;
  border-radius: 0 0 1rem 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-wrap: wrap;
}

.brand {
  font-size: 1.8rem;
  font-weight: bold;
  color: orange;
  text-shadow: 1px 1px 4px #000;
  margin-right: auto;
}

.navbar-links {
  list-style: none;
  display: flex;
  gap: 1rem;
  margin-left: 2rem;
  flex-grow: 1;
}

.navbar-links li {
  margin-right: 1rem;
}

.nav_li {
  color: orange;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: 0.3s ease;
}

.nav_li:hover,
.nav_li.router-link-exact-active {
  background: rgba(255, 165, 0, 0.2);
  color: white;
}

/* Improved Hamburger Menu */
.navbar-toggle {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 10px;
  margin-left: auto;
  outline: none;
}

.hamburger-box {
  width: 30px;
  height: 24px;
  display: inline-block;
  position: relative;
}

.hamburger-inner {
  display: block;
  top: 50%;
  margin-top: -2px;
}

.hamburger-inner,
.hamburger-inner::before,
.hamburger-inner::after {
  width: 30px;
  height: 3px;
  background-color: orange;
  border-radius: 3px;
  position: absolute;
  transition: transform 0.15s ease;
}

.hamburger-inner::before,
.hamburger-inner::after {
  content: "";
  display: block;
}

.hamburger-inner::before {
  top: -8px;
}

.hamburger-inner::after {
  bottom: -8px;
}

.hamburger-inner.is-active {
  background-color: transparent;
}

.hamburger-inner.is-active::before,
.hamburger-inner.is-active::after {
  background-color: white;
  transform-origin: center;
}

.hamburger-inner.is-active::before {
  transform: rotate(45deg);
  top: 0;
}

.hamburger-inner.is-active::after {
  transform: rotate(-45deg);
  bottom: 0;
}


/* Mobile Menu */
.mobile-menu {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: 70px;
  right: 20px;
  background: rgba(25, 27, 49, 0.98);
  padding: 1rem;
  border-radius: 10px;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  width: 200px;
  list-style: none;
  margin: 0;
  padding-left: 0;
}

.mobile-menu li {
  padding: 0.5rem 0;
}

.mobile-menu a {
  display: block;
  width: 100%;
  color: orange;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.mobile-menu a:hover {
  color: white;
  background: rgba(255, 165, 0, 0.2);
}

/* Animation */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Responsive Styles */
@media (max-width: 768px) {
  .navbar-links {
    display: none;
  }

  .navbar-toggle {
    display: block;
  }
  
  .navbar {
    padding: 1rem;
  }
}
</style>