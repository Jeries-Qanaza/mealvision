<template>
  <div class="search-wrapper">
    <div class="search-input-container">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Add Item (e.g., 'apple')"
        class="search-input"
        @input="handleInput"
        @keydown.down.prevent="onArrowDown"
        @keydown.up.prevent="onArrowUp"
        @keydown.enter.prevent="onEnter"
        @keydown.esc="showSuggestions = false"
      />
      <button class="add-button" @click="addItemFromQuery">Add</button>
    </div>

    <div
      v-if="showSuggestions && suggestions.length"
      class="suggestions-dropdown"
    >
      <ul>
        <li
          v-for="(suggestion, index) in suggestions"
          :key="suggestion"
          :class="{ active: index === activeIndex }"
          @click="selectSuggestion(suggestion)"
          v-html="highlightMatch(suggestion)"
        ></li>
      </ul>
    </div>

    <div class="search-history" v-if="searchHistory.length">
      <div
        v-for="(term, index) in searchHistory"
        :key="index"
        class="history-item"
      >
        {{ term }}
        <button @click="removeFromHistory(index)" class="remove-button">
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getSuggestions, findEmoji } from "./get_emoji.js";

export default {
  name: "ManualBox",
  data() {
    return {
      searchQuery: "",
      searchHistory: [],
      // --- Autocomplete State ---
      suggestions: [],
      showSuggestions: false,
      activeIndex: -1,
      debounceTimer: null,
    };
  },
  methods: {
    // --- Autocomplete Methods ---
    handleInput() {
      // Debounce the search function
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        if (this.searchQuery.trim() === "") {
          this.showSuggestions = false;
          return;
        }
        this.suggestions = getSuggestions(this.searchQuery);
        this.showSuggestions = this.suggestions.length > 0;
        this.activeIndex = -1; // Reset selection on new input
      }, 250); // 250ms delay
    },

    onArrowDown() {
      if (!this.showSuggestions) return;
      if (this.activeIndex < this.suggestions.length - 1) {
        this.activeIndex++;
      }
    },

    onArrowUp() {
      if (!this.showSuggestions) return;
      if (this.activeIndex > 0) {
        this.activeIndex--;
      }
    },

    onEnter() {
      if (this.activeIndex !== -1) {
        // If a suggestion is highlighted, add it
        this.selectSuggestion(this.suggestions[this.activeIndex]);
      } else {
        // Otherwise, add the raw query
        this.addItemFromQuery();
      }
    },

    selectSuggestion(suggestion) {
      this.searchQuery = suggestion;
      this.showSuggestions = false;
      this.addItemFromQuery();
    },

    // --- History Management ---
    addItemFromQuery() {
      this.addTermToHistory(this.searchQuery);
      this.searchQuery = "";
      this.showSuggestions = false;
    },

    addTermToHistory(term) {
      const normalized = term.trim().toLowerCase();
      if (!normalized) return;

      const exists = this.searchHistory.some(
        (it) => it.split(" ")[0].toLowerCase() === normalized
      );
      if (exists) {
        return;
      }

      const emoji = findEmoji(normalized);
      // Smartly add with or without emoji
      const itemToAdd = emoji ? `${normalized} ${emoji}` : normalized;

      this.searchHistory.unshift(itemToAdd);
      this.$emit("items-updated", [...this.searchHistory]);
    },

    removeFromHistory(index) {
      this.searchHistory.splice(index, 1);
      this.$emit("items-updated", [...this.searchHistory]);
    },

    // --- UI Helper ---
    highlightMatch(suggestion) {
      const query = this.searchQuery.toLowerCase();
      const suggestionLower = suggestion.toLowerCase();
      const index = suggestionLower.indexOf(query);

      if (index === -1) return suggestion;

      const before = suggestion.slice(0, index);
      const match = suggestion.slice(index, index + query.length);
      const after = suggestion.slice(index + query.length);

      return `${before}<strong>${match}</strong>${after}`;
    },
  },
};
</script>

<style scoped>
/* ------- layout ------- */
.search-wrapper {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  position: relative; /* Crucial for positioning the dropdown */
}

.search-input-container {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

/* ------- input ------- */
.search-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  outline: none;
  color: white;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  border-color: #ffa500;
  box-shadow: 0 0 0 2px rgba(255, 165, 0, 0.2);
}

/* ------- add button ------- */
.add-button {
  padding: 12px 24px;
  background: #ffa500;
  color: #191b31;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-button:hover {
  background: #ff8c00;
  transform: translateY(-2px);
}

/* Suggestions Dropdown ------- */
.suggestions-dropdown {
  position: absolute;
  width: 100%;
  background: #2c2f48;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin-top: -4px;
  z-index: 10;
  max-height: 220px; /* Limit height and make it scrollable */
  overflow-y: auto;
  backdrop-filter: blur(10px);
}

.suggestions-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 4px;
}

.suggestions-dropdown li {
  padding: 10px 16px;
  color: white;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
}

.suggestions-dropdown li:hover {
  background-color: rgba(255, 165, 0, 0.2);
}

.suggestions-dropdown li.active {
  background-color: rgba(255, 165, 0, 0.4);
}

/* Use deep selector for highlighting inside v-html */
.suggestions-dropdown li :deep(strong) {
  color: #ffa500;
  font-weight: 600;
}

/* ------- history list ------- */
.search-history {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px; /* Added margin to separate from input */
}

.history-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: rgba(255, 165, 0, 0.2);
  border: 1px solid rgba(255, 165, 0, 0.3);
  border-radius: 8px;
  font-size: 14px;
  color: white;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.history-item:hover {
  background: rgba(255, 165, 0, 0.3);
  transform: translateY(-2px);
}

/* ------- remove button ------- */
.remove-button {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  padding: 0 4px;
  margin-left: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-button:hover {
  color: white;
  transform: scale(1.2);
}
</style>
