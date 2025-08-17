<template>
  <div class="home-container page-container">
    <NavBar />
    <div id="homeHeader">
      <div class="header-content">
        <h1 id="first-title">MealVision</h1>
        <h3>Welcome to the future of food recognition.</h3>
        <img width="30%" src="@/assets/logo.png" alt="mealvision logo" />
      </div>
    </div>

    <!-- Top Wave Clip -->
    <svg width="0" height="0">
      <defs>
        <clipPath id="wavePath" clipPathUnits="objectBoundingBox">
          <path d="M 0,0 L 1,0 L 1,0.85 C 0.75,1.2 0.25,0.5 0,0.85 L 0,0 Z" />
        </clipPath>
      </defs>
    </svg>

    <div class="video-wrapper" ref="videoBox">
      <h1>Your Meal Is One Snap Away</h1>
      <video src="@/assets/demo.mp4" autoplay muted loop playsinline></video>
    </div>

    <!-- YOLOv11 Section -->
    <div class="yolo-section">
      <div class="yolo-container">
        <h2>Powered by YOLOv10</h2>
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
import NavBar from "../components/navbar/navbar.vue";
export default {
  name: "Home-vue",
  components: {
    NavBar,
  },
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
