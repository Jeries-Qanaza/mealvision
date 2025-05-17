<template>
  <div class="home-container">
    <div id="homeHeader">
      <div class="header-content">
        <h1>🍽️ MealVision</h1>
        <p>Welcome to the future of food recognition.</p>
      </div>
    </div>
      
   
    <div class="video-wrapper" ref="videoBox">
      <h1>Your Meal Is One Snap Away</h1>
      <video
        src="@/assets/demo.mp4" 
        autoplay
        muted
        loop
        playsinline
      ></video>
    </div>

    <!-- YOLOv11 Section -->
    <div class="yolo-section">
      <div class="yolo-container">
        <h2>Powered by YOLOv11</h2>
        <div class="yolo-features">
          <div class="feature">
            <span class="icon">⚡</span>
            <h4>Real-time Detection</h4>
            <p>Processes images in milliseconds for instant results</p>
          </div>
          <div class="feature">
            <span class="icon">🎯</span>
            <h4>High Accuracy</h4>
            <p>State-of-the-art precision in food recognition</p>
          </div>
          <div class="feature">
            <span class="icon">🌐</span>
            <h4>Versatile</h4>
            <p>Recognizes thousands of food items worldwide</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home-vue",
  mounted() {
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
  },
  methods: {
    handleScroll() {
      const box = this.$refs.videoBox;
      const scrollY = window.scrollY;
      if (scrollY > 50) {
        box.style.transform = "scale(1.04)";
      } else {
        box.style.transform = "scale(1)";
      }
    },
  },
};

</script>

<style scoped>
.home-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header Section */
#homeHeader {
  background-image: url('@/assets/example2.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  height: 60vh;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

#homeHeader::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
}

.header-content {
  backdrop-filter: blur(8px);
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 40px 60px;
  text-align: center;
  color: #fff;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) ;
  animation: fadeIn 1s ease-in-out;
  z-index: 1;
  max-width: 800px;
  width: 80%;
}

.header-content h1 {
  font-size: 3.5em;
  font-weight: bold;
  margin-bottom: 20px;
  color: #ffffff;
  text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
}

.header-content p {
  font-size: 1.6em;
  color: #e0e0e0;
  text-shadow: 1px 1px 5px rgba(0,0,0,0.3);
}

/* YOLO Section */
.yolo-section {
  padding-bottom: 50px;
  display: flex;
  justify-content: center;
  background-color: #191b31;
}

.yolo-container {
  max-width: 1200px;
  width: 100%;
}

.yolo-container h2 {
  font-size: 2.5em;
  margin-bottom: 50px;
  color: #FFC107;
  text-align: center;
  font-weight: 600;
  letter-spacing: 1px;
}

.yolo-features {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.feature {
  flex: 1;
  min-width: 280px;
  max-width: 320px;
  padding: 35px 30px;
  border-radius: 15px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  text-align: center;
}

.feature:hover {
  transform: translateY(-10px);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 15px 35px orange;
  border-color: rgba(0, 43, 198, 0.3);
}

.feature .icon {
  font-size: 3em;
  margin-bottom: 20px;
  color: #FFC107;
  display: inline-block;
}

.feature h4 {
  font-size: 1.5em;
  margin-bottom: 15px;
  color: #FFC107;
  font-weight: 500;
}

.feature p {
  font-size: 1.1em;
  color: #e0e0e0;
  line-height: 1.6;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .yolo-features {
    gap: 20px;
  }
  
  .feature {
    min-width: 240px;
  }
}

@media (max-width: 768px) {
  #homeHeader {
    height: 50vh;
  }
  
  .header-content {
    padding: 30px;
    width: 90%;
  }
  
  .header-content h1 {
    font-size: 2.8em;
  }
  
  .header-content p {
    font-size: 1.3em;
  }
  
  .yolo-container h2 {
    font-size: 2.2em;
    margin-bottom: 40px;
  }
  
  .feature {
    min-width: 100%;
    max-width: 400px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 25px;
  }
  
  .header-content h1 {
    font-size: 2.2em;
  }
  
  .header-content p {
    font-size: 1.1em;
  }
}

.video-wrapper {

  margin: 40px auto;
  width: 80%;
  max-width: 1000px;
  background: linear-gradient(to right ,#191b3100 , rgba(255, 166, 0, 0.345));
  border-radius: 20px;
  display: flex;
  font-family: "Mogra", system-ui;
  font-weight: 400;
  font-style: normal;

}

.video-wrapper video {
  margin:4%;
  width: 70%;
  height: 100%;
  object-fit: cover;
  border-radius: 20px;
  pointer-events: none;
  border: 5px solid orange;
  box-shadow: 0 0 25px rgba(255, 165, 0, 0.4);
  transition: transform 0.4s ease;
}
</style>