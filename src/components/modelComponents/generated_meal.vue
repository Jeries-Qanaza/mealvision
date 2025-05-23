<template>
  <div class="generated-meal">
    <!-- Show skeleton loading for the image -->
    <div v-if="!image" class="skeleton-image">
      <div class="skeleton-shimmer"></div>
    </div>

    <!-- Show actual image when loaded -->
    <img v-else class="meal-image" :src="imageSrc" alt="meal_demo">

    <div class="meal-content">
      <!-- Show skeleton loading for the meal name -->
      <div v-if="!mealName" class="skeleton-text skeleton-name"></div>
      <h3 v-else class="meal-name">{{ mealName }}</h3>

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
      required: true
    },
    steps: {
      type: Array,
      required: true
    },
    image: {
      type: String,
      default: ""
    }
  },
  computed: {
    imageSrc() {
      if (this.image) {
        return `data:image/jpg;base64,${this.image}`;
      } else {
        return "https://via.placeholder.com/100"; // Fallback image
      }
    }
  }
};
</script>

<style scoped>
/* Skeleton Loading Animation for Meal Card */
.skeleton-image {
  width: 100px;
  height: 100px;
  background: #e0e0e0; /* Gray background */
  position: relative;
  overflow: hidden;
  border-radius: 4px; /* Optional: Rounded corners */
}

.skeleton-text {
  background: #e0e0e0; /* Gray background */
  position: relative;
  overflow: hidden;
  border-radius: 4px; /* Optional: Rounded corners */
}

.skeleton-name {
  width: 80%;
  height: 20px;
  margin-bottom: 10px;
}

.skeleton-step {
  width: 100%;
  height: 16px;
  margin-bottom: 8px;
}

.skeleton-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.5),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  100% {
    left: 100%;
  }
}

/* Generated Meal Styles */
.generated-meal {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background-color: rgba(45, 90, 62, 0.39);
  border-radius: 5px;
  padding: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-align: left;
}

.generated-meal:hover {
  background-color: rgba(45, 90, 62, 0.6);
}

.meal-content {
  flex: 1;
}

.meal-name {
  font-weight: bold;
  text-decoration: underline;
  margin-bottom: 10px;
}

.meal-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 5px;
  margin: 15px;
}
</style>