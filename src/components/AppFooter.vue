<template>
  <footer class="footer">
    <div class="footer-content">
      <div>
        <img id="yvc_logo" src="@/assets/yvc.png" alt="yvc-logo" width="10%" />
        <h3>YVC</h3>
        <h4>Data Science Final Project</h4>
        <h4>Information Systems Department</h4>
        <p>&copy; 2025 MealVision. All rights reserved.</p>
      </div>
      <div class="map-container">
        <iframe
          id="map"
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d6718.440492538693!2d35.293272259291!3d32.65358269700872!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x151c52bfe51475a5%3A0x781e444ec641aaa!2sThe%20Max%20Stern%20Yezreel%20Valley%20College!5e0!3m2!1sen!2sil!4v1735661678339!5m2!1sen!2sil"
          width="300"
          height="200"
          style="border: 0"
          allowfullscreen=""
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
        ></iframe>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: "AppFooter",
};
</script>
