<template>
  <div class="container">
    <!-- Filter button -->
    <div class="filter-container">
      <button class="filter-button" @click="toggleFilter">
        <h2>🔍</h2>
      </button>

      <!-- Backdrop -->
      <div
        v-if="showFilter"
        class="filter-backdrop"
        @click.self="showFilter = false"
      >
        <!-- Modal -->
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

    <!-- Scan / Manual -->
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
      errorMessage: "",
    };
  },
  methods: {
    toggleFilter() {
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
    },
    showManualBox() {
      this.showManual = true;
      this.showScan = false;
    },
    // normalize list and clear meals when list becomes empty
    handleItemsUpdated(items) {
      const unique = new Set();
      items.forEach((raw) => {
        const word = raw.split(" ")[0].toLowerCase();
        if (word) unique.add(word);
      });
      this.addedItems = [...unique];

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
    async generateMeals() {
      if (!this.addedItems.length) {
        this.errorMessage =
          "You must scan or add at least one ingredient first.";
        this.meals = [];
        console.warn("GenerateMeals aborted – addedItems empty", {
          selectedDiets: this.selectedDiets,
        });
        return;
      }

      this.errorMessage = "";
      this.isLoading = true;
      const dietaryPreferencesStr = this.selectedDiets.join(", ");

      try {
        const { data } = await axios.post(
          "https://mealvision.onrender.com/generate-meals",
          {
            ingredients: this.addedItems,
            dietary_preferences: dietaryPreferencesStr,
          }
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
      }
    },
  },
  mounted() {
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
  },
};
</script>

<style scoped>
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

/* floating filter button */
.filter-container {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
}
.filter-button {
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 20%;
  background-color: rgba(135, 206, 250, 0.8);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.filter-button:hover {
  background-color: rgba(135, 206, 250, 1);
  transform: translateY(-2px);
}
.filter-button h2 {
  margin: 0;
  font-size: 18px;
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
  .filter-container {
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
    width: 44px;
    height: 44px;
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
  .filter-button {
    height: 40px;
    width: 40px;
    padding: 0;
  }
}
</style>
