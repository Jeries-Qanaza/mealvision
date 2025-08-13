<template>
  <div class="camera-container">
    <h1>YOLO Detection</h1>

    <div class="camera-view">
      <video
        ref="videoElement"
        autoplay
        playsinline
        :class="{ mirrored: isFrontCamera }"
      ></video>
      
      <!-- Camera Controls Overlay -->
      <div class="camera-controls-overlay">
        <div class="camera-controls-bottom">
          <!-- Video Mode Button -->
          <button 
            @click="toggleVideoMode" 
            class="camera-mode-btn"
            :class="{ active: isVideoMode }"
            :disabled="!isCameraReady || isProcessing"
            title="Video Mode"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z" fill="currentColor"/>
            </svg>
            <span class="mode-text">{{ isVideoMode ? 'VIDEO' : 'VIDEO' }}</span>
          </button>
          
          <!-- Capture/Record Button -->
          <button
            @click="handleCaptureClick"
            class="camera-capture-btn"
            :class="{ 
              recording: isRecording,
              'video-mode': isVideoMode 
            }"
            :disabled="!isCameraReady || isProcessing || isAppBusy || isSizeLimitReached"
          >
            <div class="capture-outer-ring"></div>
            <div class="capture-inner" :class="{ 'recording-square': isRecording }"></div>
          </button>
          
          <!-- Switch Camera Button -->
          <button 
            @click="switchCamera" 
            class="camera-switch-btn"
            :disabled="!isCameraReady || isProcessing"
            title="Switch Camera"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M16 7l4-4m0 0l-4-4m4 4H9a5 5 0 0 0 0 10h2.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 17l-4 4m0 0l4 4m-4-4h11a5 5 0 0 0 0-10h-2.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="mode-text">SWITCH</span>
          </button>
        </div>
      </div>
    </div>

    <div class="controls">
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
              <span class="delete-x">✕</span>
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
              <span class="delete-x">✕</span>
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
      // Video recording state
      isVideoMode: false,
      isRecording: false,
      mediaRecorder: null,
      recordedChunks: [],
      // State for multi-image & size limit
      previewImages: [], // Holds { url, labels, size, name }
      videoItems: [], // Holds { url, name, size, status, labels, extractedFrames, poster }
      allDetectedItems: [],
      MAX_TOTAL_SIZE: 15 * 1024 * 1024, // 15MB limit
      // Video processing options (fixed values)
      frameInterval: 30, // Extract every 30th frame (1 FPS from 30 FPS video)
      maxFrames: 100, // Maximum frames to extract per video
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

    // Toggle between photo and video mode
    toggleVideoMode() {
      if (this.isRecording) return; // Don't switch while recording
      this.isVideoMode = !this.isVideoMode;
      this.debugInfo = this.isVideoMode ? "Video mode activated" : "Photo mode activated";
    },

    // Handle capture button click (photo or video)
    async handleCaptureClick() {
      if (this.isVideoMode) {
        if (this.isRecording) {
          this.stopRecording();
        } else {
          this.startRecording();
        }
      } else {
        this.takeSnapshot();
      }
    },

    // Start video recording
    async startRecording() {
      if (!this.isCameraReady || this.isProcessing || !this.stream) return;

      try {
        this.recordedChunks = [];
        this.mediaRecorder = new MediaRecorder(this.stream, {
          mimeType: 'video/webm;codecs=vp9'
        });

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.recordedChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          this.saveRecordedVideo();
        };

        this.mediaRecorder.start();
        this.isRecording = true;
        this.debugInfo = "Recording started...";

      } catch (error) {
        this.debugInfo = `Recording error: ${error.message}`;
        console.error('Recording error:', error);
      }
    },

    // Stop video recording
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
        this.debugInfo = "Recording stopped. Processing...";
      }
    },

    // Save recorded video
    async saveRecordedVideo() {
      if (this.recordedChunks.length === 0) return;

      const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
      const videoFile = new File([blob], `recorded-video-${Date.now()}.webm`, {
        type: 'video/webm'
      });

      if (this.currentTotalSize + blob.size > this.MAX_TOTAL_SIZE) {
        alert(
          `Cannot save video. Total size would exceed the ${
            this.MAX_TOTAL_SIZE / 1024 / 1024
          }MB limit.`
        );
        return;
      }

      // Add to video queue and auto-process
      await this.addVideoToQueue(videoFile);
      // Auto-process the video immediately at 1 FPS
      const videoItem = this.videoItems[this.videoItems.length - 1];
      await this.processVideo(videoItem);
      this.debugInfo = "Video saved and processed successfully!";
    },

    // Add switch camera method
    async switchCamera() {
      if (!this.isCameraReady || this.isProcessing) return;
      
      this.stopCamera();
      
      // Toggle camera preference
      const newFacingMode = this.isFrontCamera ? "environment" : "user";
      
      try {
        const constraints = {
          video: {
            facingMode: { ideal: newFacingMode },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        };
        
        const videoElement = this.$refs.videoElement;
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.srcObject = this.stream;
        
        const videoTrack = this.stream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();
        this.isFrontCamera = settings.facingMode === "user";
        
        await new Promise((resolve, reject) => {
          videoElement.onloadedmetadata = () =>
            videoElement.play().then(resolve).catch(reject);
          videoElement.onerror = () => reject(new Error("Video load error"));
          setTimeout(() => reject(new Error("Video load timeout")), 5000);
        });
        
        this.isCameraReady = true;
        this.debugInfo = "Camera switched successfully!";
      } catch (error) {
        this.debugInfo = `Camera switch error: ${error.message}`;
        // Fallback to original camera
        this.initCamera();
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

      // Process videos immediately (auto-process at 1 FPS)
      for (const videoFile of videoFiles) {
        await this.addVideoToQueue(videoFile);
        // Auto-process the video immediately
        const videoItem = this.videoItems[this.videoItems.length - 1];
        await this.processVideo(videoItem);
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
        status: 'processing', // Start processing immediately
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

    // Extract frames from video at 5 FPS
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
          // Extract frames at 5 FPS (every 0.2 seconds)
          const frameInterval = 0.2; // 5 FPS = 1/5 = 0.2 seconds between frames
          const frameCount = Math.min(this.maxFrames, Math.floor(duration / frameInterval));
          
          let currentFrame = 0;
          
          const extractFrame = () => {
            if (currentFrame >= frameCount) {
              resolve(frames);
              return;
            }
            
            video.currentTime = currentFrame * frameInterval;
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
          reject(new Error(e,'Video loading failed'));
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
      // Stop any ongoing recording
      if (this.isRecording) {
        this.stopRecording();
      }
      
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