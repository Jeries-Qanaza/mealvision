<template>
  <NavBar style="background-color: #174329;"/>
  <div class="contact-us-container">
    <div class="contact-us-form">
      <h2 class="heading-gradient">Contact Us</h2>
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
        <button
          type="submit"
          class="button-gradient"
          :class="{ loading: loading }"
          :disabled="loading"
        >
          {{ loading ? 'Sending...' : 'Send Message' }}
        </button>
      </form>
    </div>
    <div class="contact-us-illustration">
      <img
        src="@/assets/contact.jpg"
        alt="Contact Image"
        style="max-width: 100%; max-height: 300px; object-fit: cover; border-radius: 12px; box-shadow: 0 8px 20px #719920;"
      />
    </div>
  </div>
</template>

<script>
import NavBar from "../components/navbar/navbar.vue";
export default {
  name: "ContactUs",
  components: {
    NavBar,
  },
  data() {
    return {
      name: "",
      email: "",
      message: "",
      loading: false,
    };
  },
  methods: {
    handleSubmit() {
      this.loading = true;
      fetch('https://mealvision.onrender.com/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: this.name,
          email: this.email,
          message: this.message,
        }),
      })
        .then((response) => {
          if (!response.ok) throw new Error('Failed to send email');
          return response.json();
        })
        .then((data) => {
          alert('Message Sent! We will contact you shortly.');
          this.name = this.email = this.message = '';
          console.log('Success:', data);
        })
        .catch((error) => {
          console.error('Error:', error);
          alert('Something went wrong. Please try again later.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
  }
}
</script>

<style scoped>
.contact-us-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px;
  border-radius: 16px;
  background-color: #ffffff;
  box-shadow: 0 12px 24px #174329;
  flex-wrap: wrap;
  margin: 20px;
  margin-top: 7%;
  border: 1px solid #174329;
}

.contact-us-form {
  flex: 1;
  max-width: 500px;
  margin-right: auto;
  margin-left: auto;
}

.contact-us-form h2 {
  margin-bottom: 30px;
  font-size: 32px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  background-image: linear-gradient(to right, #719920, #174329);
  -webkit-background-clip: text;
  color: transparent;
  text-shadow: 1px 1px 2px rgba(113, 153, 32, 0.4);
}

.form-group {
  margin-bottom: 25px;
}

input,
textarea {
  width: 100%;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #174329;
  font-size: 16px;
  transition: border-color 0.3s;
  background-color: #f8f8f8;
  color: #333;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #174329;
  box-shadow: 0 4px 8px rgba(113, 153, 32, 0.3);
}

textarea {
  resize: vertical;
}

.button-gradient {
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 18px;
  font-weight: 500;
  background-image: linear-gradient(to right, #719920, #174329);
  box-shadow: 0 5px 10px rgba(113, 153, 32, 0.3);
  border: 2px solid #719920;
}

.button-gradient:hover {
  background-image: linear-gradient(to right, #89b833, #174329);
  box-shadow: 0 6px 12px rgba(113, 153, 32, 0.4);
  transform: translateY(-2px);
}

.contact-us-illustration {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.contact-us-illustration img {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 10px 30px #174329;
  transition: transform 0.3s ease;
}

.contact-us-illustration img:hover {
  transform: scale(1.04);
}

@media (max-width: 768px) {
  .contact-us-container {
    flex-direction: column;
    align-items: stretch;
    padding: 20px;
  }

  .contact-us-form {
    max-width: 100%;
    margin: 0 auto;
  }

  .contact-us-illustration {
    margin-top: 30px;
  }

  .contact-us-illustration img {
    max-height: 250px;
  }
}

@media (max-width: 480px) {
  .contact-us-form h2 {
    font-size: 28px;
  }

  input,
  textarea {
    font-size: 14px;
    padding: 12px;
  }

  .button-gradient {
    font-size: 16px;
    padding: 12px 24px;
  }
}

.button-gradient.loading {
  position: relative;
  pointer-events: none;
  color: transparent;
  background-color: #174329;
  opacity: 0.9;
}

.button-gradient.loading::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 12px 0 white, -12px 0 white;
  transform: translate(-50%, -50%);
  animation: dots 1s infinite ease-in-out;
}

@keyframes dots {
  0%, 80%, 100% {
    box-shadow: 12px 0 rgba(255, 255, 255, 0.3), -12px 0 rgba(255, 255, 255, 0.3);
  }
  40% {
    box-shadow: 12px 0 white, -12px 0 white;
  }
}
</style>
