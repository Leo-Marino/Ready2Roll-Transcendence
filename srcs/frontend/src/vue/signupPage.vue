<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { z } from 'zod';
import LanguageSwitcher from '../vue/LanguageSwitcher.vue';
import { currentLang } from '../i18n';
import { t as $t } from '../i18n';
const router = useRouter();

const type_of_user = ref('standard'); // 'standard' | 'business'
const username = ref('');
const email = ref('');
const password = ref('');
const legalName = ref('');
const vatTax = ref('');
const showPasswordBox = ref(false);

const tags = ref('');
const availableTags = ref(['Disco', 'Pop', 'Rock', 'Hip-Hop', 'Jazz']);

const selectedTagsList = computed(() => {
    if (!tags.value) return [];
    return tags.value.split(',').map(t => t.trim()).filter(Boolean);
});

const toggleTag = (tagName) => {
    let currentTags = [...selectedTagsList.value];
    const index = currentTags.findIndex(t => t.toLowerCase() === tagName.toLowerCase());
    if (index > -1) {
        currentTags.splice(index, 1);
    } else {
        currentTags.push(tagName);
    }
    tags.value = currentTags.join(', ');
};

const isTagSelected = (tagName) => {
    return selectedTagsList.value.some(t => t.toLowerCase() === tagName.toLowerCase());
};

