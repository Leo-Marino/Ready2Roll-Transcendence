<template>
	<video autoplay muted loop playsinline id="bgVideo">
		<source src="../assets/ready2roll_wave_background_inverted.mp4" type="video/mp4">
	</video>
	<div class="error-container">
		<h1>404</h1>
		<h2>Page Not Found</h2>
		<p>The link you followed may be broken, or the page may have been removed</p>
		<router-link to="/home" class="home-link">Back to Home</router-link>
	</div>
</template>

<style scoped>

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

.error-container {
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
min-height: 100vh;
color: #ffffff;
text-align: center;
font-family: "Huninn", sans-serif;
padding: 20px;
}

.error-container h1 {
font-size: 5rem;
margin: 0;
color: #e83dee;
}

.error-container h2 {
font-size: 1.5rem;
margin: 10px 0;
}

.error-container p {
color: rgba(255, 255, 255, 0.7);
margin-bottom: 20px;
}

.home-link {
background: rgba(0, 242, 254, 0.2);
border: 1px solid #e83dee;
color: #e83dee;
padding: 10px 20px;
border-radius: 12px;
text-decoration: none;
font-weight: bold;
transition: all 0.3s ease;
}

.home-link:hover {
background: #e83dee;
color: #000000;
}
</style>