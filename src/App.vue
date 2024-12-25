<template>
    <Nav_bar/>
    <SignUp_page/>
    <SignIn_page/>
    <Contact/>
</template>

<script>

//import SignIn_page from './components/sign_in.vue'
import SignUp_page from './components/sign_in_up/sign_up.vue'
import SignIn_page from './components/sign_in_up/sign_in.vue'
import Nav_bar from './components/navbar/navbar.vue'
import Contact from './components/contact/contact.vue'

export default {
  name: 'App',
  components: {
    Nav_bar,
    SignIn_page,
    SignUp_page,
    Contact
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
