<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { z } from 'zod';

const router = useRouter();

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
    .regex(/[0-9]/, 'Must contain at least one number')
});

// form related vairables
const userType = ref('Normal User'); // 'Normal User' oppure 'Local Owner'
const username = ref('');
const email = ref('');
const password = ref('');

// local ownner related variables
const clubName = ref('');
const taxId = ref(''); // partita iva or codice iscale

// send data to backend Django
const submitSignup = async () => {
    // prepare payload for the POST request
    const payload = {
        user_type: userType.value,
        username: username.value,
        email: email.value,
        password: password.value
    };

    // if the user is a Local Owner, add local owner variables to the payload
    if (userType.value === 'Local Owner') {
        payload.club_name = clubName.value;
        payload.tax_id = taxId.value;
    }

    try {
        // send the POST request to the Django backend through api
        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            // if all good then store the token in local storage for future authenticated requests
            if (data.token) {
                localStorage.setItem('token', data.token);
            }

            alert("Registrazione completata con successo! Benvenuto su Ready2Roll!");
            // go back to home page after successful signup
            router.push('/home');
        } else {
            console.error("Errore risposta dal server:", data);
            alert(data.error || "Errore durante la registrazione. Controlla i dati inseriti.");
        }
    } catch (error) {
        console.error("Errore di rete:", error);
        alert("Impossibile connettersi al server backend.");
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
                <form @submit.prevent="submitSignup">

                    <!-- Selettore Ruolo Utente -->
                    <div class="role-toggle-container">
                        <button
                            type="button"
                            :class="{'active-role': userType === 'Normal User'}"
                            @click="userType = 'Normal User'">
                            Normal User
                        </button>
                        <button
                            type="button"
                            :class="{'active-role': userType === 'Local Owner'}"
                            @click="userType = 'Local Owner'">
                            Local Owner
                        </button>
                    </div>

                    <!-- Campi Comuni -->
                    <div class="inputFieldDiv">
                        <input type="text" v-model="username" placeholder="Username" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="email" v-model="email" placeholder="E-mail" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="password" v-model="password" placeholder="Password" required>
                    </div>

                    <!-- Campi Extra per Local Owner -->
                    <div v-if="userType === 'Local Owner'">
                        <div class="inputFieldDiv">
                            <input type="text" v-model="clubName" placeholder="Club / Venue Name" required>
                        </div>
                        <div class="inputFieldDiv">
                            <input type="text" v-model="taxId" placeholder="Tax ID / VAT Number" required>
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
    a
    {
        color: #FFFFFF;
        text-decoration: underline;
        text-decoration-color: #FFFFFF;
    }

    .centred
    {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    #bgVideo
    {
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

    .signup-container
    {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 900px;
        margin: 200px auto;
        gap: 50px;
    }

    #logoDiv
    {
        width: 350px;
        height: 350px;
        max-width: 100%;
    }

    #logoDiv img
    {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }

    #loginForm
    {
        width: 350px;
        height: auto;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 30px 20px;
        box-sizing: border-box;
    }

    .inputFieldDiv
    {
        margin: 10px auto 10px auto;
        width: 100%;
    }

    .inputFieldDiv input
    {
        width: 100%;
        box-sizing: border-box;
        padding: 10px;
        border-radius: 17px;
        background: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
        font-family: "Bruno Ace", sans-serif;
        font-weight: 400;
        font-style: normal;
    }

    .inputFieldDiv input::placeholder
    {
        color: #FFFFFF;
        opacity: 1;
    }

    .inputFieldButton button
    {
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

    .inputFieldButton button:hover
    {
        background: rgba(5, 212, 202, 0.61);
    }

    .or-separator
    {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin: 20px 0;
    }

    .dashedSeparator
    {
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
</style>