const passwordRules = computed(() => [
{
    id: 'length',
    label: $t('passReqLength'),
    valid: password.value.length >= 8
},
{
    id: 'uppercase',
    label: $t('passReqUpper'),
    valid: /[A-Z]/.test(password.value)
},
{
    id: 'number',
    label: $t('passReqNumber'),
    valid: /[0-9]/.test(password.value)
},
{
    id: 'special',
    label: $t('passReqSpecial'),
    valid: /[!@#$%^&*(),.?":{}|<>]/.test(password.value)
}
]);

const isPasswordValid = computed(() =>
    passwordRules.value.every(rule => rule.valid)
);

const errors = ref({});

const getSignupSchema = () => {
    const baseSchema = {
        username: z
            .string()
            .min(3, 'Username must be at least 3 characters')
            .regex(
                /^[A-Za-z0-9_.]+$/,
                'Usernames can only contain letters, numbers, underscores, and periods.'
            ),
        email: z
            .string()
            .min(1, 'E-mail is required')
            .email('Invalid email address'),
        password: z
            .string()
            .min(8, 'Password must be at least 8 characters')
            .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
            .regex(/[0-9]/, 'Must contain at least one number')
            .regex(/[!@#$%^&*(),.?|<>]/, 'Must contain at least one special character')
    };
    if (type_of_user.value === 'business') {
        baseSchema.legalName = z.string().min(1, 'Business / Venue Name is required');
        baseSchema.vatTax = z.string().min(1, 'Tax ID / VAT Number is required');
    }
    return z.object(baseSchema);
};

const handleFocusOut = (event) => {
    if (!event.currentTarget.contains(event.relatedTarget)) {
        showPasswordBox.value = false;
    }
};

const submitSignup = async () => {
    errors.value = {};
    const formData = {
        username: username.value,
        email: email.value,
        password: password.value,
        ...(type_of_user.value === 'business' && {
            legalName: legalName.value,
            vatTax: vatTax.value
        })
    };

    const validationResult = getSignupSchema().safeParse(formData);

    if (!validationResult.success) {
        const fieldErrors = {};
        validationResult.error.issues.forEach((issue) => {
            const fieldName = issue.path[0];
            if (fieldName) {
                if (!fieldErrors[fieldName]) {
                    fieldErrors[fieldName] = [];
                }
                fieldErrors[fieldName].push(issue.message);
            }
        });
        errors.value = fieldErrors;
        return;
    }

    const payload = {
        type_of_user: type_of_user.value,
        username: username.value,
        email: email.value,
        password: password.value,
        tags: selectedTagsList.value
    };

    if (type_of_user.value === 'business') {
        payload.legal_name = legalName.value;
        payload.vat_tax = vatTax.value;
    }

    try {
        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            if (data.token) {
                sessionStorage.setItem('token', data.token);
            }
            alert($t('signupSuccess'));
            router.push('/login');
        } else {
            console.error('Error message by the server:', data);
            alert(data.error || $t('signupFailed'));
        }
    } catch (error) {
        console.error('Network error: ', error);
        alert($t('networkError'));
    }
};
</script>

<template>
<video autoplay muted loop playsinline id="bgVideo">
<source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
</video>

<div class="wrapper">
        <div class="top-nav-icons">
            <LanguageSwitcher />
        </div>
<div class="signup-container">
    <div id="logoDiv" class="centred">
    <img src="../assets/logo_temp.png" alt="logo">
    </div>
    <div id="loginForm" class="centred">
    <form @submit.prevent="submitSignup" novalidate>

        <!-- Banner di errore generale in cima -->
        <div v-if="Object.keys(errors).length > 0" class="error-banner">
            <span>{{ $t('signupErrorBanner') }} </span>
        </div>

        <div class="role-toggle-container">
        <button
            type="button"
            :class="{'active-role': type_of_user === 'standard'}"
            @click="type_of_user = 'standard'; errors = {};">
            {{ $t('roleStandard') }}
        </button>
        <button
            type="button"
            :class="{'active-role': type_of_user === 'business'}"
            @click="type_of_user = 'business'; errors = {};">
            {{ $t('roleBusiness') }}
        </button>
        </div>

        <div class="inputFieldDiv">
        <input
            type="text"
            v-model="username"
            :placeholder="$t('signupUsername')"
            :class="{ 'input-error': errors.username }"
            :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
        >
        </div>

        <div class="inputFieldDiv">
        <input
            type="email"
            v-model="email"
            :placeholder="$t('signupEmail')"
            :class="{ 'input-error': errors.email }"
            :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
        >
        </div>

        <div
            class="inputFieldDiv password-group"
            tabindex="-1"
            @focusin="showPasswordBox = true"
            @focusout="handleFocusOut"
        >
            <input
                type="password"
                v-model="password"
                :placeholder="$t('signupPassword')"
                :class="{ 'input-error': errors.password }"
                @focus="showPasswordBox = true"
                @blur="showPasswordBox = false"
                :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
            />
            <div v-if="showPasswordBox" class="password-dropdown-box">
                <p class="password-box-title">{{ $t('passwordReqTitle') }}</p>
                <ul class="password-checklist">
                <li
                    v-for="rule in passwordRules"
                    :key="rule.id"
                    :class="rule.valid ? 'rule-valid' : 'rule-invalid'"
                >
                    <span class="rule-icon">{{ rule.valid ? '✓' : '✖' }}</span>
                    <span>{{ rule.label }}</span>
                </li>
                </ul>
            </div>
        </div>

        <!-- Campi Extra per business -->
        <div v-if="type_of_user === 'business'">
        <div class="inputFieldDiv">
            <input
                type="text"
                v-model="legalName"
                :placeholder="$t('signupLegalName')"
                :class="{ 'input-error': errors.legalName }"
                :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
            >
        </div>
        <div class="inputFieldDiv">
            <input
                type="text"
                v-model="vatTax"
                :placeholder="$t('signupVatTax')"
                :class="{ 'input-error': errors.vatTax }"
                :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
            >
        </div>
        </div>

        <br>
        <div class="inputFieldButton">
        <button type="submit">{{ $t('signupButton') }}</button>
        </div>

        <div class="or-separator">
        <hr class="dashedSeparator">
        <span class="or-text">{{ $t('signupOr') }}</span>
        <hr class="dashedSeparator">
        </div>

        <div class="centred" id="signupLink">
        <p>{{ $t('signupHaveAccount') }} <router-link to="/login">{{ $t('signupLoginLink') }}</router-link></p>
        </div>
        <div class="centred" style="gap: 8px; margin-top: 10px; font-size: 12px; color: rgba(255,255,255,0.7);">
        <router-link to="/privacy">{{ $t('privacy') }}</router-link>
        <span>·</span>
        <router-link to="/terms">{{ $t('term') }}</router-link>
      </div>
    </form>
    </div>
</div>
</div>
</template>

<style scoped>

a {
color: #FFFFFF;
text-decoration: underline;
text-decoration-color: #FFFFFF;
font-family: var(--font-main);
}

.centred {
display: flex;
justify-content: center;
align-items: center;
}

#bgVideo {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
min-width: 100%;
min-height: 100%;
width: 100%;
height: 100%;
z-index: -1;
object-fit: cover;
}

.signup-container {
display: flex;
flex-direction: row;
align-items: center;
justify-content: center;
width: 100%;
max-width: 900px;
margin: 150px auto;
gap: 50px;
}

#logoDiv {
width: 350px;
height: 350px;
max-width: 100%;
}

