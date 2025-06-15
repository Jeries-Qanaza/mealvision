<template>
  <div class="container">
    <!-- Filter button - positioned differently on mobile vs desktop -->
    <div class="filter-container">
      <button class="filter-button" @click="showFilter = true">
        <h2>🔍</h2>
      </button>

      <div v-if="showFilter" class="filter-modal">
        <button id="closeDietary" @click="showFilter = false">X</button>
        <h3>Select Dietary Preferences</h3>

        <div class="checkbox-group">
          <label v-for="type in dietOptions" :key="type">
            <input type="checkbox" :value="type" v-model="selectedDiets" />
            {{ type }}
          </label>
        </div>
        <div class="filter-actions">
          <button id="okDietary" @click="applyFilters">OK</button>
        </div>
      </div>
    </div>

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
    <button class="generate-meals-button" @click="generateMeals">
      Generate Meals
    </button>

    <!-- Show skeleton loading while waiting for meals -->
    <div v-if="isLoading" class="skeleton-meal-list">
      <div v-for="i in 3" :key="i" class="skeleton-meal">
        <div class="skeleton-shimmer"></div>
      </div>
    </div>

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
      cameraError: null,
      showFilter: false,
      dietOptions: [
        "Vegan 🌱",
        "Vegetarian 🥦",
        "Pescetarian 🐟",
        "Gluten-Free 🚫🌾",
        "Keto 🥩",
        "Halal 🕌",
      ],
      selectedDiets: [],
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
      this.cameraError = error.message || "Failed to access camera";
      this.cameraReady = false;
    },
    retryCamera() {
      this.cameraError = null;
      this.cameraReady = false;
      // force the ModelCam to remount:
      this.showScan = false;
      this.$nextTick(() => (this.showScan = true));
    },
    applyFilters() {
      console.log("Selected dietary preferences:", this.selectedDiets);
      // Note: localStorage usage removed for Claude.ai compatibility
      this.showFilter = false;
    },
    async generateMeals() {
      this.isLoading = true;
      const dietaryPreferencesStr = this.selectedDiets.join(", ");

      try {
        const response = await axios.post(
          "https://mealvision.onrender.com/generate-meals",
          {
            ingredients: this.addedItems,
            dietary_preferences: dietaryPreferencesStr,
          }
        );

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
  mounted() {
    // Note: localStorage usage removed for Claude.ai compatibility
    // You can restore this functionality in your own environment if needed
  },
  watch: {
    showScan(newVal) {
      if (newVal) {
        this.cameraReady = false;
        this.cameraError = null;
      }
    },
  },
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
  position: relative;
}

/* Desktop: Filter in top-right corner */
.filter-container {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.choice-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
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

.camera-error,
.camera-loading {
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
  background-color: #ffa500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  margin-top: 20px;
}

.generate-meals-button:hover {
  background-color: #ff8c00;
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

.filter-button {
  padding: 15px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  background-color: rgba(135, 206, 250, 0.8);
  color: #191b31;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-button:hover {
  background-color: rgba(135, 206, 250, 1);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

.filter-button h2 {
  margin: 0;
  font-size: 20px;
}

.filter-modal {
  position: absolute;
  top: 70px;
  right: 0;
  background: white;
  color: #191b31;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 999;
  width: 250px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
  text-align: left;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
}

#okDietary {
  width: 100%;
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

#closeDietary {
  position: absolute;
  top: 8px;
  right: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #191b31;
}

#closeDietary:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* Mobile Layout: Filter button above and aligned with choice buttons */
@media (max-width: 768px) {
  .container {
    padding: 20px;
  }

  /* Move filter above choice buttons, aligned to the right */
  .filter-container {
    position: static;
    display: flex;
    justify-content: flex-end;
    margin-bottom: 15px;
    padding-right: 0;
  }

  .choice-buttons {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }

  .choice-buttons button {
    width: 100%;
    max-width: 300px;
  }

  .filter-button {
    width: 60px;
    height: 60px;
    padding: 10px;
  }

  .filter-modal {
    width: 200px;
    top: 70px;
    right: 0;
  }
}

/* Extra small devices */
@media (max-width: 480px) {
  .container {
    padding: 15px;
    margin: 10px;
  }

  .filter-modal {
    width: 260px;
  }

  .choice-buttons button {
    padding: 12px 20px;
    font-size: 14px;
  }

  .filter-button {
    height: 45px;
    padding: 8px;
  }
}
</style>
