import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import About from '../views/About.vue';
import Contact from '../views/Contact.vue';
import signIn from '../views/Sign_in.vue';
import signUp from '../views/Sign_up.vue';
import Our_Model from '../views/Model.vue';
import NotFound from '../views/NotFound.vue';



const routes = [
  { path: '/', name: 'Home-vue', component: Home },
  { path: '/about', name: 'About', component: About },
  { path: '/contact', name: 'Contact', component: Contact },
  { path: '/signIn', name: 'signIn', component: signIn },
  { path: '/signUp', name: 'signUp', component: signUp },
  { path: '/model', name: 'Model', component: Our_Model },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
