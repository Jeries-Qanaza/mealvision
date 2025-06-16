<template>
  <div class="camera-container">
    <h1>YOLO Detection</h1>
    <video 
      ref="videoElement" 
      autoplay 
      playsinline 
      :class="{ mirrored: isFrontCamera }"
    ></video>

    <div class="controls">
      <button @click="takeSnapshot" class="snapshot-btn" :disabled="!isCameraReady || isProcessing">
        <img class="btn-icon" src="@/assets/snappingCamer.png" alt="Snapshot icon">
        <span class="btn-text">Take Snapshot</span>
      </button>

      <div 
        class="upload-zone"
        :class="{ 'drag-over': isDragOver }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <img class="btn-icon" src="@/assets/upload_icon.png" alt="Upload icon">
        <span class="btn-text">Upload Image</span>
        <div class="drag-text">or drag & drop here</div>
        <input 
          ref="fileInput"
          type="file" 
          accept="image/*" 
          @change="handleFileUpload" 
          class="file-input" 
        />
      </div>
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
      isProcessing: false,
      isDragOver: false,
      isFrontCamera: false
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
            facingMode: { ideal: 'environment' },
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        };

        const videoElement = this.$refs.videoElement;
        if (!videoElement) throw new Error('Video element not found');

        this.debugInfo = 'Requesting camera permissions...';
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);

        videoElement.srcObject = this.stream;

        // Get camera settings to determine if it's front-facing
        const videoTrack = this.stream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();
        this.isFrontCamera = settings.facingMode === 'user';

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
          this.debugInfo = 'Detection complete.';
          this.$emit('items-updated', this.detectedLabels);
        }, "image/jpeg");

      } catch (error) {
        this.debugInfo = `Snapshot error: ${error.message}`;
        console.error('Detection error:', error);
        this.detectedLabels = '';
      } finally {
        this.isProcessing = false;
      }
    },
    handleDragOver(event) {
      event.preventDefault();
      this.isDragOver = true;
    },
    handleDragLeave(event) {
      event.preventDefault();
      this.isDragOver = false;
    },
    async handleDrop(event) {
      event.preventDefault();
      this.isDragOver = false;

      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
          await this.processImageFile(file);
        } else {
          this.debugInfo = 'Please drop an image file.';
        }
      }
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      await this.processImageFile(file);
    },
    async processImageFile(file) {
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
  padding: 15px;
  max-width: 100%;
  box-sizing: border-box;
}

video {
  width: 100%;
  max-width: 640px;
  height: auto;
  border: 2px solid orange;
  border-radius: 10px;
  object-fit: cover;
}

video.mirrored {
  transform: scaleX(-1);
}

.controls {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 15px;
  margin: 15px auto;
  max-width: 640px;
  flex-wrap: nowrap;
}

.snapshot-btn,
.upload-zone {
  flex: 1;
  min-width: 0;
  padding: 12px 16px;
  font-size: 14px;
  background-color: orange;
  color: black;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: relative;
  text-align: center;
}

.snapshot-btn:hover:not(:disabled),
.upload-zone:hover {
  background-color: darkorange;
  transform: translateY(-2px);
}

.snapshot-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cccccc;
}

.upload-zone {
  border: 2px dashed transparent;
  min-height: 70px;
}

.upload-zone.drag-over {
  background-color: #ff6b35;
  border-color: #ff4500;
  transform: scale(1.02);
}

.btn-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.btn-text {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.2;
}

.drag-text {
  font-size: 10px;
  opacity: 0.8;
  font-weight: normal;
  line-height: 1;
}

.file-input {
  display: none;
}

.debug-info {
  margin: 15px auto 0;
  color: #888;
  font-size: 12px;
  text-align: left;
  max-width: 640px;
  word-break: break-word;
  padding: 0 15px;
  box-sizing: border-box;
}

#labels {
  margin: 15px auto 0;
  font-weight: bold;
  font-size: 16px;
  max-width: 640px;
  padding: 0 15px;
  box-sizing: border-box;
  word-wrap: break-word;
}

/* Responsive and other media queries remain unchanged */
</style>
