<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { z } from 'zod';
import { computed } from 'vue';

const router = useRouter();

const userType = ref('standard'); // 'Normal User' | 'Local Owner'
const username = ref('');
const email = ref('');
const password = ref('');
const clubName = ref('');
const taxId = ref('');

const passwordRules = computed(() => [
{
    id: 'length',
    label: 'At least 8 characters',
    valid: password.value.length >= 8
},
{
    id: 'uppercase',
    label: 'At least one uppercase letter',
    valid: /[A-Z]/.test(password.value)
},
{
    id: 'number',
    label: 'At least one number',
    valid: /[0-9]/.test(password.value)
}
]);

const isPasswordValid = computed(() =>
    passwordRules.value.every(rule => rule.valid)
);

const errors = ref({});

const getSignupSchema = () => {
    const baseSchema = {
    username: z.string().min(3, 'Username must be at least 3 characters'),
    email: z.string().email('Please enter a valid email address'),
    password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
        .regex(/[0-9]/, 'Must contain at least one number')
    };
    if (userType.value === 'business') {
        baseSchema.clubName = z.string().min(1, 'Club / Venue Name is required');
        baseSchema.taxId = z.string().min(1, 'Tax ID / VAT Number is required');
    }
    return z.object(baseSchema);
};


const submitSignup = async () => {
    errors.value = {};
    const formData = {
    username: username.value,
        email: email.value,
        password: password.value,
        ...(userType.value === 'business' && {
            clubName: clubName.value,
            taxId: taxId.value
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
        user_type: userType.value,
        username: username.value,
        email: email.value,
        password: password.value
    };

    if (userType.value === 'business') {
        payload.club_name = clubName.value;
        payload.tax_id = taxId.value;
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
        localStorage.setItem('token', data.token);
        }
        alert('Registrazione completata con successo!');
        router.push('/login');
    } else {
        console.error('Errore risposta dal server:', data);
        alert(data.error || 'Errore durante la registrazione, controlla meglio i dati che hai inserito');
    }
    } catch (error) {
    console.error('Errore di rete:', error);
    alert('Impossibile connettersi al server backend');
    }
};
</script>

<template>
<video autoplay muted loop playsinline id="bgVideo">
<source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
</video>

<div class="wrapper">
<div class="signup-container">
    <div id="logoDiv" class="centred">
    <img src="../assets/logo_temp.png" alt="logo">
    </div>
    <div id="loginForm" class="centred">
    <form @submit.prevent="submitSignup" novalidate>

        <!-- Selettore Ruolo Utente -->
        <div class="role-toggle-container">
        <button
            type="button"
            :class="{'active-role': userType === 'standard'}"
            @click="userType = 'standard'; errors = {};">
            standard
        </button>
        <button
            type="button"
            :class="{'active-role': userType === 'business'}"
            @click="userType = 'business'; errors = {};">
            business
        </button>
        </div>

        <!-- Campi Comuni -->
        <div class="inputFieldDiv">
        <input type="text" v-model="username" placeholder="Username">
        <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
        </div>

        <div class="inputFieldDiv">
        <input type="email" v-model="email" placeholder="E-mail">
        <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </div>

        <div class="inputFieldDiv">
            <input 
                type="password" 
                v-model="password" 
                placeholder="Password"
            />
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

        <div v-if="userType === 'business'">
        <div class="inputFieldDiv">
            <input type="text" v-model="clubName" placeholder="Club / Venue Name">
            <span v-if="errors.clubName" class="error-text">{{ errors.clubName }}</span>
        </div>
        <div class="inputFieldDiv">
            <input type="text" v-model="taxId" placeholder="Tax ID / VAT Number">
            <span v-if="errors.taxId" class="error-text">{{ errors.taxId }}</span>
        </div>
        </div>

        <br>
        <div class="inputFieldButton">
        <button type="submit">Submit</button>
        </div>

        <div class="or-separator">
        <hr class="dashedSeparator">
        <span class="or-text">OR</span>
        <hr class="dashedSeparator">
        </div>

        <div class="centred" id="signupLink">
        <p>Already have an account? <router-link to="/login">Login</router-link></p>
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
margin: 200px auto;
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
width: 350px;
height: auto;
background: rgba(255, 255, 255, 0.1);
border-radius: 15px;
padding: 30px 20px;
box-sizing: border-box;
}

/* Toggle Button Styles */
.role-toggle-container {
display: flex;
background: rgba(20, 20, 40, 0.5);
border-radius: 25px;
margin-bottom: 20px;
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
font-family: "Bruno Ace", sans-serif;
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
margin: 10px auto 10px auto;
width: 100%;
display: flex;
flex-direction: column;
}

.inputFieldDiv input {
width: 100%;
box-sizing: border-box;
padding: 10px;
border-radius: 17px;
background: rgba(255, 255, 255, 0.1);
color: #FFFFFF;
font-family: "Bruno Ace", sans-serif;
font-weight: 400;
font-style: normal;
border: 1px solid transparent;
}

.inputFieldDiv input::placeholder {
color: #FFFFFF;
opacity: 1;
}

/* Validation Error Styles */
.error-text {
color: #ff4d4d;
font-size: 11px;
font-family: "Bruno Ace", sans-serif;
margin-top: 4px;
margin-left: 8px;
text-align: left;
}

.inputFieldButton button {
background: rgba(0, 242, 254, 67.65%);
color: #FFFFFF;
width: 100%;
height: 40px;
border: none;
border-radius: 17px;
cursor: pointer;
font-family: "Bruno Ace", sans-serif;
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
margin: 20px 0;
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
font-family: "Bruno Ace", sans-serif;
font-style: normal;
font-size: 14px;
}

#signupLink {
font-family: "Bruno Ace", sans-serif;
color: #FFFFFF;
font-size: 14px;
}

.password-checklist {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 8px;
  text-align: left;
}

.password-checklist li {
  font-size: 11px;
  font-family: "Bruno Ace", sans-serif;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s ease;
}

.rule-invalid {
  color: #ff4d4d;
}

.rule-valid {
  color: #00e676;
}
</style>
