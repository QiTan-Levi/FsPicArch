<template>
    <div :class="['upload-page', currentTheme]">
      <h1>多图片上传</h1>
      <div class="upload-container">
        <input type="file" multiple @change="handleFileChange" />
        <button @click="uploadFiles">上传</button>
      </div>
      <div class="theme-switcher">
        <button @click="setTheme('purple')">紫色系</button>
        <button @click="setTheme('green')">绿色系</button>
        <button @click="setTheme('dark')">暗色系</button>
      </div>
      <div class="preview">
        <div v-for="(file, index) in selectedFiles" :key="index" class="preview-item">
          <p>{{ file.name }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  // 引入 Vue 组合式 API
  import { ref } from 'vue'
  
  // 选择的文件
  const selectedFiles = ref([])
  
  // 当前主题，默认紫色
  const currentTheme = ref('purple')
  
  // 文件选择事件
  function handleFileChange(event) {
    selectedFiles.value = Array.from(event.target.files)
  }
  
  // 文件上传逻辑（此处为占位）
  function uploadFiles() {
    console.log('上传文件：', selectedFiles.value)
  }
  
  // 设置主题
  function setTheme(theme) {
    currentTheme.value = theme
  }
  </script>
  
  <style scoped>
  /* 通用布局样式 */
  .upload-page {
    font-family: Arial, sans-serif;
    padding: 2rem;
    max-width: 50rem;
    margin: 0 auto;
  }
  
  /* 上传容器样式 */
  .upload-container {
    margin-bottom: 2rem;
    display: flex;
    gap: 1rem;
  }
  
  /* 主题切换按钮 */
  .theme-switcher button {
    margin-right: 1rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s ease;
  }
  
  /* 文件预览区 */
  .preview {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
    gap: 1rem;
  }
  
  .preview-item {
    background: var(--card-bg);
    color: var(--text-color);
    padding: 1rem;
    border-radius: 1rem;
    box-shadow: 0 0.2rem 0.5rem rgba(0,0,0,0.1);
    text-align: center;
  }
  
  /* ===== 主题色定义 ===== */
  
  /* 紫色系 */
  .purple {
    --primary: #7e5bef;
    --background: #f5f3ff;
    --card-bg: #e0d9f7;
    --text-color: #4b0082;
  }
  
  /* 绿色系 */
  .green {
    --primary: #10b981;
    --background: #f0fdf4;
    --card-bg: #bbf7d0;
    --text-color: #064e3b;
  }
  
  /* 暗色系 */
  .dark {
    --primary: #374151;
    --background: #1f2937;
    --card-bg: #4b5563;
    --text-color: #f9fafb;
  }
  
  /* 应用主题变量 */
  .upload-page {
    background: var(--background);
    color: var(--text-color);
  }
  
  /* 按钮主题 */
  .theme-switcher button {
    background: var(--primary);
    color: white;
  }
  
  /* 上传按钮 */
  .upload-container button {
    background: var(--primary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
  }
  </style>
  