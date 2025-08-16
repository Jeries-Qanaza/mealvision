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
        <span v-html="highlightMatch(item.text)"></span>
        <span v-if="item.emoji"> {{ item.emoji }} </span>
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
  data() {
    return {
      searchQuery: "",
      searchHistory: [], // store objects {text, emoji}
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
    // Sync history from parent
    syncWithExistingItems(existingItems) {
      this.searchHistory =
        existingItems && existingItems.length
          ? existingItems.map((term) => ({
              text: term,
              emoji: findEmoji(term),
            }))
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
      // If a suggestion is actively highlighted (by mouse or arrows), select it
      if (this.activeIndex !== -1) {
        this.selectSuggestion(this.suggestions[this.activeIndex]);
      }
      // If no suggestion is highlighted, but the list is visible, select the first one
      else if (this.showSuggestions && this.suggestions.length > 0) {
        this.selectSuggestion(this.suggestions[0]);
      }
      // Otherwise (if the list is not visible), add what the user typed
      else {
        this.addItemFromQuery();
      }
    },

    selectSuggestion(suggestion) {
      this.searchQuery = suggestion;
      this.showSuggestions = false;
      this.addItemFromQuery();
    },

    // Add to history
    addItemFromQuery() {
      const term = this.searchQuery.trim();
      if (!term) return;

      const exists = this.searchHistory.some(
        (it) => it.text.toLowerCase() === term.toLowerCase()
      );
      if (exists) {
        this.searchQuery = "";
        this.showSuggestions = false;
        return;
      }

      const emoji = findEmoji(term);
      this.searchHistory.unshift({ text: term, emoji });
      this.$emit(
        "items-updated",
        this.searchHistory.map(
          (it) => `${it.text}${it.emoji ? " " + it.emoji : ""}`
        )
      );

      this.searchQuery = "";
      this.showSuggestions = false;
    },

    removeFromHistory(index) {
      this.searchHistory.splice(index, 1);
      this.$emit(
        "items-updated",
        this.searchHistory.map(
          (it) => `${it.text}${it.emoji ? " " + it.emoji : ""}`
        )
      );
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
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this.handleClickOutside);
  },
};
</script>
