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
        class="btn btn-solid"
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
        class="btn btn-solid upload-zone-layout"
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
        <span class="btn-text">Upload Images/Videos</span>
        <div class="drag-text">or drag & drop here</div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*,video/*"
          @change="handleFileUpload"
          class="file-input"
          :disabled="isProcessing || isAppBusy || isSizeLimitReached"
          multiple
        />
      </div>
    </div>

    <!-- Video Processing Options -->
    <div v-if="hasVideos" class="video-options">
      <div class="option-group">
        <label>Frame extraction interval:</label>
        <select v-model="frameInterval">
          <option value="1">Every frame</option>
          <option value="5">Every 5th frame</option>
          <option value="10">Every 10th frame</option>
          <option value="30">Every 30th frame (~1 sec)</option>
        </select>
      </div>
      
      <div class="option-group">
        <label>Max frames per video:</label>
        <select v-model="maxFrames">
          <option value="10">10 frames</option>
          <option value="20">20 frames</option>
          <option value="50">50 frames</option>
          <option value="100">100 frames</option>
        </select>
      </div>

      <button 
        @click="processAllVideos" 
        class="btn btn-primary"
        :disabled="isProcessing || isAppBusy"
      >
        Process Videos ({{ videoItems.length }} pending)
      </button>
    </div>

    <div v-if="previewImages.length > 0 || videoItems.length > 0" class="glassy-preview">
      <!-- Images Grid -->
      <div v-if="previewImages.length > 0" class="content-section">
        <h3 class="section-title">Images ({{ previewImages.length }})</h3>
        <div class="image-grid">
          <div v-for="(img, index) in previewImages" :key="'img-' + index" class="thumb">
            <img :src="img.url" :alt="'Preview ' + (index + 1)" />
            <div class="item-info">
              <div class="item-name">{{ img.name }}</div>
              <div class="item-labels">{{ img.labels.join(', ') }}</div>
            </div>
            <button
              @click="deleteImage(index)"
              class="delete-btn-modern"
              title="Delete image"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Videos Grid -->
      <div v-if="videoItems.length > 0" class="content-section">
        <h3 class="section-title">Videos ({{ videoItems.length }})</h3>
        <div class="video-grid">
          <div v-for="(video, index) in videoItems" :key="'video-' + index" class="video-thumb">
            <video 
              :src="video.url" 
              :poster="video.poster"
              controls 
              preload="metadata"
              class="video-preview"
            ></video>
            <div class="item-info">
              <div class="item-name">{{ video.name }}</div>
              <div class="item-status" :class="video.status">
                {{ getVideoStatusText(video) }}
              </div>
              <div v-if="video.extractedFrames > 0" class="frame-count">
                {{ video.extractedFrames }} frames extracted
              </div>
              <div v-if="video.labels && video.labels.length > 0" class="item-labels">
                {{ video.labels.join(', ') }}
              </div>
            </div>
            <button
              @click="deleteVideo(index)"
              class="delete-btn-modern"
              title="Delete video"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="limit-note">
        <span>{{ sizeLimitMessage }} | Items: {{ totalItemCount }}</span>
        <div v-if="isSizeLimitReached" style="color: red; font-weight: bold">
          Maximum size reached!
        </div>
      </div>
    </div>

    <div v-if="isProcessing" class="loading-dots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
      <div class="processing-text">{{ processingMessage }}</div>
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
      processingMessage: '',
      // State for multi-image & size limit
      previewImages: [], // Holds { url, labels, size, name }
      videoItems: [], // Holds { url, name, size, status, labels, extractedFrames, poster }
      allDetectedItems: [],
      MAX_TOTAL_SIZE: 15 * 1024 * 1024, // 15MB limit
      // Video processing options
      frameInterval: 10, // Extract every Nth frame
      maxFrames: 20, // Maximum frames to extract per video
    };
  },
  computed: {
    // Computed properties for size management
    currentTotalSize() {
      const imageSize = this.previewImages.reduce((total, img) => total + img.size, 0);
      const videoSize = this.videoItems.reduce((total, video) => total + video.size, 0);
      return imageSize + videoSize;
    },
    isSizeLimitReached() {
      return this.currentTotalSize >= this.MAX_TOTAL_SIZE;
    },
    sizeLimitMessage() {
      const currentMB = (this.currentTotalSize / 1024 / 1024).toFixed(1);
      const maxMB = (this.MAX_TOTAL_SIZE / 1024 / 1024).toFixed(1);
      return `Total size: ${currentMB} / ${maxMB} MB`;
    },
    hasVideos() {
      return this.videoItems.some(video => video.status === 'pending');
    },
    totalItemCount() {
      return this.previewImages.length + this.videoItems.length;
    }
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

    // Separate files into images and videos
    async processFiles(files) {
      if (this.isProcessing || this.isAppBusy) return;

      const imageFiles = [];
      const videoFiles = [];

      for (const file of files) {
        // Check for duplicates by filename
        const isDuplicateImage = this.previewImages.some((img) => img.name === file.name);
        const isDuplicateVideo = this.videoItems.some((video) => video.name === file.name);
        
        if (isDuplicateImage || isDuplicateVideo) {
          console.warn(`Skipping duplicate file: ${file.name}`);
          continue;
        }

        if (this.currentTotalSize + file.size > this.MAX_TOTAL_SIZE) {
          alert(
            `Could not add "${file.name}". Total size would exceed the ${
              this.MAX_TOTAL_SIZE / 1024 / 1024
            }MB limit.`
          );
          break;
        }

        if (file.type.startsWith('image/')) {
          imageFiles.push(file);
        } else if (file.type.startsWith('video/')) {
          videoFiles.push(file);
        }
      }

      // Process images immediately
      if (imageFiles.length > 0) {
        await this.processImageFiles(imageFiles);
      }

      // Add videos to the queue (don't process immediately)
      for (const videoFile of videoFiles) {
        await this.addVideoToQueue(videoFile);
      }
    },

    // Process image files (existing logic)
    async processImageFiles(files) {
      this.$emit("processing-state", true);
      this.isProcessing = true;
      this.processingMessage = 'Processing images...';

      let initialDebugInfo = this.debugInfo;

      for (const file of files) {
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
            name: file.name,
            url: previewURL,
            labels: uniqueLabels,
            size: file.size,
          });
        } catch (error) {
          this.debugInfo = `Error: ${error.message}`;
          console.error("Processing error:", error);
          break;
        }
      }

      this.updateAllDetectedItems();
      this.debugInfo = this.previewImages.length > 0 ? "Image processing complete." : initialDebugInfo;
      this.isProcessing = false;
      this.processingMessage = '';
      this.$emit("processing-state", false);
    },

    // Add video to queue without processing
    async addVideoToQueue(videoFile) {
      const previewURL = await this.readFileAsDataURL(videoFile);
      const poster = await this.generateVideoPoster(videoFile);
      
      this.videoItems.push({
        name: videoFile.name,
        url: previewURL,
        poster: poster,
        size: videoFile.size,
        status: 'pending', // pending, processing, completed, error
        labels: [],
        extractedFrames: 0,
        file: videoFile // Keep reference to original file
      });
    },

    // Generate video poster/thumbnail
    async generateVideoPoster(videoFile) {
      return new Promise((resolve) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        video.addEventListener('loadedmetadata', () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          video.currentTime = Math.min(1, video.duration / 2); // Seek to middle or 1 second
        });

        video.addEventListener('seeked', () => {
          ctx.drawImage(video, 0, 0);
          resolve(canvas.toDataURL('image/jpeg'));
        });

        video.addEventListener('error', () => {
          resolve(null); // Return null if poster generation fails
        });

        video.src = URL.createObjectURL(videoFile);
      });
    },

    // Process all pending videos
    async processAllVideos() {
      const pendingVideos = this.videoItems.filter(video => video.status === 'pending');
      if (pendingVideos.length === 0) return;

      this.$emit("processing-state", true);
      this.isProcessing = true;

      for (let i = 0; i < pendingVideos.length; i++) {
        const video = pendingVideos[i];
        this.processingMessage = `Processing video ${i + 1} of ${pendingVideos.length}: ${video.name}`;
        await this.processVideo(video);
      }

      this.updateAllDetectedItems();
      this.isProcessing = false;
      this.processingMessage = '';
      this.$emit("processing-state", false);
    },

    // Process individual video
    async processVideo(videoItem) {
      const videoIndex = this.videoItems.findIndex(v => v.name === videoItem.name);
      if (videoIndex === -1) return;

      this.videoItems[videoIndex].status = 'processing';

      try {
        const frames = await this.extractFramesFromVideo(videoItem.file);
        this.videoItems[videoIndex].extractedFrames = frames.length;

        const allLabels = new Set();

        for (let i = 0; i < frames.length; i++) {
          this.processingMessage = `Processing frame ${i + 1}/${frames.length} of ${videoItem.name}`;
          
          const formData = new FormData();
          formData.append("image", frames[i], `${videoItem.name}_frame_${i}.jpg`);

          const response = await fetch(`${API_BASE}/detect`, {
            method: "POST",
            body: formData,
          });

          if (response.ok) {
            const result = await response.json();
            result.labels.forEach(label => allLabels.add(label));
          }
        }

        this.videoItems[videoIndex].labels = Array.from(allLabels);
        this.videoItems[videoIndex].status = 'completed';
        this.debugInfo = `Video "${videoItem.name}" processed successfully. Found: ${Array.from(allLabels).join(', ')}`;

      } catch (error) {
        console.error('Video processing error:', error);
        this.videoItems[videoIndex].status = 'error';
        this.debugInfo = `Error processing video "${videoItem.name}": ${error.message}`;
      }
    },

    // Extract frames from video
    async extractFramesFromVideo(videoFile) {
      return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const frames = [];

        video.addEventListener('loadedmetadata', () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          
          const duration = video.duration;
          const frameCount = Math.min(this.maxFrames, Math.floor(duration * 30 / this.frameInterval)); // Assuming 30fps
          const timeStep = duration / frameCount;
          
          let currentFrame = 0;
          
          const extractFrame = () => {
            if (currentFrame >= frameCount) {
              resolve(frames);
              return;
            }
            
            video.currentTime = currentFrame * timeStep;
            currentFrame++;
          };

          video.addEventListener('seeked', () => {
            ctx.drawImage(video, 0, 0);
            canvas.toBlob((blob) => {
              if (blob) {
                const frameFile = new File([blob], `frame_${frames.length}.jpg`, {
                  type: 'image/jpeg'
                });
                frames.push(frameFile);
              }
              
              setTimeout(extractFrame, 100); // Small delay to ensure frame is processed
            }, 'image/jpeg', 0.8);
          });

          extractFrame();
        });

        video.addEventListener('error', (e) => {
          reject(new Error('Video loading failed'));
        });

        video.src = URL.createObjectURL(videoFile);
      });
    },

    // Get video status text
    getVideoStatusText(video) {
      switch (video.status) {
        case 'pending': return 'Ready to process';
        case 'processing': return 'Processing...';
        case 'completed': return `Complete (${video.labels.length} unique objects)`;
        case 'error': return 'Processing failed';
        default: return 'Unknown status';
      }
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

    // Event handlers
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

    // Methods for managing the preview grids
    deleteImage(index) {
      this.previewImages.splice(index, 1);
      this.updateAllDetectedItems();
    },

    deleteVideo(index) {
      this.videoItems.splice(index, 1);
      this.updateAllDetectedItems();
    },

    updateAllDetectedItems() {
      const imageItems = this.previewImages.flatMap((img) => img.labels);
      const videoItems = this.videoItems.flatMap((video) => video.labels);
      const allItems = [...imageItems, ...videoItems];
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
.video-options {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 15px;
  margin: 15px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.option-group label {
  font-size: 0.9em;
  color: #333;
  font-weight: 500;
}

.option-group select {
  padding: 8px 12px;
  border-radius: 5px;
  border: 1px solid #ddd;
  background: white;
  font-size: 0.9em;
}

.content-section {
  margin-bottom: 20px;
}

.content-section h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.1em;
}

.section-title {
  color: #ff7043 !important;
  font-weight: 600;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.video-thumb {
  position: relative;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.video-preview {
  width: 100%;
  height: 120px;
  object-fit: cover;
  background: #f0f0f0;
}

.item-info {
  padding: 8px;
  font-size: 0.8em;
}

.item-name {
  font-weight: bold;
  margin-bottom: 4px;
  color: #333;
  word-break: break-word;
}

.item-status {
  margin-bottom: 4px;
  font-weight: 500;
}

.item-status.pending {
  color: #ff9800;
}

.item-status.processing {
  color: #2196f3;
}

.item-status.completed {
  color: #4caf50;
}

.item-status.error {
  color: #f44336;
}

.frame-count {
  font-size: 0.75em;
  color: #666;
  margin-bottom: 4px;
}

.item-labels {
  color: #666;
  font-style: italic;
  word-break: break-word;
}

.processing-text {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
  text-align: center;
}

.btn-primary {
  background: #2196f3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Update existing styles */
.camera-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  display: flex;
  gap: 15px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-solid {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.glassy-preview {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  margin: 20px 0;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.thumb {
  position: relative;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.thumb img {
  width: 100%;
  height: 100px;
  object-fit: cover;
}

.delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(244, 67, 54, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.delete-btn-modern {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 6px;
  width: 22px;
  height: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.delete-btn-modern:hover {
  background: rgba(244, 67, 54, 0.8);
  transform: scale(1.05);
}

.loading-dots {
  text-align: center;
  padding: 20px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  margin: 0 2px;
  animation: loading 1.4s ease-in-out infinite both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes loading {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>