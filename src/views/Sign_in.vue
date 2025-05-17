<template>
  <div class="sign_in_container">
    <div class="auth-form">
      <h1 class="form-title">Sign In</h1>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit">Sign In</button>
        <hr />

        <p>Don't have an account? <router-link class="nav_li" to="/signUp">Sign-Up</router-link></p>
      </form>

    </div>
  </div>
</template>

<script>
export default {
  name: "Signin_page",
  data() {
    return {
      email: "",
      password: "",
      isLogin: true,  // Assuming you are handling the login/signup toggle with this property
    };
  },
  methods: {
    handleSubmit() {
      // Handle form submission logic here
      console.log("Logging in with:", this.email, this.password);
    },
    switchToSignup() {
      this.isLogin = false;
      // Logic to switch to Sign Up page (perhaps routing or setting a flag)
    },
  },
};
</script>

<style scoped>
.sign_in_container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #191b31;
  padding: 20px;
  
}

.auth-form {
  background: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  
}

.form-title {
  text-align: center;
  font-family: 'Arial', sans-serif;
  color: #191b31;
  font-size: 28px;
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

input,
select {
  width: 80%;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-size: 16px;
  color: #191b31;
  background-color: #f4f4f4;
  transition: border-color 0.3s ease;
  
}

input:focus,
select:focus {
  border-color: #ff5722; /* Orange focus color */
  outline: none;
}

button[type="submit"] {
  width: 50%;
  padding: 12px;
  background-color: #ff5722; /* Orange color */
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #e64a19; /* Darker orange on hover */
}

hr {
  margin: 20px 0;
  border: 0;
  border-top: 1px solid #ddd;
}

p {
  text-align: center;
  color: #191b31;
  font-size: 14px;
}

a {
  color: #ff5722;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .sign_in_container {
    padding: 20px;
  }

  .auth-form {
    padding: 20px;
  }
}
</style>
