<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import LanguageSwitcher from './LanguageSwitcher.vue';
import { currentLang } from '../i18n';

const route = useRoute();
const router = useRouter();

const activeTab = computed(() => (route.path === '/terms' ? 'terms' : 'privacy'));

const copy = {
  en: {
    back: 'Back',
    privacyTab: 'Privacy Policy',
    termsTab: 'Terms of Service',
    updated: 'Last updated: May 2026',
    privacyIntro:
      'Ready2Roll ("we", "our", or "the Platform") respects your privacy and is committed to protecting the personal data of both Standard Users and Business Organizers.',
    privacySections: [
      {
        title: '1. Information We Collect',
        body: 'We collect account details provided at registration (username, email address, hashed password, and for Business accounts, legal venue name and VAT/Tax ID), profile customization data (avatar image, bio, preferred music tags), and user-generated activity (published events, uploaded event photos/videos, likes, comments, reactions, subscriptions, and direct messages).'
      },
      {
        title: '2. How We Use Your Data',
        body: 'Your information is used strictly to operate Ready2Roll: authenticating your sessions via JWT, personalizing your "For You" and "Discover" event feeds using our tag and engagement recommendation engine, delivering real-time WebSocket notifications and direct messages, and answering event questions through our AI assistant Rolly.'
      },
      {
        title: '3. Media Storage & Security',
        body: 'Uploaded avatars and event media are stored in our isolated MinIO object storage bucket and automatically purged via django-cleanup when replaced or deleted. All secrets and credentials are encrypted and managed via HashiCorp Vault, and all traffic is protected over HTTPS by our OWASP ModSecurity Web Application Firewall (WAF).'
      },
      {
        title: '4. Your Rights & Data Deletion',
        body: 'You can update your profile information, change your avatar, modify your music tags, or delete your published events at any time from your Profile page. We never sell or rent your personal data to third-party advertisers.'
      }
    ],
    termsIntro:
      'By creating an account or using Ready2Roll, you agree to comply with and be bound by the following Terms of Service.',
    termsSections: [
      {
        title: '1. Account Eligibility & Roles',
        body: 'Ready2Roll offers two account types: Standard accounts for discovering events and interacting socially, and Business accounts for verified venues and event organizers. Business account holders must provide accurate legal venue names and valid VAT/Tax identification numbers.'
      },
      {
        title: '2. User Conduct & Content Standards',
        body: 'You are solely responsible for the comments, reactions, direct messages, and event media you upload. Harassment, hate speech, spam, unauthorized commercial solicitation, or uploading unlawful or copyrighted media without permission is strictly prohibited.'
      },
      {
        title: '3. Event Listings & Accuracy',
        body: 'Business organizers must ensure that event titles, dates, locations, ticket prices, and maximum capacities are accurate. Ready2Roll acts as a discovery and social platform and is not liable for venue cancellations, schedule changes, or third-party ticket transactions.'
      },
      {
        title: '4. Platform Security & Fair Use',
        body: 'Attempting to bypass our Web Application Firewall (WAF), abuse API rate limits (including the Rolly AI assistant quota), or disrupt WebSocket services will result in immediate account suspension.'
      }
    ]
  },
  fr: {
    back: 'Retour',
    privacyTab: 'Politique de Confidentialité',
    termsTab: "Conditions d'Utilisation",
    updated: 'Dernière mise à jour : Mai 2026',
    privacyIntro:
      'Ready2Roll (« nous » ou « la Plateforme ») respecte votre vie privée et protège les données personnelles des utilisateurs standards et des comptes professionnels.',
    privacySections: [
      {
        title: '1. Données Collectées',
        body: "Nous collectons les informations d'inscription (nom d'utilisateur, e-mail, mot de passe haché, et pour les comptes professionnels, nom légal et numéro de TVA), les données de profil (avatar, bio, tags musicaux) ainsi que vos interactions (événements publiés, médias, likes, commentaires, abonnements et messages directs)."
      },
      {
        title: '2. Utilisation des Données',
        body: 'Vos données servent uniquement à faire fonctionner Ready2Roll : authentification JWT, personnalisation du fil « Pour toi » et « Découvrir », notifications et messagerie en temps réel via WebSockets, et réponses contextuelles via notre assistant IA Rolly.'
      },
      {
        title: '3. Stockage & Sécurité',
        body: 'Les médias sont stockés sur MinIO et supprimés automatiquement lorsqu’ils sont remplacés ou effacés. Les secrets sont protégés par HashiCorp Vault et le trafic HTTPS est filtré par notre pare-feu applicatif ModSecurity (WAF).'
      },
      {
        title: '4. Vos Droits',
        body: 'Vous pouvez modifier votre profil, vos tags ou supprimer vos événements à tout moment depuis votre page Profil. Vos données ne sont jamais vendues à des tiers.'
      }
    ],
    termsIntro:
      "En créant un compte ou en utilisant Ready2Roll, vous acceptez de respecter les présentes Conditions d'Utilisation.",
    termsSections: [
      {
        title: '1. Comptes & Rôles',
        body: 'Ready2Roll propose des comptes Standards (découverte et interactions sociales) et des comptes Professionnels (organisateurs et clubs). Les comptes professionnels doivent fournir une raison sociale et un numéro de TVA valides.'
      },
      {
        title: '2. Règles de Conduite',
        body: 'Vous êtes responsable des commentaires, messages et médias que vous publiez. Tout contenu illicite, diffamatoire, spam ou portant atteinte aux droits d’auteur est strictement interdit.'
      },
      {
        title: '3. Exactitude des Événements',
        body: 'Les organisateurs doivent indiquer des informations exactes (dates, lieux, tarifs, capacité). Ready2Roll est une plateforme de découverte et ne saurait être tenue responsable des annulations d’événements.'
      },
      {
        title: '4. Sécurité de la Plateforme',
        body: 'Toute tentative de contournement du pare-feu WAF, d’abus des limites de requêtes API ou de perturbation des WebSockets entraînera la suspension immédiate du compte.'
      }
    ]
  },
  ar: {
    back: 'رجوع',
    privacyTab: 'سياسة الخصوصية',
    termsTab: 'شروط الخدمة',
    updated: 'آخر تحديث: مايو 2026',
    privacyIntro:
      'تحترم منصة Ready2Roll خصوصيتك وتلتزم بحماية البيانات الشخصية لجميع المستخدمين ومنظمي الفعاليات.',
    privacySections: [
      {
        title: '1. البيانات التي نجمعها',
        body: 'نجمع بيانات التسجيل (اسم المستخدم، البريد الإلكتروني، كلمة المرور المشفرة، ولحسابات الأعمال الاسم القانوني والرقم الضريبي)، وبيانات الملف الشخصي (الصورة، النبذة، الوسوم الموسيقية)، والتفاعلات (الأحداث المنشورة، الصور والفيديوهات، الإعجابات، التعليقات، والرسائل المباشرة).'
      },
      {
        title: '2. كيفية استخدام البيانات',
        body: 'تُستخدم بياناتك حصرياً لتشغيل المنصة: مصادقة الجلسات عبر JWT، تخصيص خلاصة الأحداث عبر نظام التوصيات، إرسال الإشعارات والرسائل الفورية عبر WebSockets، والإجابة على استفسارات الأحداث عبر المساعد الذكي Rolly.'
      },
      {
        title: '3. أمن وتخزين الوسائط',
        body: 'يتم تخزين الوسائط في خدمة MinIO المعزولة وحذفها تلقائياً عند إزالتها. تُدار جميع المفاتيح السرية بواسطة HashiCorp Vault وتُحمى جميع الاتصالات عبر HTTPS وجدار الحماية ModSecurity WAF.'
      },
      {
        title: '4. حقوق المستخدم',
        body: 'يمكنك تعديل بيانات حسابك أو وسومك أو حذف أحداثك في أي وقت من صفحة الملف الشخصي. نحن لا نبيع بياناتك لأي طرف ثالث.'
      }
    ],
    termsIntro:
      'من خلال إنشاء حساب أو استخدام منصة Ready2Roll، فإنك توافق على الالتزام بشروط الخدمة التالية.',
    termsSections: [
      {
        title: '1. أهلية الحساب والأدوار',
        body: 'توفر المنصة نوعين من الحسابات: حسابات قياسية للمستخدمين، وحسابات أعمال لمنظمي الفعاليات والأندية. يجب على حسابات الأعمال تقديم اسم قانوني ورقم ضريبي صحيحين.'
      },
      {
        title: '2. سلوك المستخدم والمحتوى',
        body: 'أنت مسؤول بالكامل عن التعليقات والرسائل والوسائط التي ترفعها. يُمنع منعاً باتاً نشر أي محتوى مسيء أو غير قانوني أو ينتهك حقوق الملكية الفكرية.'
      },
      {
        title: '3. دقة معلومات الفعاليات',
        body: 'يلتزم منظمو الفعاليات بتقديم معلومات دقيقة حول المواعيد والمواقع وأسعار التذاكر والسعة القصوى. المنصة غير مسؤولة عن إلغاء الفعاليات من قِبل المنظمين.'
      },
      {
        title: '4. أمن المنصة والاستخدام العادل',
        body: 'أي محاولة لتجاوز جدار الحماية WAF أو إساءة استخدام حدود طلبات النظام أو المساعد الذكي ستؤدي إلى إيقاف الحساب فوراً.'
      }
    ]
  }
};

