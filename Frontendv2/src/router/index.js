import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../components/UploadPage.vue'
import NavBar from '../components/NavBar.vue'  

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/upload',
    name: 'UploadPage',
    component: UploadPage
  },
  {
    path: '/navBar',
    name: 'NavBar',
    component: NavBar
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router