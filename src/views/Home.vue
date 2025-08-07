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
      <video src="@/assets/demo.mp4" autoplay muted loop playsinline></video>
    </div>

    <!-- YOLOv11 Section -->
    <div class="yolo-section">
      <div class="yolo-container">
        <h2>Powered by YOLOv8</h2>
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
