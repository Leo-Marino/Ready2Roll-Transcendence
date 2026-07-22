<script setup>
    import { ref } from vue;

    // create the object that is going to store our data
    const formData = ref({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })

    // when the function is called, vue is going to create the JSON
    // object containing the necessary info, then it's going to make
    // a POST request to the port 8000 of the localhost website, where
    // a 'server' is already setup in the backend part in Django,
    // where it is going to see the request made by vue, then Django
    // is going to try to store the gotten variables into the DB, and
    // finally, a response is going to be given back to vue, where:
    // if everything has gone well, then its going to get a positive code
    // (code 200 OK etc), therefore the website can redirect the user to
    // the main page, otherwise its going to return a code 400 error or sum,
    // which means the storing has gone wrong.
    const handleSubmit = async() => {
        try
        {
            const response = await fetch('http://localhost:8000/api/signup/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData.value)
            })
            const data = await response.json()
            if (response.ok)
                console.log('Registration successful: ', data)
            else
                console.error('Registration failed: ', data)
        }
        catch (error)
        {
            console.error('Network error: ', error)
        }
    }
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
                <form method="post" @submit.prevent="handleSubmit">
                    <div class="inputFieldDiv">
                        <input type="text" placeholder="Username" v-model="formData.username">
                    </div>
                    <div class="inputFieldDiv">
                        <input type="text" placeholder="E-mail" v-model="formData.email">
                    </div>
                    <div class="inputFieldDiv">
                        <input type="password" placeholder="Password" v-model="formData.password">
                    </div>
                    <div class="inputFieldDiv">
                        <input type="password" placeholder="Confirm password" v-model="formData.confirmPassword">
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
        width: 600px;
        height: auto;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 30px 20px;
        box-sizing: border-box;
    }

    .inputFieldDiv
    {
        margin: 10px auto 10px auto;
        width: 500px;
    }

    .inputFieldDiv input
    {
        width: 100%;
        margin: 10px auto 10px auto;
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