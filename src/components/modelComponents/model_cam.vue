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
      <button
        @click="takeSnapshot"
        class="snapshot-btn"
        :disabled="
          !isCameraReady || isProcessing || isAppBusy || isSizeLimitReached
        "
      >
        <img
          class="btn-icon"
          src="@/assets/snappingCamer.png"
          alt="Snapshot icon"
        />
        <span class="btn-text">Take Snapshot</span>
      </button>

      <div
        class="upload-zone"
        :class="{
          'drag-over': isDragOver,
          disabled: isProcessing || isAppBusy || isSizeLimitReached,
        }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <img
          class="btn-icon"
          src="@/assets/upload_icon.png"
          alt="Upload icon"
        />
        <span class="btn-text">Upload Images</span>
        <div class="drag-text">or drag & drop here</div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileUpload"
          class="file-input"
          :disabled="isProcessing || isAppBusy || isSizeLimitReached"
          multiple
        />
      </div>
    </div>

    <div v-if="previewImages.length > 0" class="glassy-preview">
      <div class="image-grid">
        <div v-for="(img, index) in previewImages" :key="index" class="thumb">
          <img :src="img.url" :alt="'Preview ' + (index + 1)" />
          <button
            @click="deleteImage(index)"
            class="delete-btn"
            title="Delete image"
          >
            ×
          </button>
        </div>
      </div>
      <div class="limit-note">
        <span>{{ sizeLimitMessage }} | Images: {{ previewImages.length }}</span>
        <div v-if="isSizeLimitReached" style="color: red; font-weight: bold">
          Maximum size reached!
        </div>
      </div>
    </div>

    <div v-if="isProcessing" class="loading-dots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>

    <div id="labels">
      Detected Labels: <span>{{ allDetectedItems.join(", ") }}</span>
    </div>

    <div v-if="debugInfo" class="debug-info">
      <pre>{{ debugInfo }}</pre>
    </div>
  </div>
</template>

<script>
const API_BASE = process.env.VUE_APP_API_BASE; // Save the Backend url in a variable

