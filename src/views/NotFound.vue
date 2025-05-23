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
    name: 'NotFound'
  }
  </script>
  
  <style scoped>
  .not-found {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #191b31;
    color: white;
    text-align: center;
    padding: 20px;
  }
  
  .content {
    max-width: 600px;
  }
  
  h1 {
    font-size: 3rem;
    margin-bottom: 20px;
    color: #FFA500;
  }
  
  p {
    font-size: 1.2rem;
    margin-bottom: 30px;
  }
  
  .home-link {
    display: inline-block;
    padding: 12px 24px;
    background-color: #FFA500;
    color: #191b31;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
  }
  
  .home-link:hover {
    background-color: #FF8C00;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  </style>