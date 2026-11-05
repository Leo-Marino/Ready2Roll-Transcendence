import { ref } from 'vue';

export const currentLang = ref(localStorage.getItem('lang') || 'en');

export const messages = {
  en: {
    forYou: 'For you',
    subscriptions: 'Subscriptions',
    discover: 'Discover',
    search: 'Search...',
    following: 'following',
    followers: 'followers',
    editProfile: 'Edit Profile',
    createEvent: 'Create Event',
    logout: 'Logout',
    myEvents: 'My Events',
    likes: 'Likes'
  },
  fr: {
    forYou: 'Pour toi',
    subscriptions: 'Abonnements',
    discover: 'Découvrir',
    search: 'Rechercher...',
    following: 'abonnements',
    followers: 'abonnés',
    editProfile: 'Modifier le profil',
    createEvent: 'Créer un événement',
    logout: 'Déconnexion',
    myEvents: 'Mes événements',
    likes: 'J’aime'
  },
  ar: {
    forYou: 'لك',
    subscriptions: 'الاشتراكات',
    discover: 'اكتشف',
    search: 'بحث...',
    following: 'يتابع',
    followers: 'متابعون',
    editProfile: 'تعديل الحساب',
    createEvent: 'إنشاء حدث',
    logout: 'تسجيل الخروج',
    myEvents: 'أحداثي',
    likes: 'الإعجابات'
  }
};

export const setLanguage = (lang) => {
  currentLang.value = lang;
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
};

// Apply saved language direction on load
setLanguage(currentLang.value);

export const t = (key) => {
  return messages[currentLang.value]?.[key] || messages.en[key] || key;
};
