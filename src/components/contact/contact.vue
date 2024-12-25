<template>
    <div class="contact-us-container">
      <div class="contact-us-form">
        <h2>Contact us</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <input type="text" v-model="name" placeholder="Name" required />
          </div>
          <div class="form-group">
            <input type="email" v-model="email" placeholder="Email" required />
          </div>
          <div class="form-group">
            <textarea v-model="message" placeholder="Message" rows="4" required></textarea>
          </div>
          <button type="submit">Send Message</button>
        </form>
      </div>
      <div class="contact-us-illustration">
        <img src="@/assets/contact.jpg" alt="Conatct Image" />
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "ContactUs",
    data() {
      return {
        name: "",
        email: "",
        message: "",
      };
    },
    methods: {
      handleSubmit() {
        console.log("Submitted data:", {
          name: this.name,
          email: this.email,
          message: this.message,
        });
        alert("Message Sent! We will contact you shortly.");
      },
    },
  };
  </script>
  
  <style scoped>
  .contact-us-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .contact-us-form {
    flex: 1;
    max-width: 400px;
  }
  
  .contact-us-form h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 24px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  input, textarea {
    width: 100%;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ddd;
    font-size: 14px;
  }
  
  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  .contact-us-illustration {
    flex: 1;
    display: flex;
    justify-content: center;
  }
  
  .contact-us-illustration img {
    max-width: 100%;
    height: auto;
  }
  </style>
  