const content = computed(() => copy[currentLang.value] || copy.en);

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/login');
  }
};
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
    <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="legal-page">
    <header class="legal-navbar glass-panel">
      <div class="logo" @click="router.push('/home')">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
        <span class="logo-text">Ready2Roll</span>
      </div>

      <div class="legal-nav-right">
        <LanguageSwitcher />
        <button class="back-btn" @click="goBack">← {{ content.back }}</button>
      </div>
    </header>

    <main class="legal-card glass-panel">
      <div class="legal-tabs">
        <router-link to="/privacy" class="legal-tab" :class="{ active: activeTab === 'privacy' }">
          {{ content.privacyTab }}
        </router-link>
        <router-link to="/terms" class="legal-tab" :class="{ active: activeTab === 'terms' }">
          {{ content.termsTab }}
        </router-link>
      </div>

      <p class="legal-updated">{{ content.updated }}</p>

      <article v-if="activeTab === 'privacy'" class="legal-body">
        <h1>{{ content.privacyTab }}</h1>
        <p class="legal-intro">{{ content.privacyIntro }}</p>
        <section v-for="sec in content.privacySections" :key="sec.title" class="legal-section">
          <h2>{{ sec.title }}</h2>
          <p>{{ sec.body }}</p>
        </section>
      </article>

      <article v-else class="legal-body">
        <h1>{{ content.termsTab }}</h1>
        <p class="legal-intro">{{ content.termsIntro }}</p>
        <section v-for="sec in content.termsSections" :key="sec.title" class="legal-section">
          <h2>{{ sec.title }}</h2>
          <p>{{ sec.body }}</p>
        </section>
      </article>
    </main>
  </div>
