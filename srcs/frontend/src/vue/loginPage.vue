<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Variables to hold the user's input
const username = ref('');
const password = ref('');

// Function to handle login submission and communicate with Django
const submitLogin = async () => {
    // --- REAL BACKEND CODE (Commented out until Django is ready) ---
    const payload = {
        username: username.value,
        password: password.value
    };

    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access', data.access);
            alert("Login successful! Welcome back.");
            router.push('/home');
        } else {
            alert("Invalid username or password. Please try again.");
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("Unable to connect to the Backend Server.");
    }
};
</script>
<template>
    <video autoplay muted loop playsinline id="bgVideo">
        <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
    </video>
    <div class="wrapper">
        <div id="logoDiv" class="centred">
            <img src="../assets/logo_temp.png" alt="logo">
        </div>
        <div id="loginForm" class="centred">
            <form @submit.prevent="submitLogin">
                <div class="inputFieldDiv">
                    <input type="text" placeholder="Username" v-model="username" required>
                </div>
                <div class="inputFieldDiv">
                    <input type="password" placeholder="Password" v-model="password" required>
                </div>
                <br>
                <div class="inputFieldButton">
                    <button type="submit">Log-in</button>
                </div>
                <div class="or-separator">
                    <hr class="dashedSeparator">
                    <span class="or-text">OR</span>
                    <hr class="dashedSeparator">
                </div>
                <div class="centred" id="signupLink">
                    <p>Don't have an account? <router-link to="/signup">Sign up</router-link></p>
                </div>
            </form>
        </div>
    </div>
</template>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/justfont/open-huninn-font@1.1/font/jf-openhuninn.css');

    a
    {
        color: #FFFFFF;
        text-decoration: underline;
        text-decoration-color: #FFFFFF;
        font-family: "Huninn", sans-serif;
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

    #logoDiv
    {
        width: 250px;
        height: 250px;
        margin: 150px auto 30px auto;
        max-width: 100%;
    }

    #logoDiv img
    {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        padding-left: 0;
    }

    #loginForm
    {
        width: 350px;
        height: 350px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
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
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
        font-family: "Huninn", sans-serif;
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
        font-family: "Huninn", sans-serif;
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

    .or-text
    {
        padding: 0 15px;
        color: rgb(255, 255, 255);
        font-family: "Huninn", sans-serif;
        font-style: normal;
        font-size: 14px;
    }

    #signupLink
    {
        font-family: "Huninn", sans-serif;
        color: #FFFFFF;
        font-size: 14px;
    }
</style>