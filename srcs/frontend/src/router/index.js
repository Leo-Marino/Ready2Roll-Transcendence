import { createRouter, createWebHistory } from 'vue-router'
import CreateEvent from '../vue/ownerEventCreate.vue'
import ViewEvent from '../vue/ownerEventView.vue'
import LoginPage from '../vue/loginPage.vue'
import SignupPage from '../vue/signupPage.vue'
import HomePage from '../vue/HomePage.vue'
import ChatView from '../vue/ChatView.vue';
import ProfileView from '../vue/ProfileView.vue';
import SubscriptionsView from '../vue/SubscriptionsView.vue';
import OtherUserProfileView from '../vue/OtherUserProfileView.vue';
import SearchView from '../vue/SearchView.vue'

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
  },
  // {
  //   path: '/home',
  //   name: 'home',
  //   component: HomePage
  // },
  { path: '/home',          name: 'home',          component: HomePage, props: { mode: 'for_you' } },
  { path: '/discover',      name: 'discover',      component: HomePage, props: { mode: 'discover' } },
  { path: '/subscriptions', name: 'subscriptions', component: HomePage, props: { mode: 'following' } },
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
  // {
  //   path: '/subscriptions',
  //   name: 'subscriptions',
  //   component: SubscriptionsView
  // },
  {
    path: '/CreateEvent',
    name: 'CreateEvent',
    component: CreateEvent
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: OtherUserProfileView
  },
{
    path: '/ViewEvent',
    redirect: '/profile'
  },

  { path: '/search', name: 'search', component: SearchView },
]

const router = createRouter({
	history: createWebHistory(),
	routes
})


export default router