export default {
  name: "ModelCam",
  props: {
    isAppBusy: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["camera-error", "camera-ready", "items-updated", "processing-state"],
  data() {
    return {
      stream: null,
      debugInfo: null,
      isCameraReady: false,
      isDragOver: false,
      isFrontCamera: false,
      isProcessing: false, // Local processing for spinner
      // State for multi-image & size limit
      previewImages: [], // Holds { url, labels, size }
      allDetectedItems: [],
      MAX_TOTAL_SIZE: 15 * 1024 * 1024, // 15MB limit
    };
  },
  computed: {
    // Computed properties for size management
    currentTotalSize() {
      return this.previewImages.reduce((total, img) => total + img.size, 0);
    },
    isSizeLimitReached() {
      return this.currentTotalSize >= this.MAX_TOTAL_SIZE;
    },
    sizeLimitMessage() {
      const currentMB = (this.currentTotalSize / 1024 / 1024).toFixed(1);
      const maxMB = (this.MAX_TOTAL_SIZE / 1024 / 1024).toFixed(1);
      return `Total size: ${currentMB} / ${maxMB} MB`;
    },
  },
  mounted() {
    this.initCamera();
  },
  beforeUnmount() {
    this.stopCamera();
  },
  methods: {
    async initCamera() {
      this.debugInfo = "Initializing camera...";
      this.isCameraReady = false;
      try {
        const constraints = {
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        };
        const videoElement = this.$refs.videoElement;
        if (!videoElement) throw new Error("Video element not found");
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.srcObject = this.stream;
        const videoTrack = this.stream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();
        this.isFrontCamera = settings.facingMode === "user";
        this.$emit("camera-ready");
        await new Promise((resolve, reject) => {
          videoElement.onloadedmetadata = () =>
            videoElement.play().then(resolve).catch(reject);
          videoElement.onerror = () => reject(new Error("Video load error"));
          setTimeout(() => reject(new Error("Video load timeout")), 5000);
        });
        this.debugInfo = "Camera is ready!";
        this.isCameraReady = true;
      } catch (error) {
        this.debugInfo = `Camera error: ${error.message}`;
        this.$emit("camera-error", error);
        this.stopCamera();
      }
    },

    async takeSnapshot() {
      if (
        !this.isCameraReady ||
        this.isProcessing ||
        this.isAppBusy ||
        this.isSizeLimitReached
      )
        return;

      const video = this.$refs.videoElement;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          this.debugInfo = "Failed to create image blob.";
          return;
        }
        if (this.currentTotalSize + blob.size > this.MAX_TOTAL_SIZE) {
          alert(
            `Cannot add snapshot. Total size would exceed the ${
              this.MAX_TOTAL_SIZE / 1024 / 1024
            }MB limit.`
          );
          return;
        }
        // Create a pseudo-file object with a unique name for the blob
        const snapshotFile = new File([blob], `snapshot-${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        await this.processFiles([snapshotFile]);
      }, "image/jpeg");
    },
    // Unified file list processing with duplicate check
    async processFiles(files) {
      if (this.isProcessing || this.isAppBusy) return;

      this.$emit("processing-state", true);
      this.isProcessing = true;

      let initialDebugInfo = this.debugInfo;

      for (const file of files) {
        // Check for duplicates by filename. If found, skip this file.
        if (this.previewImages.some((img) => img.name === file.name)) {
          console.warn(`Skipping duplicate file: ${file.name}`);
          continue; // Move to the next file in the loop
        }

        if (this.currentTotalSize + file.size > this.MAX_TOTAL_SIZE) {
          alert(
            `Could not add "${file.name}". Total size would exceed the ${
              this.MAX_TOTAL_SIZE / 1024 / 1024
            }MB limit.`
          );
          break;
        }

        try {
          const formData = new FormData();
          formData.append("image", file, file.name);

          this.debugInfo = `Sending "${file.name}" to server...`;

          const response = await fetch(`${API_BASE}/detect`, {
            method: "POST",
            body: formData,
          });
          if (!response.ok)
            throw new Error(`Detection failed for ${file.name}`);

          const result = await response.json();
          const uniqueLabels = [...new Set(result.labels)];

          const previewURL = await this.readFileAsDataURL(file);
          this.previewImages.push({
            name: file.name, // Store the file name
            url: previewURL,
            labels: uniqueLabels,
            size: file.size,
          });
          this.updateAllDetectedItems();
        } catch (error) {
          this.debugInfo = `Error: ${error.message}`;
          console.error("Processing error:", error);
          break;
        }
      }

      this.debugInfo =
        this.previewImages.length > 0
          ? "All detections complete."
          : initialDebugInfo;
      this.isProcessing = false;
      this.$emit("processing-state", false);
    },

    // HELPER to read file for preview
    readFileAsDataURL(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
      });
    },

    // Event handlers now just delegate to processFiles
    async handleFileUpload(event) {
      await this.processFiles(event.target.files);
      event.target.value = ""; // Allow re-selecting same file
    },
    async handleDrop(event) {
      event.preventDefault();
      this.isDragOver = false;
      await this.processFiles(event.dataTransfer.files);
    },

    triggerFileInput() {
      if (this.isProcessing || this.isAppBusy || this.isSizeLimitReached)
        return;
      this.$refs.fileInput.click();
    },

    // Methods for managing the preview grid
    deleteImage(index) {
      this.previewImages.splice(index, 1);
      this.updateAllDetectedItems();
    },
    updateAllDetectedItems() {
      const allItems = this.previewImages.flatMap((img) => img.labels);
      this.allDetectedItems = [...new Set(allItems)];
      this.$emit("items-updated", this.allDetectedItems);
    },

    handleDragOver(event) {
      event.preventDefault();
      if (!this.isProcessing && !this.isAppBusy && !this.isSizeLimitReached) {
        this.isDragOver = true;
      }
    },
    handleDragLeave(event) {
      event.preventDefault();
      this.isDragOver = false;
    },

    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach((track) => track.stop());
        this.stream = null;
      }
      const videoElement = this.$refs.videoElement;
      if (videoElement) videoElement.srcObject = null;
      this.isCameraReady = false;
      this.debugInfo = "Camera stopped.";
    },
  },
};
</script>

<style scoped>
.upload-zone.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cccccc;
}
.upload-zone.disabled:hover {
  background-color: #cccccc;
  transform: none;
}
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
.upload-zone:hover:not(.disabled) {
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
@media (max-width: 768px) {
  .camera-container {
    padding: 10px;
  }
  .controls {
    gap: 10px;
    margin: 10px auto;
  }
  .snapshot-btn,
  .upload-zone {
    padding: 10px 12px;
    font-size: 13px;
  }
  .btn-icon {
    width: 20px;
    height: 20px;
  }
  .btn-text {
    font-size: 13px;
  }
  .drag-text {
    font-size: 9px;
  }
  #labels {
    font-size: 14px;
  }
}
@media (max-width: 480px) {
  .camera-container {
    padding: 8px;
  }
  .controls {
    gap: 8px;
    margin: 8px auto;
  }
  .snapshot-btn,
  .upload-zone {
    padding: 8px 10px;
    font-size: 12px;
    min-height: 60px;
  }
  .btn-icon {
    width: 18px;
    height: 18px;
  }
  .btn-text {
    font-size: 12px;
  }
  .drag-text {
    font-size: 8px;
  }
  #labels {
    font-size: 13px;
  }
  .debug-info {
    font-size: 11px;
  }
}
@media (orientation: landscape) and (max-height: 500px) {
  .camera-container {
    padding: 5px;
  }
  video {
    max-height: 200px;
  }
  .controls {
    margin: 8px auto;
  }
  .snapshot-btn,
  .upload-zone {
    padding: 6px 10px;
    min-height: 50px;
  }
}
@media (hover: none) and (pointer: coarse) {
  .snapshot-btn,
  .upload-zone {
    min-height: 48px;
  }
  .snapshot-btn:active,
  .upload-zone:active {
    transform: scale(0.98);
  }
}
.loading-dots {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px auto 0;
  gap: 6px;
  height: 24px;
}
.loading-dots .dot {
  width: 8px;
  height: 8px;
  background: orange;
  border-radius: 50%;
  animation: dot-flash 1.2s infinite ease-in-out;
}
.loading-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes dot-flash {
  0%,
  80%,
  100% {
    opacity: 0.2;
    transform: scale(1);
  }
  40% {
    opacity: 1;
    transform: scale(1.4);
  }
}
/* Styles for the preview grid */
.glassy-preview {
  margin: 10px auto;
  padding: 15px;
  max-width: 640px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}
.image-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.thumb {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ccc;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.delete-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: all 0.2s ease;
}
.delete-btn:hover {
  background: rgba(255, 68, 68, 1);
  transform: scale(1.1);
}
.limit-note {
  margin-top: 10px;
  font-size: 12px;
  color: white;
  text-align: center;
}
</style>
