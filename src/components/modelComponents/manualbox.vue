<template>
  <div class="search-wrapper" ref="searchWrapper">
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

    // --- Event Handling ---
    handleClickOutside(event) {
      // Check if the click was outside the component's main wrapper
      if (
        this.$refs.searchWrapper &&
        !this.$refs.searchWrapper.contains(event.target)
      ) {
        this.showSuggestions = false;
      }
    },
  },

  watch: {
    // Watch for changes on showSuggestions to add/remove the event listener
    showSuggestions(isShown) {
      if (isShown) {
        // When the dropdown opens, start listening for clicks anywhere on the page
        document.addEventListener("mousedown", this.handleClickOutside);
      } else {
        // When it closes, stop listening to prevent unnecessary checks
        document.removeEventListener("mousedown", this.handleClickOutside);
      }
    },
  },

  beforeUnmount() {
    // Clean up the listener when the component is destroyed to prevent memory leaks
    document.removeEventListener("mousedown", this.handleClickOutside);
  },
};
</script>
