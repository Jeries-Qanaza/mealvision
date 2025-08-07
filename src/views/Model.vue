<template>
  <div class="manual-container">
    <UserInputDiv />
    <ManualBox />
  </div>
</template>

<script>
import UserInputDiv from "@/components/modelComponents/user_input_div.vue";

export default {
  name: "Our_Model",
  components: {
    UserInputDiv,
  },
};
</script>
