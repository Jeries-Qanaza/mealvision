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
      <!-- UPDATE your template section in user_input_div.vue -->
      <div v-if="showScan" class="camera-placeholder">
        <ModelCam
          @camera-ready="cameraReady = true"
          @camera-error="handleCameraError"
          @items-updated="handleItemsUpdated"
          @processing-state="handleProcessingState"
          @media-updated="handleMediaUpdated"
          :is-app-busy="isAppBusy"
          :existing-items="addedItems"
          :existing-preview-images="previewImages"
          :existing-video-items="videoItems"
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
        :existing-items="addedItems"
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
      previewImages: [],
      videoItems: [],
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
    handleMediaUpdated(mediaData) {
      this.previewImages = mediaData.previewImages || [];
      this.videoItems = mediaData.videoItems || [];
    },
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
      this.meals = [];
    },
    showManualBox() {
      this.showManual = true;
      this.showScan = false;
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
        console.info("Current ingredients list:", this.addedItems);
      } else {
        this.meals = [];
      }
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
        // Optional meal_type filter
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
      } catch (error) {
        console.error("Axios error:", error);

        // Check if the server sent back a specific error message in the response
        if (
          error.response &&
          error.response.data &&
          error.response.data.error
        ) {
          // Use the specific error message from the server
          this.errorMessage = error.response.data.error;
        } else {
          // Fallback to a generic message for other types of errors
          this.errorMessage =
            "An error occurred. Please check your connection and try again.";
        }
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