</template>

<style scoped>
#bgVideo {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  object-fit: cover;
}

.legal-page {
  min-height: 100vh;
  padding: 15px 20px 40px;
  box-sizing: border-box;
  color: #ffffff;
  font-family: var(--font-main);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.glass-panel {
  background: rgba(20, 10, 40, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  backdrop-filter: blur(14px);
  box-sizing: border-box;
}

.legal-navbar {
  position: relative;
  z-index: 50;
  width: 100%;
  max-width: 920px;
  height: 60px;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.nav-logo-img {
  height: 35px;
  width: auto;
}

.logo-text {
  font-family: "Bruno Ace", sans-serif;
  font-weight: bold;
  font-size: 1.2rem;
}

.legal-nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  background: rgba(0, 242, 254, 0.16);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 7px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #00f2fe;
  color: #000;
}

.legal-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 920px;
  padding: 28px 32px;
}

.legal-tabs {
  display: flex;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding-bottom: 16px;
}

.legal-tab {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 8px 18px;
  border-radius: 12px;
  font-weight: bold;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.legal-tab.active,
.legal-tab:hover {
  color: #00f2fe;
  background: rgba(0, 242, 254, 0.12);
  border-color: rgba(0, 242, 254, 0.45);
}

.legal-updated {
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.82rem;
  margin: 14px 0 6px;
}

.legal-body h1 {
  font-family: "Bruno Ace", sans-serif;
  font-size: 1.5rem;
  color: #00f2fe;
  margin: 8px 0 12px;
}

.legal-intro {
  font-size: 0.98rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20px;
}

.legal-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 14px;
}

.legal-section h2 {
  font-size: 1.05rem;
  color: #00f2fe;
  margin: 0 0 8px;
}

.legal-section p {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.85);
}
</style>
