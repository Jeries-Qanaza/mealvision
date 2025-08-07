<template>
  <div id="app">
    <NavBar />
    <router-view />

    <div id="myfooter">
      <AppFooter />
    </div>
  </div>
</template>

<script>
import NavBar from "./components/navbar/navbar.vue";
import AppFooter from "./components/AppFooter.vue";
export default {
  name: "App",
  components: {
    NavBar,
    AppFooter,
  },
  data() {
    return {
      email: "",
      password: "",
      birthday: {
        day: "",
        month: "",
        year: "",
      },
    };
  },
  methods: {},
};
</script>
