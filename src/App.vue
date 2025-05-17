<template>
  <div id="app">
    <NavBar />
    <router-view />

    <div id="myfooter">
      <AppFooter />
    </div>
  </div>
</template>

<script>
import NavBar from "./components/navbar/navbar.vue";
import AppFooter from "./components/AppFooter.vue";

import { getFirestore, doc, setDoc } from "firebase/firestore";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase/firebase.js";

export default {
  name: "App",
  components: {
    NavBar,
    AppFooter,
  },
  data() {
    return {
      email: "",
      password: "",
      birthday: {
        day: "",
        month: "",
        year: "",
      },
    };
  },
  methods: {
    async handleSubmit() {
      if (!this.email || !this.password) {
        alert("Please fill in all fields!");
        return;
      }

      try {
        // Create a new user
        const userCredential = await createUserWithEmailAndPassword(auth, this.email, this.password);
        const user = userCredential.user;

        // Save additional user info to Firestore
        const db = getFirestore();
        await setDoc(doc(db, "users", user.uid), {
          email: this.email,
          birthday: this.birthday,
        });

        alert("Signup successful and user data stored!");
      } catch (error) {
        console.error("Error:", error.message);
        alert(error.message);
      }
    },
  },
};
</script>


<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #FFC107; /* Apply primary theme color to text */
  background-color: #191b31;/* Subtle frosted background */
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

/* Optional: make links/buttons use theme color */
a, button {
  color: #FFC107;
}

button {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid #FFC107;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  background-color: #FFC107;
  color: black;
}

.myfooter {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.05);
  padding: 10px;
  color: #FFC107;
}
</style>
