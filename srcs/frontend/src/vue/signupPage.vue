<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// User variables
const userType = ref('Normal User'); // Default role
const username = ref('');
const email = ref('');
const password = ref('');

// Extra variables for Local Owner
const clubName = ref('');
const taxId = ref(''); // Tax ID / VAT Number

// Function to send data to the Django backend
const submitSignup = async () => {
    // Prepare the payload
    const payload = {
        role: userType.value,
        username: username.value,
        email: email.value,
        password: password.value
    };

    // If the user is a Local Owner, append the extra fields
    if (userType.value === 'Local Owner') {
        payload.clubName = clubName.value;
        payload.taxId = taxId.value;
    }

    try {
        // Send POST request to the backend
        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            alert("Registration completed successfully! Welcome to Ready2Roll!");
            // Redirect to the home page after successful signup
            router.push('/home');
        } else {
            const errors = await response.json();
            console.error("Server error:", errors);
            alert("Error during registration.");
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
        <div class="signup-container">
            <div id="logoDiv" class="centred">
                <img src="../assets/logo_temp.png" alt="logo">
            </div>
            <div id="loginForm" class="centred">
                <form @submit.prevent="submitSignup">

                    <!-- Role Toggle Button -->
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

                    <!-- Common fields for all users -->
                    <div class="inputFieldDiv">
                        <input type="text" v-model="username" placeholder="Username" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="email" v-model="email" placeholder="E-mail" required>
                    </div>

                    <div class="inputFieldDiv">
                        <input type="password" v-model="password" placeholder="Password" required>
                    </div>

                    <!-- Extra fields for Local Owner (visible only if selected) -->
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
        margin: 200px auto; /* Adjusted margin to accommodate extra fields */
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
    }

    .inputFieldDiv input::placeholder {
        color: #FFFFFF;
        opacity: 1;
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
</style>
