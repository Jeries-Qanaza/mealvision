<template>
  <div class="search-wrapper">
    <div class="search-input-container">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Add Item"
        class="search-input"
        @keyup.enter="addToHistory"
      />
      <button class="add-button" @click="addToHistory">Add</button>
    </div>
    <div class="search-history" v-if="searchHistory.length > 0">
      <div 
        v-for="(term, index) in searchHistory" 
        :key="index"
        class="history-item"
      >
        {{ term }}
        <button
          @click="removeFromHistory(index)"
          class="remove-button"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ManualBox",
  data() {
    return {
      searchQuery: '',
      searchHistory: []
    }
  },
  methods: {
    addToHistory() {
      if (this.searchQuery.trim()) {
        this.searchHistory.unshift(this.searchQuery.trim());
        this.searchQuery = '';

        console.log("Manula Input: " + this.searchHistory);

        this.$emit('items-updated', this.searchHistory);
      }
    },
    removeFromHistory(index) {
      this.searchHistory.splice(index, 1);
      this.$emit('items-updated', this.searchHistory);
    }
  }
}
</script>

<style scoped>
.search-wrapper {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.search-input-container {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
  color: white;
  backdrop-filter: blur(5px);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  border-color: #FFA500;
  box-shadow: 0 0 0 2px rgba(255, 165, 0, 0.2);
}

.add-button {
  padding: 12px 24px;
  background: #FFA500;
  color: #191b31;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-button:hover {
  background: #FF8C00;
  transform: translateY(-2px);
}

.search-history {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
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