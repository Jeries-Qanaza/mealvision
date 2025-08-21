<template>
  <div class="search-wrapper" ref="searchWrapper">
    <!-- Input & Add button -->
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

    <!-- Suggestions dropdown -->
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
          @mouseover="activeIndex = index"
          v-html="highlightMatch(suggestion)"
        ></li>
      </ul>
    </div>

    <!-- Search history -->
    <div class="search-history" v-if="searchHistory.length">
      <div
        class="history-item"
        v-for="(item, index) in searchHistory"
        :key="index"
      >
        <span v-html="highlightMatch(item)"></span>
        <span v-if="findEmoji(item)"> {{ findEmoji(item) }} </span>
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
  props: {
    existingItems: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["manual-items-updated"],
  data() {
    return {
      searchQuery: "",
      searchHistory: [], // store only plain text
      suggestions: [],
      showSuggestions: false,
      activeIndex: -1,
      debounceTimer: null,
    };
  },
  watch: {
    existingItems: {
      handler(newItems) {
        this.syncWithExistingItems(newItems);
      },
      immediate: true,
      deep: true,
    },
    showSuggestions(isShown) {
      if (isShown) {
        document.addEventListener("mousedown", this.handleClickOutside);
      } else {
        document.removeEventListener("mousedown", this.handleClickOutside);
      }
    },
  },
  methods: {
    // Sync history from parent (store only plain text)
    syncWithExistingItems(existingItems) {
      this.searchHistory = existingItems && existingItems.length
        ? existingItems.map(term => term.trim())
        : [];
    },

    // Input handling & autocomplete
    handleInput() {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        if (!this.searchQuery.trim()) {
          this.showSuggestions = false;
          return;
        }
        this.suggestions = getSuggestions(this.searchQuery);
        this.showSuggestions = this.suggestions.length > 0;
        this.activeIndex = -1;
      }, 250);
    },

    onArrowDown() {
      if (!this.showSuggestions) return;
      if (this.activeIndex < this.suggestions.length - 1) this.activeIndex++;
    },

    onArrowUp() {
      if (!this.showSuggestions) return;
      if (this.activeIndex > 0) this.activeIndex--;
    },

    onEnter() {
      if (this.activeIndex !== -1) {
        this.selectSuggestion(this.suggestions[this.activeIndex]);
      } else if (this.showSuggestions && this.suggestions.length > 0) {
        this.selectSuggestion(this.suggestions[0]);
      } else {
        this.addItemFromQuery();
      }
    },

    selectSuggestion(suggestion) {
      this.searchQuery = suggestion;
      this.showSuggestions = false;
      this.addItemFromQuery();
    },

    // Add to history (store plain text only)
    addItemFromQuery() {
      const term = this.searchQuery.trim();
      if (!term) return;

      // Normalize duplicate check
      const exists = this.searchHistory.some(
        it => it.toLowerCase() === term.toLowerCase()
      );
      if (exists) {
        this.searchQuery = "";
        this.showSuggestions = false;
        return;
      }

      // Add plain text only
      this.searchHistory.unshift(term);
      this.$emit("manual-items-updated", [...this.searchHistory]);

      this.searchQuery = "";
      this.showSuggestions = false;
    },

    removeFromHistory(index) {
      this.searchHistory.splice(index, 1);
      this.$emit("manual-items-updated", [...this.searchHistory]);
    },

    // Highlight query match in text
    highlightMatch(text) {
      if (!this.searchQuery) return text;
      const query = this.searchQuery.toLowerCase();
      const index = text.toLowerCase().indexOf(query);
      if (index === -1) return text;

      const before = text.slice(0, index);
      const match = text.slice(index, index + query.length);
      const after = text.slice(index + query.length);

      return `${before}<strong>${match}</strong>${after}`;
    },

    handleClickOutside(event) {
      if (
        this.$refs.searchWrapper &&
        !this.$refs.searchWrapper.contains(event.target)
      ) {
        this.showSuggestions = false;
      }
    },

    // Expose emoji helper for template
    findEmoji(term) {
      return findEmoji(term);
    },
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this.handleClickOutside);
  },
};
</script>
