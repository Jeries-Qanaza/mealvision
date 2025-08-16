<template>
  <div id="app">

        
      <router-view/>
      
    


    <div id="myfooter">
      <AppFooter />
    </div>
  </div>
</template>

<script>

import AppFooter from "./components/AppFooter.vue";
export default {
  name: "App",
  components: {
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
