<template>
  <div class="sign_up_container">
    <div class="auth-form">
      <h1 class="form-title">Sign Up</h1>
      <form @submit.prevent="handleSubmit">
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
        <p>Already have an account? <router-link class="nav_li" to="/signIn">Sign-In</router-link> </p>
      </form>
    </div>
  </div>
</template>

<script>
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth, db } from "../firebase/firebase"; // Import Firebase initialization
import { ref, set } from "firebase/database"; // Import Realtime Database functions
const currentYear = new Date().getFullYear();

export default {
  name: "Signup_page",
  data() {
    return {
      email: "",
      password: "",
      birthday: {
        day: "",
        month: "",
        year: "",
      },
      days: Array.from({ length: 31 }, (_, i) => i + 1),
      months: Array.from({ length: 12 }, (_, i) => i + 1),
      years: Array.from({ length: 120 }, (_, i) => currentYear - i),
    };
  },
  methods: {
    sanitizeEmail(email) {
      return email.replace(/\./g, ","); // Replace dots with commas (Firebase doesn't allow dots in keys)
    },
    async handleSubmit() {
      try {
        // Step 1: Register the user with email and password
        await createUserWithEmailAndPassword(auth, this.email, this.password);

        // Step 2: Use sanitized email as the key in Realtime Database
        const sanitizedEmail = this.sanitizeEmail(this.email);
        const userRef = ref(db, `users/${sanitizedEmail}`);
        await set(userRef, {
          email: this.email,
          password: this.password,
          birthday: this.birthday,
        });

        alert("Signup successful!");
      } catch (error) {
        console.error("Error during signup:", error.message);
        alert(error.message);
      }
    },
  },
};
</script>

<style scoped>
.sign_up_container {
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

.birthday-inputs {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

select {
  flex: 1;
  padding: 10px;
  background-color: #f4f4f4;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid #ddd;
}

/* Hover and Focus Effects for Select */
select:focus {
  border-color: #ff5722;
}

@media (max-width: 768px) {
  .sign_up_container {
    padding: 20px;
  }

  .auth-form {
    padding: 20px;
  }
}
</style>
