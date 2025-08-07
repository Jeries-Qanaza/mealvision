<template>
  <div class="generatedDataDiv">
    <h1>Generated Data</h1>
    <!-- Loop through meals and pass each meal as a prop to GeneratedMeal -->
    <GeneratedMeal
      v-for="(meal, index) in meals"
      :key="index"
      :mealName="meal.mealName"
      :description="meal.description"
      :steps="meal.steps"
      :image="meal.image"
    />
  </div>
</template>

<script>
import GeneratedMeal from "./generated_meal.vue";

export default {
  name: "GeneratedData",
  components: {
    GeneratedMeal,
  },
  props: {
    meals: {
      type: Array,
      required: true,
      default: () => [], // Default to an empty array
    },
  },
};
</script>
