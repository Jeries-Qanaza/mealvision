import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// PrimeVue Import
import PrimeVue from "primevue/config";

// Paths for PrimeVue v3+
import "primevue/resources/themes/lara-light-indigo/theme.css"; // A popular default theme
import "primevue/resources/primevue.min.css"; // Core CSS
import "primeicons/primeicons.css"; // Icons

const app = createApp(App);
app.use(router);

// Use PrimeVue with ripple effect enabled
app.use(PrimeVue, { ripple: true });
app.mount("#app");
