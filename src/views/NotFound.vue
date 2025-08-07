<template>
  <div class="not-found">
    <div class="content">
      <h1>404 - Page Not Found</h1>
      <p>Oops! The page you're looking for doesn't exist.</p>
      <router-link to="/" class="home-link">Return to Home</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "NotFound",
};
</script>
