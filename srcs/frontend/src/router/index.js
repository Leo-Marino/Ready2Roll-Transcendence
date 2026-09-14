import { createRouter, createWebHistory } from 'vue-router'
import CreateEvent from '../vue/ownerEventVisual.vue'
// import LoginPage from '../vue/loginPage.vue'
// import SignupPage from '../vue/signupPage.vue'
// import HomePage from '../vue/HomePage.vue'

const routes = [
  {
    path: '/',
      name: 'create-event',
      component: CreateEvent
  //   path: '/login',
  //   name: 'Login',
  //   component: LoginPage
  // },
  // {
  //   path: '/signup',
  //   name: 'Signup',
  //   component: SignupPage
  // },
  // {
  //   path: '/',
  //   redirect: '/login'
  // },
  // {
  //   path: '/home',
  //   name: 'home',
  //   component: HomePage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
