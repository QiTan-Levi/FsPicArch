import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/HomePage.vue'
import Login from '../components/login.vue'
import Register from '../components/register.vue'
import Upload from '../components/UploadPage.vue'
import Profile from '../components/ProfilePage.vue'
import uu from '../components/uu.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/account/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/account/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: { requiresAuth: true } // 这个路由需要认证

  },
  {
    path: '/my-profile',
    name: 'Profile',
    component: Profile,
  },
  {
    path: '/uu',
    name: 'uu',
    component: uu,
  }

];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'), // Use import.meta.env for environment variables
  routes
});

export default router;