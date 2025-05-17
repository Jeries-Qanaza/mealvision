import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";
import { getAuth } from "firebase/auth"; 

const firebaseConfig = {
  apiKey: "AIzaSyBgT9ybD7XDcN1opQNYdgmo8Kpy_gSKmcE",
  authDomain: "mealvision2025.firebaseapp.com",
  projectId: "mealvision2025",
  storageBucket: "mealvision2025.firebasestorage.app",
  messagingSenderId: "244997305685",
  appId: "1:244997305685:web:0c85833c359bda7edd6bdc",
  measurementId: "G-3KG257PRDT"
};

const app = initializeApp(firebaseConfig);
export const db = getDatabase(app); // Realtime Database instance
export const auth = getAuth(app);
