<template>
  <NavBar style="background-color: #174329" />
  <div class="manual-container page-container">
    <UserInputDiv />
    <ManualBox />
  </div>
</template>

<script>
import NavBar from "@/components/navbar/navbar.vue";
import UserInputDiv from "@/components/modelComponents/user_input_div.vue";

export default {
  name: "Our_Model",
  components: {
    UserInputDiv,
    NavBar,
  },
};
</script>
