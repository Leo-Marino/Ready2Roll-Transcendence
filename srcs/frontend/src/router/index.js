import { createRouter, createWebHistory } from 'vue-router'
import CreateEvent from '../vue/ownerEventCreate.vue'
import LoginPage from '../vue/loginPage.vue'
import SignupPage from '../vue/signupPage.vue'
import HomePage from '../vue/HomePage.vue'
import ChatView from '../vue/ChatView.vue';
import LegalView from '../vue/LegalView.vue'
import NotFound from '../vue/NotFound.vue'
import ProfileView from '../vue/ProfileView.vue';
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
    path: '/chat',
    name: 'chat',
    component: ChatView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/CreateEvent',
    name: 'CreateEvent',
    component: CreateEvent,
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
    {
    path: '/privacy',
    name: 'privacy',
     component: LegalView
  },
    { path: '/terms',
    name: 'terms',
    component: LegalView
  },
    { path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound
  },
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

// === HADA HWA L-3ESSASS (Navigation Guard) ===
router.beforeEach((to, from) => {

  const token = sessionStorage.getItem('token');

  const userType = sessionStorage.getItem('type_of_user');

  if (to.meta.requiresAuth && !token) {
    return ('/login');
  } else if (to.meta.requiresBusiness && (!userType || userType.toLowerCase() !== 'business')) {
    return ('/home');
  } else if (to.meta.guestOnly && token) {
    return ('/home');
  } else {
    return true;
  }
})

export default router
