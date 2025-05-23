<template> 
    <div class="about-us-container"> 
        <!-- Upper part: About the project --> 
        <div class="about-project"> 
            <h1>MealVision</h1> 
            <img src="@/assets/logo.png" alt="mealVision_logo" class="logo-image"> 
            <p class="project-description">This project aims to create a tool that can help people decide what to cook. By analyzing images of food ingredients, our model will identify what's in the picture and suggest potential meal ideas using an AI API. This will help users save time and discover new recipes based on the ingredients they have on hand.</p> 
        </div> 
        <!-- Lower part: Founders' introduction --> 
          
        <div class="section-title">
            <h2>Our Team</h2>
            <div class="title-underline"></div>
        </div>
        
        <div class="founders-container"> 
            <!-- Founder Card 1 -->
            <div class="founder-card">
                <div class="founder-image-container">
                    <img class="founder-image" src="@/assets/jeries.png" alt="Jeries Qanaza">
                </div>
                <div class="founder-info">
                    <h3>Jeries Qanaza</h3>
                    <p class="founder-title">Co-Founder @ MealVision</p>
                    <p class="founder-subtitle">3rd year student @ YVC</p>
                    <a href="https://www.linkedin.com/in/jeries-qanaza-36b14620a/" target="_blank" class="social-link"> 
                        <img class="linkedin-icon" src="@/assets/linkedinLogo.png" alt="LinkedIn"> 
                    </a>
                </div>
            </div>
 
            <!-- Founder Card 2 -->
            <div class="founder-card">
                <div class="founder-image-container">
                    <img class="founder-image" src="@/assets/image_placeholder.png" alt="Yohai Abramovitz">
                </div>
                <div class="founder-info">
                    <h3>Yohai Abramovitz</h3>
                    <p class="founder-title">Co-Founder @ MealVision</p>
                    <p class="founder-subtitle">3rd year student @ YVC</p>
                    <a href="https://www.linkedin.com/in/yohaii/" target="_blank" class="social-link"> 
                        <img class="linkedin-icon" src="@/assets/linkedinLogo.png" alt="LinkedIn"> 
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Supervisor Card -->
        <div class="supervisor-section">
            <div class="founder-card supervisor-card">
                <div class="founder-image-container">
                    <img class="founder-image" src="@/assets/image_placeholder.png" alt="Salih Abu Shahin">
                </div>
                <div class="founder-info">
                    <h3>Salih Abu Shahin</h3>
                    <p class="founder-title">Project Supervisor</p>
                </div>
            </div>
        </div>
        
        <ManualBox/> 
    </div> 
</template> 
 
<script> 
export default { 
    name: "AboutUs", 
 
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
.about-us-container { 
    display: flex; 
    flex-direction: column; 
    align-items: center;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    color: #ffffff;
    background-color: #191b31;
} 

.about-project { 
    text-align: center; 
    margin-bottom: 3rem;
    max-width: 800px;
} 

.logo-image {
    width: 150px;
    margin: 1rem 0;
}

.project-description {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #ffffff;
}

.section-title {
    width: 100%;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
}

.section-title h2 {
    font-size: 2rem;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.title-underline {
    height: 4px;
    width: 80px;
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    margin: 0 auto;
    border-radius: 2px;
}

.founders-container { 
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
    width: 100%;
    margin-bottom: 2rem;
} 

.supervisor-section {
    margin-top: 1rem;
    margin-bottom: 3rem;
}

.founder-card {
    width: 300px;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
}

.founder-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.founder-image-container {
    height: 250px;
    overflow: hidden;
    position: relative;
    background: #f5f7fa;
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
    color: #1a202c;
    font-size: 1.5rem;
    font-weight: 600;
}

.founder-title {
    font-weight: bold;
    color: #2d3748;
    margin: 0.5rem 0;
}

.founder-subtitle {
    color: #4a5568;
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
    background: linear-gradient(to right, #f6f9fc, #f1f5f9);
    border: 2px solid #e2e8f0;
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
</style>