#logoDiv img {
max-width: 100%;
max-height: 100%;
object-fit: contain;
}

#loginForm {
width: 380px;
height: auto;
background: rgba(255, 255, 255, 0.1);
border-radius: 15px;
padding: 25px 20px;
box-sizing: border-box;
overflow: visible;
}

.role-toggle-container {
display: flex;
background: rgba(20, 20, 40, 0.5);
border-radius: 25px;
margin-bottom: 15px;
padding: 4px;
width: 100%;
box-sizing: border-box;
}

.role-toggle-container button {
flex: 1;
background: transparent;
color: #999999;
border: none;
padding: 10px 0;
border-radius: 21px;
font-family: var(--font-main);
font-size: 13px;
cursor: pointer;
transition: all 0.3s ease;
}

.role-toggle-container button.active-role {
background: #00d2d3;
color: #ffffff;
font-weight: bold;
}

.inputFieldDiv {
margin: 10px auto;
width: 100%;
display: flex;
flex-direction: column;
}

/* .tags-label {
font-size: 11px;
font-family: "Huninn", sans-serif;
color: rgba(255, 255, 255, 0.75);
padding: 4px 0 4px 0;
margin-bottom: 4px;
text-align: left;
margin-left: 4px;
} */

.inputFieldDiv input {
width: 100%;
box-sizing: border-box;
padding: 9px;
border-radius: 15px;
background: rgba(255, 255, 255, 0.1);
color: #FFFFFF;
font-family: var(--font-main);
font-weight: 400;
font-style: normal;
border: 1px solid transparent;
transition: all 0.3s ease;
}

.inputFieldDiv input::placeholder {
color: #FFFFFF;
opacity: 1;
}

/* Stili per campi in errore (bordo rosso luminoso) */
.inputFieldDiv input.input-error {
border: 1px solid #ff4d4d !important;
background: rgba(255, 77, 77, 0.15) !important;
box-shadow: 0 0 8px rgba(255, 77, 77, 0.3);
}

.error-banner {
background: rgba(255, 77, 77, 0.2);
border: 1px solid #ff4d4d;
color: #ffb3b3;
padding: 10px 14px;
border-radius: 12px;
font-size: 12px;
font-family: "Huninn", sans-serif;
margin-bottom: 15px;
text-align: center;
backdrop-filter: blur(4px);
}

.inputFieldButton button {
background: rgba(0, 242, 254, 67.65%);
color: #FFFFFF;
width: 100%;
height: 40px;
border: none;
border-radius: 17px;
cursor: pointer;
font-family: var(--font-main);
font-weight: 900;
font-style: normal;
}

.inputFieldButton button:hover {
background: rgba(5, 212, 202, 0.61);
}

