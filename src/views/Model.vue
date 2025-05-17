<template>
    <div class="manual-container">

    <UserInputDiv/>
    <ManualBox/>
 
 
    </div>
  </template>
  
  <script>
import UserInputDiv from "@/components/modelComponents/user_input_div.vue";
  
  export default {
    name: "Our_Model",
    components: {
 
      UserInputDiv
  },
  };
  </script>
  
  <style scoped>

.manual-container
{
    padding: 2%;
    background-color: #191b31;
}

  .overlay {
    text-align: center;
    color: white; /* Text color */
    background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background to make text more readable */
    padding: 20px;
    border-radius: 10px;
  }
  
  h1 {
    font-size: 3em;
    margin-bottom: 20px;
  }
  
  p {
    font-size: 1.5em;
  }
  </style>
  