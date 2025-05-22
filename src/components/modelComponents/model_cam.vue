<template>
  <div class="camera-container">
    <h1>YOLO Detection</h1>
    <video ref="videoElement" autoplay playsinline></video>

    <div class="controls">
      <button @click="takeSnapshot" class="snapshot-btn" :disabled="!isCameraReady || isProcessing">
        <i class="fas fa-camera"></i> Take Snapshot
      </button>

    <label class="upload-label">
      <i class="fas fa-upload"></i> Upload Image
      <input type="file" accept="image/*" @change="handleFileUpload" class="file-input" />
    </label>
    </div>

    <div id="labels">Detected Labels: <span>{{ detectedLabels }}</span></div>

    <div v-if="debugInfo" class="debug-info">
      <pre>{{ debugInfo }}</pre>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ModelCam',
  emits: ['camera-error', 'camera-ready'],
  data() {
    return {
      stream: null,
      debugInfo: null,
      detectedLabels: '',
      isCameraReady: false,
      isProcessing: false
    };
  },
  mounted() {
    this.initCamera();
  },
  beforeUnmount() {
    this.stopCamera();
  },
  methods: {
    async initCamera() {
      this.debugInfo = 'Initializing camera...';
      this.isCameraReady = false;

      try {
        const constraints = {
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        };

        const videoElement = this.$refs.videoElement;
        if (!videoElement) throw new Error('Video element not found');

        this.debugInfo = 'Requesting camera permissions...';
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);

        videoElement.srcObject = this.stream;

        this.$emit('camera-ready');

        await new Promise((resolve, reject) => {
          videoElement.onloadedmetadata = () => {
            this.debugInfo = 'Playing video...';
            videoElement.play().then(resolve).catch(reject);
          };
          videoElement.onerror = () => reject(new Error('Video load error'));
          setTimeout(() => reject(new Error('Video load timeout')), 5000);
        });

        this.debugInfo = 'Camera is ready!';
        this.isCameraReady = true;

      } catch (error) {
        this.debugInfo = `Camera error: ${error.message}`;
        console.error('Camera init error:', error);
        this.$emit('camera-error', error);
        this.stopCamera();
      }
    },
    async takeSnapshot() {
      if (!this.isCameraReady || this.isProcessing) return;

      this.isProcessing = true;

      try {
        const video = this.$refs.videoElement;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        this.debugInfo = 'Sending image to server...';

        canvas.toBlob(async (blob) => {
          const formData = new FormData();
          formData.append("image", blob, "snapshot.jpg");

          const response = await fetch("https://mealvision.onrender.com/detect", {
            method: "POST",
            body: formData
          });

          if (!response.ok) throw new Error('Detection failed');

          const result = await response.json();
          const uniqueLabels = [...new Set(result.labels)];

          this.detectedLabels = uniqueLabels.join(", ");
          console.log("Detected Labels:", this.detectedLabels);

          this.debugInfo = 'Detection complete.';
          this.$emit('items-updated', this.detectedLabels);
          this.isProcessing = false;
        }, "image/jpeg");

      } catch (error) {
        this.debugInfo = `Snapshot error: ${error.message}`;
        console.error('Detection error:', error);
        this.detectedLabels = '';
        this.isProcessing = false;
      }
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("image", file);

      this.isProcessing = true;
      this.debugInfo = 'Sending uploaded image to server...';

      try {
        const response = await fetch("https://mealvision.onrender.com/detect", {
          method: "POST",
          body: formData
        });

        if (!response.ok) throw new Error('Detection failed');

        const result = await response.json();
        const uniqueLabels = [...new Set(result.labels)];
        this.detectedLabels = uniqueLabels.join(", ");
        this.debugInfo = 'Detection complete.';
        this.$emit('items-updated', this.detectedLabels);
      } catch (error) {
        this.debugInfo = `Upload error: ${error.message}`;
        console.error('Upload detection error:', error);
        this.detectedLabels = '';
      } finally {
        this.isProcessing = false;
      }
    },
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }

      const videoElement = this.$refs.videoElement;
      if (videoElement) {
        videoElement.srcObject = null;
      }

      this.isCameraReady = false;
      this.debugInfo = 'Camera stopped.';
    }
  }
};
</script>


<style scoped>
.camera-container {
  text-align: center;
  padding: 20px;
}
video {
  width: 100%;
  max-width: 640px;
  border: 2px solid orange;
  border-radius: 10px;
  transform: scaleX(-1);
}
.snapshot-btn {
  margin-top: 15px;
  padding: 10px 20px;
  font-size: 16px;
  background-color: orange;
  color: black;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.snapshot-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cccccc;
}
.file-input {
  margin-top: 15px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.debug-info {
  margin-top: 10px;
  color: #888;
  font-size: 12px;
  text-align: left;
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
  word-break: break-word;
}
#labels {
  margin-top: 15px;
  font-weight: bold;
  font-size: 18px;
}
  .upload-label {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  font-size: 16px;
  background-color: orange;
  color: black;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
}

.upload-label:hover {
  background-color: darkorange;
}

.upload-label i {
  margin-right: 8px;
}

.file-input {
  display: none;
}

</style>
