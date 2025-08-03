<template>
  <div class="container" :class="{ 'is-loading': isAppBusy }">
    <div v-if="isAppBusy" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <div class="header-actions-container">
      <div class="filter-wrapper">
        <select
          v-model="selectedMealTime"
          class="meal-type-select base-filter-style"
          :disabled="isAppBusy"
        >
          <option value="">Meal Type 🕘</option>
          <option
            v-for="meal in mealTimeOptions"
            :key="meal.value"
            :value="meal.value"
          >
            {{ meal.text }}
          </option>
        </select>
        <button
          v-if="selectedMealTime"
          @click="clearMealTypeFilter"
          class="clear-filter-btn"
          :disabled="isAppBusy"
        >
          ×
        </button>
      </div>

      <div class="filter-modal-container" ref="dietFilterContainer">
        <button
          class="filter-button base-filter-style"
          @click="toggleFilter"
          :disabled="isAppBusy"
        >
          <h2>Diet Type 🍽️</h2>
        </button>

        <div
          v-if="showFilter"
          class="filter-backdrop"
          @click.self="showFilter = false"
        >
          <div class="filter-modal">
            <button class="modal-close" @click="showFilter = false">×</button>
            <h3>Select Dietary Preferences</h3>

            <div class="checkbox-group">
              <label v-for="type in dietOptions" :key="type">
                <input type="checkbox" :value="type" v-model="selectedDiets" />
                {{ type }}
              </label>
            </div>
            <div class="filter-actions">
              <button id="resetDietary" @click="resetFilters">Reset</button>
              <button id="saveDietary" @click="applyFilters">Save</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="choice-buttons">
      <button @click="showCamera" :disabled="isAppBusy"><h2>Scan</h2></button>
      <button @click="showManualBox" :disabled="isAppBusy">
        <h2>Add Manually</h2>
      </button>
    </div>

    <hr />

    <div class="content">
      <div v-if="showScan" class="camera-placeholder">
        <ModelCam
          @camera-ready="cameraReady = true"
          @camera-error="handleCameraError"
          @items-updated="handleItemsUpdated"
          @processing-state="handleProcessingState"
          :is-app-busy="isAppBusy"
        />
        <div v-if="cameraError" class="camera-error">
          <p>Camera Error: {{ cameraError }}</p>
          <button @click="retryCamera" :disabled="isAppBusy">
            Retry Camera
          </button>
        </div>
        <div v-else-if="!cameraReady" class="camera-loading">
          <p>Initializing camera...</p>
        </div>
      </div>

      <ManualBox
        v-if="showManual"
        @items-updated="handleItemsUpdated"
        :is-app-busy="isAppBusy"
      />
    </div>

    <button
      class="generate-meals-button"
      @click="generateMeals"
      :disabled="isAppBusy"
    >
      Generate Meals
    </button>

    <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

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

