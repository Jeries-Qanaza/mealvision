<template>
  <div class="container">
    <div class="choice-buttons">
      <button @click="showCamera"><h2>Scan</h2></button>
      <button @click="showManualBox"><h2>Add Manually</h2></button>
    </div>
    <hr />
    <div class="content">
      <div v-if="showScan" class="camera-placeholder">
        <ModelCam 
          @camera-ready="cameraReady = true" 
          @camera-error="handleCameraError" 
          @items-updated="handleItemsUpdated"
          />
        <div v-if="cameraError" class="camera-error">
          <p>Camera Error: {{ cameraError }}</p>
          <button @click="retryCamera">Retry Camera</button>
        </div>
        <div v-else-if="!cameraReady" class="camera-loading">
          <p>Initializing camera...</p>
        </div>
      </div>
      <ManualBox v-if="showManual" @items-updated="handleItemsUpdated" />
    </div>
    <button class="generate-meals-button" @click="generateMeals">Generate Meals</button>

    <!-- Show skeleton loading while waiting for meals -->
    <div v-if="isLoading" class="skeleton-meal-list">
      <div v-for="i in 3" :key="i" class="skeleton-meal">
        <div class="skeleton-shimmer"></div>
      </div>
    </div>

    <!-- Pass meals data to GeneratedData -->
    <GeneratedData v-else :meals="meals" />
  </div>
</template>

<script>
import axios from "axios";
import ManualBox from "./manualbox.vue";
import GeneratedData from "./generated_data.vue";
import ModelCam from "../modelComponents/model_cam.vue";

export default {
  name: "UserInputDiv",
  components: { ManualBox, GeneratedData, ModelCam },
  data() {
    return {
      showScan: true,
      showManual: false,
      addedItems: [],
      meals: [],
      isLoading: false,
      cameraReady: false,
      cameraError: null
    };
  },
  methods: {
    showCamera() {
      this.showScan = true;
      this.showManual = false;
      this.cameraReady = false;
      this.cameraError = null;
    },
    showManualBox() {
      this.showManual = true;
      this.showScan = false;
    },
    handleItemsUpdated(items) {
      this.addedItems = items;
    },
    handleCameraError(error) {
      this.cameraError = error.message || 'Failed to access camera';
      this.cameraReady = false;
    },
    retryCamera() {
      this.cameraError = null;
      this.cameraReady = false;
      // force the ModelCam to remount:
      this.showScan = false;
      this.$nextTick(() => this.showScan = true);
    },
    async generateMeals() {
      this.isLoading = true;
      try {
        const response = await axios.post("https://mealvision.onrender.com/generate-meals", {
          ingredients: this.addedItems,
        });

        if (response.data && Array.isArray(response.data.meals_res)) {
          this.meals = response.data.meals_res;
        } else {
          console.error("Invalid response format:", response.data);
          this.meals = [];
        }
      } catch (error) {
        console.error("Error generating meals:", error);
        this.meals = [];
      } finally {
        this.isLoading = false;
      }
    },
  },
  watch: {
    showScan(newVal) {
      if (newVal) {
        this.cameraReady = false;
        this.cameraError = null;
      }
    }
  }
};
</script>

<style scoped>
.container {
  background-color: rgba(25, 27, 49, 0.8);
  border-radius: 15px;
  padding: 30px;
  text-align: center;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  margin: 20px auto;
  color: white;
}

.choice-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.choice-buttons button {
  padding: 15px 30px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  background-color: rgba(255, 165, 0, 0.8);
  color: #191b31;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.choice-buttons button:hover {
  background-color: rgba(255, 165, 0, 1);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

.choice-buttons button h2 {
  margin: 0;
}

hr {
  border: none;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  margin: 20px 0;
}

.content {
  margin: 20px 0;
}

.camera-placeholder {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.7);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-error, .camera-loading {
  text-align: center;
  padding: 20px;
}

.camera-error button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.generate-meals-button {
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  color: #191b31;
  background-color: #FFA500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  margin-top: 20px;
}

.generate-meals-button:hover {
  background-color: #FF8C00;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* Skeleton Loading Animation for Meal List */
.skeleton-meal-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 30px;
}

.skeleton-meal {
  width: 100%;
  height: 120px;
  background: rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  border-radius: 8px;
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
    rgba(255, 255, 255, 0.1),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  100% {
    left: 100%;
  }
}

@media (max-width: 768px) {
  .choice-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .container {
    padding: 20px;
  }
}
</style>
