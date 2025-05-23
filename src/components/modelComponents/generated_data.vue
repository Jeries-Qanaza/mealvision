<template>
  <div id="generatedDataDiv">
    <h1>Generated Data</h1>
    <!-- Loop through meals and pass each meal as a prop to GeneratedMeal -->
    <GeneratedMeal
      v-for="(meal, index) in meals"
      :key="index"
      :mealName="meal.mealName"
      :steps="meal.steps"
      :image="meal.image"
       />
  </div>
</template>

<script>
import GeneratedMeal from './generated_meal.vue';

export default {
  name: "GeneratedData",
  components: {
    GeneratedMeal
  },
  props: {
    meals: {
      type: Array,
      required: true,
      default: () => [] // Default to an empty array
    }
  }
};
</script>

<style>
#generatedDataDiv {
  background-color: rgba(45, 90, 62, 0.39);
  border-radius: 5px;
  padding: 20px;
  margin-top: 20px;
}
</style>