const API_BASE = process.env.VUE_APP_API_BASE; // Save the Backend url in a variable
export default {
  name: "UserInputDiv",
  components: { ManualBox, GeneratedData, ModelCam },
  data() {
    return {
      showScan: true,
      showManual: false,
      addedItems: [],
      meals: [],
      isLoading: false, // For the skeleton screen specifically
      isAppBusy: false, // Global state for disabling all controls
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
      // Meal time options and selected value
      mealTimeOptions: [
        { text: "Breakfast ☀️", value: "Breakfast" },
        { text: "Lunch 🍝", value: "Lunch" },
        { text: "Dinner 🌙", value: "Dinner" },
      ],
      selectedMealTime: "", // Empty string means no preference
      errorMessage: "",
    };
  },
  methods: {
    // Method to handle processing state from child components
    handleProcessingState(isProcessing) {
      this.isAppBusy = isProcessing;
    },
    toggleFilter() {
      if (this.isAppBusy) return; // Prevent opening filter when busy
      this.showFilter = !this.showFilter;
    },
    resetFilters() {
      this.selectedDiets = [];
    },
    showCamera() {
      this.showScan = true;
      this.showManual = false;
      this.cameraReady = false;
      this.cameraError = null;
      this.addedItems = []; // Clear items when switching mode
      this.meals = []; // Clear meals when switching mode
    },
    showManualBox() {
      this.showManual = true;
      this.showScan = false;
      this.addedItems = []; // Clear items when switching mode
      this.meals = []; // Clear meals when switching mode
    },
    handleItemsUpdated(items) {
      const unique = new Set();
      items.forEach((raw) => {
        const word = raw.split(" ")[0].toLowerCase();
        if (word) unique.add(word);
      });
      this.addedItems = [...unique];
      this.meals = []; // Clear previous meals when ingredients change

      if (this.addedItems.length) {
        this.errorMessage = "";
      } else {
        this.meals = [];
      }
      console.info("Current ingredients list:", this.addedItems);
    },
    handleCameraError(error) {
      this.cameraError = error.message || "Failed to access camera";
      this.cameraReady = false;
    },
    retryCamera() {
      this.cameraError = null;
      this.cameraReady = false;
      this.showScan = false;
      this.$nextTick(() => (this.showScan = true));
    },
    applyFilters() {
      console.log("Selected dietary preferences:", this.selectedDiets);
      localStorage.setItem("selectedDiets", JSON.stringify(this.selectedDiets));
      this.showFilter = false;
    },
    // By Clicking 'x' Clear Meal Type filter
    clearMealTypeFilter() {
      this.selectedMealTime = "";
    },
    handleClickOutside_Diet(event) {
      if (
        this.$refs.dietFilterContainer &&
        !this.$refs.dietFilterContainer.contains(event.target)
      ) {
        this.showFilter = false;
      }
    },
    async generateMeals() {
      // Case 1: App is already busy, ignore the click silently and do nothing.
      if (this.isAppBusy) {
        return;
      }

      // Case 2: No items added. Show error, clear old meals, and log a warning.
      if (!this.addedItems.length) {
        this.errorMessage =
          "You must scan or add at least one ingredient first.";
        this.meals = [];
        console.warn("GenerateMeals aborted – addedItems empty", {
          selectedDiets: this.selectedDiets,
        });
        return;
      }

      // If we passed the checks, continue with the meal generation
      this.errorMessage = "";
      this.isAppBusy = true;
      this.isLoading = true; // For skeleton screen
      this.meals = []; // Clear old results immediately
      const dietaryPreferencesStr = this.selectedDiets.join(", ");

      try {
        // Added payload: removed user_local_time and added optional meal_type
        const payload = {
          ingredients: this.addedItems,
          dietary_preferences: dietaryPreferencesStr,
        };
        if (this.selectedMealTime) {
          payload.meal_type = this.selectedMealTime;
        }

        // DEBUGGING payload to console
        console.log("Sending payload to server:", payload);
        const { data } = await axios.post(
          `${API_BASE}/generate-meals`,
          payload
        );

        if (Array.isArray(data?.meals_res)) {
          this.meals = data.meals_res;
        } else {
          console.error("Unexpected response format", data);
          this.errorMessage = "Server returned an unexpected response.";
          this.meals = [];
        }
      } catch (err) {
        console.error("Axios error:", err);
        this.errorMessage = "Error generating meals. Please try again.";
        this.meals = [];
      } finally {
        this.isLoading = false;
        this.isAppBusy = false;
      }
    },
  },
  mounted() {
    // Set default disabled option for meal type select
    this.selectedMealTime = "";
    const saved = localStorage.getItem("selectedDiets");
    if (saved) {
      try {
        this.selectedDiets = JSON.parse(saved);
      } catch (_) {
        localStorage.removeItem("selectedDiets");
      }
    }
  },
  watch: {
    showScan(val) {
      if (val) {
        this.cameraReady = false;
        this.cameraError = null;
      }
    },
    showFilter(isShown) {
      if (isShown) {
        // When the filter is open
        document.addEventListener("mousedown", this.handleClickOutside_Diet);
      } else {
        document.removeEventListener("mousedown", this.handleClickOutside_Diet);
      }
    },
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this.handleClickOutside_Diet);
  },
};
</script>

