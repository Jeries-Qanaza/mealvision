import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Our_Model from "../views/Model.vue";
import NotFound from "../views/NotFound.vue";

const routes = [
  { path: "/", name: "Home-vue", component: Home },
  { path: "/model", name: "Model", component: Our_Model },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: NotFound },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
