<template>
  <div class="sign_in_container">
    <div class="auth-form">
      <h1>Sign In</h1>

      <form @submit.prevent="handleSubmit">
        
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>

        <button  type="submit">Sign In</button>
        <hr/>
        <p>
          Don't have an account? <a href="#" @click="switchToLogin">Login</a>
        </p>
        
      </form>
    </div>
  </div>
</template>

<script>
import "./sign_in_up.css";

export default {
  name: "Signin_page",

  methods: {
    handleSubmit() {
      // Handle form submission logic here
      // For example:
      if (this.isLogin) {
        console.log("Logging in with:", this.email, this.password);
      } else {
        console.log(
          "Signing up with:",
          this.email,
          this.password,
          this.birthday
        );
      }
    },
    switchToSignup() {
      this.isLogin = false;
    },
    switchToLogin() {
      this.isLogin = true;
    },
  },
};
</script>
