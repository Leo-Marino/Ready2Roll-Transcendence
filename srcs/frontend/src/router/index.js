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
    component: LoginPage,
    meta: { guestOnly: true } // Khassa ghir b li baqi ma dar login
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupPage,
    meta: { guestOnly: true }
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/home',
    name: 'home',
    component: HomePage,
    props: { mode: 'for_you' },
    meta: { requiresAuth: true } // Khassk tkon logé
  },
  {
    path: '/discover',
    name: 'discover',
    component: HomePage,
    props: { mode: 'discover' },
    meta: { requiresAuth: true }
  },
  {
    path: '/subscriptions',
    name: 'subscriptions',
    component: HomePage,
    props: { mode: 'following' },
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile', // Sme7 lia beddelt lik '/profile' b 'profile' (name dyal route 7ssen ykon bla '/')
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/CreateEvent',
    name: 'CreateEvent',
    component: CreateEvent,
    // Hna zedna requiresBusiness bach n-7ebsou l-comptat l-3adiyin
    meta: { requiresAuth: true, requiresBusiness: true }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: OtherUserProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/ViewEvent',
    redirect: '/profile'
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

// === HADA HWA L-3ESSASS (Navigation Guard) ===
router.beforeEach((to, from) => {
  // Kan-qraw l-token mn sessionStorage wla localStorage
  const token = sessionStorage.getItem('token');

  // Kan-qraw type d l-user (khassk tkon katsauvegardih f loginPage)
  const userType = sessionStorage.getItem('type_of_user');

  if (to.meta.requiresAuth && !token) {
    // 1. Bgha ydkhl l-page d nas li logé, w howa ma 3ndouch token -> lo7o l-Login
    return ('/login');
  } else if (to.meta.requiresBusiness && userType !== 'business') {
    // 2. Bgha ydkhl l-CreateEvent, w howa 3ndo token walakin machi "business" -> lo7o l-Home
    return ('/home');
  } else if (to.meta.guestOnly && token) {
    // 3. Howa m-logé, w bgha ydkhl l-page d Login wla Signup -> lo7o l-Home (ma 3ndo maydir bihom)
    return ('/home');
  } else {
    // 4. Kolchi mzyan, khelsso ydkhl l-page
    return true;
  }
})

export default router