<style scoped>
.container.is-loading {
  pointer-events: none; /* Disables all mouse events on the container */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(25, 27, 49, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  border-radius: 15px;
  backdrop-filter: blur(4px);
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-left-color: #ffa500;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Style for disabled filter buttons */
.base-filter-style:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none; /* Prevents hover effect on disabled */
}

/* container */
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

.header-actions-container {
  position: sticky;
  top: 0;
  display: flex;
  justify-content: flex-end; /* Align to the right inside the container */
  align-items: center;
  gap: 10px;
  margin-bottom: 40px; /* Space below the filters */
  z-index: 1000;
  background-color: rgba(25, 27, 49, 0.8); /* Optional: matches container bg to avoid overlap transparency */
  padding-top: 10px; /* Optional: small spacing above */
  padding-right: 10px; /* Push from right edge */
}

/* Wrapper for positioning the select and clear button together */
.filter-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

/* New: Shared base style for filter buttons to ensure uniformity */
.base-filter-style {
  background-color: #ffffff;
  color: #191b31;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  height: 40px;
  transition: all 0.3s ease;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 15px;
}

.base-filter-style:hover {
  background-color: #ffffff;
  transform: translateY(-2px);
}

/* Styling for the meal type dropdown */
.meal-type-select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20width%3D%27292.4%27%20height%3D%27292.4%27%3E%3Cpath%20fill%3D%27%23191B31%27%20d%3D%27M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%27%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 12px top 50%;
  background-size: 0.7em auto;
  padding-right: 50px; /* make space for arrow and clear button */
  justify-content: flex-start; /* Align text to the left */
}

/* Styling for the clear button */
.clear-filter-btn {
  position: absolute;
  right: 35px; /* Position inside the select, near the dropdown arrow */
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #ffffff;
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
  padding: 0;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.clear-filter-btn:hover {
  opacity: 1;
}

.filter-modal-container {
  position: relative;
}

.filter-button {
  width: auto; /* Allow button to size based on content */
}

.filter-button h2 {
  margin: 0;
  font-size: 15px; /* Match font size for consistency */
}

/* backdrop */
.filter-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 80px;
  box-sizing: border-box;
  z-index: 999;
}
@media (max-width: 768px) {
  .filter-backdrop {
    justify-content: center;
    padding: 80px 0 0;
  }
}

/* modal box */
.filter-modal {
  background: white;
  color: #191b31;
  width: 220px;
  padding: 18px 20px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
  position: relative;
}
.filter-modal h3 {
  margin: 0 0 12px;
  font-size: 18px;
  text-align: center;
}

/* small X */
.modal-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  color: #191b31;
  opacity: 0.6;
}
.modal-close:hover {
  opacity: 1;
}

/* checkboxes */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0 18px;
  text-align: left;
}
.checkbox-group label {
  font-size: 14px;
}

/* buttons */
.filter-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 18px;
}
#resetDietary,
#saveDietary {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: white;
}
#resetDietary {
  background-color: #2196f3;
}
#resetDietary:hover {
  background-color: #1976d2;
}
#saveDietary {
  background-color: #4caf50;
}
#saveDietary:hover {
  background-color: #43a047;
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
.error-msg {
  color: #ff6b6b;
  margin-top: 12px;
  font-weight: 600;
}
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

/* responsive tweaks */
@media (max-width: 768px) {
  .container {
    padding: 20px;
  }
  .header-actions-container {
    position: static;
    display: flex;
    justify-content: flex-end;
    margin-bottom: 15px;
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
    min-width: 120px;
    height: 44px;
  }

  .filter-button h2 {
    font-size: 14px;
    white-space: nowrap;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
    margin: 10px;
  }
  .choice-buttons button {
    padding: 12px 20px;
    font-size: 14px;
  }
  .base-filter-style {
    height: 40px;
    padding-top: 0;
    padding-bottom: 0;
  }
}
</style>
