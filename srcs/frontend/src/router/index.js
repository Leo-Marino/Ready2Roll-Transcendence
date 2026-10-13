import { createRouter, createWebHistory } from 'vue-router'
import CreateEvent from '../vue/ownerEventCreate.vue'
import ViewEvent from '../vue/ownerEventView.vue'
import LoginPage from '../vue/loginPage.vue'
import SignupPage from '../vue/signupPage.vue'
import HomePage from '../vue/HomePage.vue'
import ChatView from '../vue/ChatView.vue';
import ProfileView from '../vue/ProfileView.vue';
import SubscriptionsView from '../vue/SubscriptionsView.vue';
import NotFound from '../vue/NotFound.vue';

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
{
	path: '/home',
	name: 'home',
	component: HomePage,
	// meta: { requiresAuth: true }
},
{
	path: '/chat',
	name: 'chat',
	component: ChatView,
	// meta: { requiresAuth: true }
},
{
	path: '/profile',
	name: '/profile',
	component: ProfileView,
	// meta: { requiresAuth: true }
},
{
	path: '/subscriptions',
	name: 'subscriptions',
	component: SubscriptionsView,
	// meta: { requiresAuth: true }
},
{
	path: '/CreateEvent',
	name: 'CreateEvent',
	component: CreateEvent,
	// meta: { requiresAuth: true }
},
{
	path: '/ViewEvent',
	name: 'ViewEvent',
	component: ViewEvent,
	// meta: { requiresAuth: true }
},
{
	path: '/:pathMatch(.*)*',
	name: 'NotFound',
	component: NotFound
}
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

// router.beforeEach((to, from, next) => {
// 	const token = localStorage.getItem('access'); // check if the access token exists or not

// 	if (to.meta.requiresAuth && !token)// if the page asks for authentication and the token does not exist, redirect to login page
// 		next('/login');
// 	else
// 		next();
// });

// DECOMMENT ALL ABOVE TO ENABLE AUTHENTICATION CHECKING !! and to test ofc

export default router
