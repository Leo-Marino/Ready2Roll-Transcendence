import { createRouter, createWebHistory } from 'vue-router'
import CreateEvent from '../vue/ownerEventCreate.vue'
import LoginPage from '../vue/loginPage.vue' // comment this to test other pages n therefore to put privilege on
import SignupPage from '../vue/signupPage.vue' // ```
import HomePage from '../vue/HomePage.vue' // ```
import ChatView from '../vue/ChatView.vue';
import ProfileView from '../vue/ProfileView.vue';

const routes = [
  {
    // decomment this to test other pages n therefore to put privilege on
    // path: '/',
    //   name: 'create-event',
    //   component: CreateEvent
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
  },
  {
    path: '/home',
    name: 'home',
    component: HomePage
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView
  },
  {
    path: '/profile',
    name: '/profile',
    component: ProfileView
  },
  {
    path: '/CreateEvent',
    name: 'CreateEvent',
    component: CreateEvent
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
