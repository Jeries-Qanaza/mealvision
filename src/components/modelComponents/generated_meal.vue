<template>
  <div class="generated-meal">
    <!-- Show skeleton loading for the image -->
    <div v-if="!image" class="skeleton-image">
      <div class="skeleton-shimmer"></div>
    </div>

    <!-- Show actual image when loaded -->
    <img v-else class="meal-image" :src="imageSrc" alt="meal_demo" />

    <div class="meal-content">
      <!-- Show skeleton loading for the meal name -->
      <div v-if="!mealName" class="skeleton-text skeleton-name"></div>
      <h3 v-else class="meal-name">{{ mealName }}</h3>

      <!-- Show skeleton for description -->
      <div v-if="!description" class="skeleton-text skeleton-description"></div>
      <p v-else class="meal-description">{{ description }}</p>

      <!-- Show skeleton loading for the steps -->
      <ul>
        <li v-for="(step, index) in steps" :key="index">
          <div v-if="!step" class="skeleton-text skeleton-step"></div>
          <span v-else>{{ step }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "GeneratedMeal",
  props: {
    mealName: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    steps: {
      type: Array,
      required: true,
    },
    image: {
      type: String,
      default: "",
    },
  },
  computed: {
    imageSrc() {
      if (this.image) {
        return `data:image/jpg;base64,${this.image}`;
      } else {
        return "https://via.placeholder.com/100"; // Fallback image
      }
    },
  },
};
</script>