.or-separator {
display: flex;
align-items: center;
justify-content: center;
width: 100%;
margin: 15px 0;
}

.dashedSeparator {
border: none;
border-top: 2px solid rgb(255, 255, 255);
flex-grow: 1;
margin: 0;
}

.or-text {
padding: 0 15px;
color: rgb(255, 255, 255);
font-family: var(--font-main);
font-style: normal;
font-size: 14px;
}

#signupLink {
font-family: var(--font-main);
color: #FFFFFF;
font-size: 14px;
}

/* Stili per i tag */
.tag-selector-container {
display: flex;
flex-wrap: wrap;
gap: 5px;
margin-top: 2px;
}

.selectable-tag-pill {
cursor: pointer;
user-select: none;
transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.selectable-tag-pill:hover {
transform: translateY(-1px);
}

.business-badge {
display: inline-flex;
align-items: center;
gap: 4px;
background: rgba(0, 242, 254, 0.15);
border: 1px solid #00f2fe;
color: #00f2fe;
padding: 3px 8px;
border-radius: 12px;
font-size: 0.65rem;
font-weight: bold;
letter-spacing: 0.5px;
text-transform: uppercase;
backdrop-filter: blur(4px);
box-shadow: 0 0 6px rgba(0, 242, 254, 0.2);
}

.standard-badge {
display: inline-flex;
align-items: center;
gap: 4px;
background: rgba(255, 255, 255, 0.1);
border: 1px solid rgba(255, 255, 255, 0.3);
color: rgba(255, 255, 255, 0.85);
padding: 3px 8px;
border-radius: 12px;
font-size: 0.65rem;
font-weight: bold;
letter-spacing: 0.5px;
text-transform: uppercase;
backdrop-filter: blur(4px);
}

.password-group {
  position: relative;
  outline: none;
}

.password-dropdown-box {
  position: absolute;
  top: 50%;
  left: 105%;
  transform: translateY(-50%);
  width: 275px;
  background: #ffffff;
  border: 1px solid #dcdcdc;
  border-radius: 8px;
  padding: 12px 14px;
  box-sizing: border-box;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.password-dropdown-box::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -6px;
  transform: translateY(-50%) rotate(45deg);
  width: 10px;
  height: 10px;
  background: #ffffff;
  border-left: 1px solid #dcdcdc;
  border-bottom: 1px solid #dcdcdc;
}

.password-box-title {
  print-color-adjust: exact;
  font-size: 11px;
  font-family: var(--font-main);
  color: #333333;
  font-weight: bold;
  margin: 0 0 8px 0;
  text-align: left;
}

.password-checklist {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}

.password-checklist li {
  font-size: 11px;
  font-family: var(--font-main);
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.password-checklist li:last-child {
  margin-bottom: 0;
}

.rule-invalid {
  color: #d32f2f;
}

.rule-valid {
  color: #2e7d32;
}

.top-nav-icons {
    position: absolute;
    top: 25px;
    right: 30px;
    z-index: 1000;
    display: flex;
    gap: 15px;
    align-items: center;
}

/* Ila kan l-projet fih RTL (l-3arbiya), n-jibouha l-lisser */
[dir="rtl"] .top-nav-icons {
    right: auto;
    left: 30px;
}

[dir="rtl"] .password-dropdown-box {
  left: auto;
  right: 105%; /* Kay-rje3ha t-ban f l-issser f RTL */
}

[dir="rtl"] .password-dropdown-box::before {
  left: auto;
  right: -6px;
  transform: translateY(-50%) rotate(45deg);
  border-left: none;
  border-bottom: none;
  border-right: 1px solid #dcdcdc;
  border-top: 1px solid #dcdcdc;
}

[dir="rtl"] .password-checklist {
  text-align: right; /* Bach ijiw n-n9ati (bullets) mn l-imin */
}

[dir="rtl"] .password-box-title {
  text-align: right;
}

</style>
