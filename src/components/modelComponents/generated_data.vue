<template>
  <div id="generatedDataDiv">
    <h1>Generated Data</h1>

    <!-- loop through meals -->
    <GeneratedMeal
      v-for="meal in meals"
      :key="meal.mealName"
      :mealName="meal.mealName"
      :steps="meal.steps"
      :image="meal.image"
    />
  </div>
</template>

<script>
import GeneratedMeal from "./generated_meal.vue";

export default {
  name: "GeneratedData",
  components: { GeneratedMeal },
  props: {
    meals: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style>
#generatedDataDiv {
  background-color: rgba(45, 90, 62, 0.388);
  border-radius: 5px;
  padding: 20px;
  margin-top: 20px;
}
</style>
