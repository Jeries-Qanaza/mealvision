<template> 
  <NavBar style="background-color: #174329;"/>
  <div class="about-us-container"> 
    <!-- Upper part: About the project --> 
    <div class="about-project"> 
      <h1>MealVision</h1> 
      <img src="@/assets/logo.png" alt="mealVision_logo" class="logo-image"> 
      <p class="project-description">
        This project aims to create a tool that can help people decide what to cook. 
        By analyzing images of food ingredients, our model will identify what's in the 
        picture and suggest potential meal ideas using an AI API. This will help users 
        save time and discover new recipes based on the ingredients they have on hand.
      </p> 
      <a target="_blank" href="https://universe.roboflow.com/food-updated/food3proj-pf2xc/browse?queryText=&pageSize=50&startingIndex=0&browseQuery=true"> 
        <p>Explore our dataset on Roboflow</p>
      </a>
    </div> 

    <div class="about-us-team">
      
  
    <!-- Lower part: Founders' introduction --> 
    <!-- Lower part: Founders' introduction --> 
<div class="founders-container"> 
  <div class="section-title">
    <h2 style="color: orange;">Our Team</h2>
    <div class="title-underline"></div>
  </div>

  <!-- Founder Card 1 -->
  <div class="founder-card">
    <div class="founder-info">
      <h3>Jeries Qanaza</h3>
      <p class="founder-title">Co-Founder @ MealVision</p>
      <a href="https://www.linkedin.com/in/jeries-qanaza-36b14620a/" target="_blank" class="social-link"> 
        <img class="linkedin-icon" src="@/assets/linkedinLogo.png" alt="LinkedIn"> 
      </a>
    </div>
  </div>

  <!-- Founder Card 2 -->
  <div class="founder-card">
    <div class="founder-info">
      <h3>Yohai Abramovitz</h3>
      <p class="founder-title">Co-Founder @ MealVision</p>
      <a href="https://www.linkedin.com/in/yohaii/" target="_blank" class="social-link"> 
        <img class="linkedin-icon" src="@/assets/linkedinLogo.png" alt="LinkedIn"> 
      </a>
    </div>
  </div>
</div>

<!-- Supervisor section is now outside -->
<div class="supervisor-section">
  <div class="founder-card supervisor-card">
    <div class="founder-info">
      <h3>Salih Abu Shahin</h3>
      <p class="founder-title">Project Supervisor</p>
    </div>
  </div>
</div>

      </div>

      
      <div class="About_Model">
        <div class="tech-carousel">
          <u><h2 style="color: #174329;">Used Technologies</h2> </u>
          <div class="carousel-track">
            <div class="tech-slide"> <img src="@/assets/python.png" alt="Python"> </div>
            <div class="tech-slide"> <img src="@/assets/roboflowLogo.png" alt="Roboflow"> </div>
            <div class="tech-slide"> <img src="@/assets/vueJSlogo.png" alt="Vue.js"> </div>
            <div class="tech-slide"> <img src="@/assets/Gemini.png" alt="Gemini"> </div>
            <div class="tech-slide"> <img src="@/assets/stable_diffusion.png" alt="Stable Diffusion"> </div>
            <div class="tech-slide"> <img src="@/assets/yolo.png" alt="YOLO"> </div>
            <div class="tech-slide"> <img src="@/assets/oracle_cloud.png" alt="Oracle Cloud"> </div>
            <div class="tech-slide"> <img src="@/assets/google_colab.jpg" alt="Google Colab"> </div>
          </div>
        </div>


      </div>


  </div> 
</template> 
 
<script>
import NavBar from "../components/navbar/navbar.vue";

export default { 
  name: "AboutUs", 
    components: {
    NavBar,
  },
  data() { 
    return { 
      name: "", 
      email: "", 
      message: "", 
    }; 
  } 
} 
</script> 
 
<style> 
.About_Model
{
  margin-top: 5px;
  background-color: orange;
  border-radius: 60px;
}
.about-us-team
{
  background-color: #174329;
  border-radius: 60px;
}

.about-us-container { 
  display: flex; 
  flex-direction: column; 
  align-items: center;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  margin-top: 30px;
  color: #333;
  background-color: #ffffff;
} 

.about-project { 
  text-align: center; 
  margin-bottom: 3rem;
  max-width: 800px;
 
} 

.about-project h1 {
  font-size: 2.5rem;
  font-weight: 700;
  background-image: linear-gradient(to right, #719920, #9bd74b);
  -webkit-background-clip: text;
  color: transparent;
}

.logo-image {
  width: 150px;
  margin: 1rem 0;
}

.project-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #444;
}

.about-project a p {
  color: #719920;
  font-weight: bold;
  transition: color 0.3s ease;
}

.about-project a p:hover {
  color: #9bd74b;
}

.section-title {
  width: 100%;
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
}

.section-title h2 {
  font-size: 2rem;
  color: #719920;
  margin-bottom: 0.5rem;
}

.title-underline {
  height: 4px;
  width: 80px;
  background: orange;
  margin: 0 auto;
  border-radius: 2px;
}

.founders-container { 
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
  width: 100%;
  margin-bottom: 1rem;

  border-radius: 10px;
  width: fit-content;
  padding: 2rem; /* optional for spacing */
}

.supervisor-section {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  margin-bottom: 3rem;
  width: 100%;
}

.founder-card {
  width: 300px;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(113, 153, 32, 0.15);
  border: 1px solid #dfe8d0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}

.founder-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(113, 153, 32, 0.25);
}

.founder-image-container {
  height: 250px;
  overflow: hidden;
  position: relative;
  background: #f8fbf4;
}

.founder-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 1rem;
  transition: transform 0.5s ease;
}

.founder-card:hover .founder-image {
  transform: scale(1.05);
}

.founder-info {
  padding: 1.5rem;
  text-align: center;
  background-color: white;
}

.founder-info h3 {
  margin: 0 0 0.5rem 0;
  color: #719920;
  font-size: 1.5rem;
  font-weight: 600;
}

.founder-title {
  font-weight: bold;
  color: #5c7c19;
  margin: 0.5rem 0;
}

.founder-subtitle {
  color: #7d8f5f;
  font-size: 0.95rem;
  margin-bottom: 1rem;
}

.social-link {
  display: inline-block;
  transition: transform 0.3s ease;
}

.social-link:hover {
  transform: scale(1.2);
}

.linkedin-icon {
  width: 30px;
  height: 30px;
}

.supervisor-card {
  background: linear-gradient(to right, #f8fbf4, #eef6e2);
  border: 2px solid #c6d8a5;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .founders-container {
    flex-direction: column;
    align-items: center;
  }
  
  .founder-card {
    width: 90%;
    max-width: 350px;
  }
}


.tech-carousel {
    width: 100%;
    max-width: 800px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.carousel-track {
    display: flex;
    animation: scroll 15s linear infinite;
    gap: 30px;
}

.tech-slide {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.386);
    border-radius: 12px;
    transition: transform 0.3s ease;
    min-width: 120px;
}

.tech-slide:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.2);
}

.tech-slide img {
    width: 60px;
    height: 60px;
    object-fit: contain;
}


@keyframes scroll {
    0% {
        transform: translateX(0);
    }
    100% {
        transform: translateX(-50%);
    }
}

/* Pause on hover */
.tech-carousel:hover .carousel-track {
    animation-play-state: paused;
}

@media (max-width: 600px) {
    .tech-slide {
        min-width: 100px;
        padding: 15px;
    }
    
    .tech-slide img {
        width: 45px;
        height: 45px;
    }
  
}
</style>
