<template>
<nav class="navbar" :class="{ 'hidden-navbar': !visible }">
  <div class="brand">MealVision</div>
  <ul class="navbar-links" v-show="!showMobileMenu">
    <li><router-link class="nav_li" to="/">Home</router-link></li>
    <li><router-link class="nav_li" to="/about">About</router-link></li>
    <li><router-link class="nav_li" to="/contact">Contact</router-link></li>
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
      <li><router-link to="/model" @click="toggleMenu">Model</router-link></li>
    </ul>
  </transition>
</nav>

</template>

<script>
export default {
  name: "Nav_bar",
  data() {
    return {
      showMobileMenu: false,
      visible: true,      // navbar visibility
      lastScroll: 0,      // to track scroll position
    };
  },
  methods: {
    toggleMenu() {
      this.showMobileMenu = !this.showMobileMenu;
    }
  }
}

</script>