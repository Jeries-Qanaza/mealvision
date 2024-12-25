<template>
  <div class="sign_up_container">
    <div class="auth-form">
      <h1>Sign Up</h1>

      <form>

        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>

        
        <div class="form-group birthday-field">
          <label for="birthday">Birthday</label>
          <div class="birthday-inputs">

            <!-- Day-->
            <select v-model="birthday.day" id="day" required>
              <option value="" disabled selected>Day</option>
              <option v-for="day in days" :key="day">{{ day }}</option>
            </select>

            <!-- Month-->
            <select v-model="birthday.month" id="month" required>
              <option value="" disabled selected>Month</option>
              <option v-for="month in months" :key="month">{{ month }}</option>
            </select>

            <!-- Year-->
            <select v-model="birthday.year" id="year" required>
              <option value="" disabled selected>Year</option>
              <option v-for="year in years" :key="year">{{ year }}</option>
            </select>

          </div>
        </div>

        <button type="submit">Sign Up</button>
        <hr />
        <p>Already have an account? <a href="#">Login</a></p>
      </form>
    </div>
  </div>
</template>

<script>
import "./sign_in_up.css";

export default {
  name: "Login_page",
  data() {
    return {
      isLogin: true,
      email: "",
      password: "",
      birthday: {
        day: "",
        month: "",
        year: "",
      },

      days: Array.from({ length: 31 }, (_, i) => i + 1),
      months: Array.from({ length: 12 }, (_, i) => i + 1),
      years: Array.from({ length: 120 }, (_, i) => 2025 - i),

    };
  },
  methods: {
    handleSubmit() {
      // Handle form submission logic here
      // For example:
      if (this.isLogin) {
        console.log("Logging in with:", this.email, this.password);
      }
    },
  },
};
</script>
