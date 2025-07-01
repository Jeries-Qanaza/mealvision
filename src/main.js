// src/main.js

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// PrimeVue Import
import PrimeVue from "primevue/config";

// --- PATHS FOR PRIMEVUE v4 ---
import "primevue/themes/lara-light-indigo/theme.css"; // Theme, can be change
import "primevue/core/primevue.min.css"; // Core CSS
import "primeicons/primeicons.css"; // Icons

const app = createApp(App);

app.use(router);

// Use PrimeVue with ripple effect enabled
app.use(PrimeVue, { ripple: true });

app.mount("#app");
