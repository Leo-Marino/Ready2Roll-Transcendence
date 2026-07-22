import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../vue/loginPage.vue'
import SignupPage from '../vue/signupPage.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupPage
  },
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router