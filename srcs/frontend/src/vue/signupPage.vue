<script setup>
import { ref } from 'vue';

// 1. Creiamo le variabili per salvare quello che l'utente digita
const username = ref('');
const email = ref('');
const password = ref('');

// 2. La funzione che spedisce i dati al tuo Django
const submitSignup = async () => {
    // Impacchettiamo i dati
    const payload = {
        username: username.value,
        email: email.value,
        password: password.value
    };

    try {
        // Bussiamo alla porta del backend!
        const response = await fetch('http://localhost:8000/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            alert("Registrazione completata con successo! Benvenuto in Ready2Roll!");
            // Opzionale: qui il tuo amico potrà inserire il codice per cambiare pagina
            // es: router.push('/login');
        } else {
            const errors = await response.json();
            console.error("Errore dal server:", errors);
            alert("Errore nella registrazione. (Forse l'username esiste già o la password è debole)");
        }
    } catch (error) {
        console.error("Errore di rete:", error);
        alert("Impossibile connettersi al Server Backend.");
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

                    <div class="inputFieldDiv">
                        <input type="text" v-model="username" placeholder="Username" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="email" v-model="email" placeholder="E-mail" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="password" v-model="password" placeholder="Password" required>
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
        margin: 250px auto;
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
        background: rgba(0, 242, 254, 1);
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

    .or-text
    {
        padding: 0 15px;
        color: rgb(255, 255, 255);
        font-family: "Bruno Ace", sans-serif;
        font-style: normal;
        font-size: 14px;
    }

    #signupLink
    {
        font-family: "Bruno Ace", sans-serif;
        color: #FFFFFF;
        font-size: 14px;
    }
</style>
