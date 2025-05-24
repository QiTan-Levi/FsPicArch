<template>
  <div class="body">
    <!-- 导航栏 -->
    <nav class="nav-bar">
      <div class="nav-content">
        <div class="nav-left">
          <router-link to="/" class="logo">
            <img src="@/assets/logo.svg" alt="Logo" class="logo-image">
            <span class="logo-text">ImageShare</span>
          </router-link>
        </div>
        <div class="nav-right">
          <div class="user-info">
            <span class="user-name">示例用户</span>
            <div class="dropdown-menu">
              <button class="dropdown-item">登出</button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="home-container">
      <div class="main-content">
        <!-- 上传区域 -->
        <div class="upload-container glass-card">
          <h2>上传新图片</h2>
          <div class="upload-form">
            <div class="image-upload-area">
              <div class="upload-placeholder">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>拖放图片到此处或点击上传</p>
                <p class="upload-hint">支持 JPG, PNG, GIF 格式</p>
              </div>
            </div>
            <input 
              type="file" 
              style="display: none"
            >
            <div class="form-group">
              <label for="image-description">图片描述</label>
              <textarea 
                id="image-description" 
                placeholder="为图片添加描述..."
                rows="3"
              ></textarea>
            </div>
            <button class="submit-button">
              上传图片
            </button>
          </div>
        </div>

        <!-- 我的图片区域 -->
        <div class="glass-card" style="width: 60%;">
          <h2>我的图片</h2>
          <div class="image-grid">
            <div class="image-card">
              <img 
                src="https://via.placeholder.com/300" 
                class="image-thumbnail"
              >
              <div class="image-meta">
                <span class="image-status status-approved">
                  已通过
                </span>
                <button class="delete-button">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            <div class="image-card">
              <img 
                src="https://via.placeholder.com/300" 
                class="image-thumbnail"
              >
              <div class="image-meta">
                <span class="image-status status-pending">
                  审核中
                </span>
                <button class="delete-button">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            <div class="image-card">
              <img 
                src="https://via.placeholder.com/300" 
                class="image-thumbnail"
              >
              <div class="image-meta">
                <span class="image-status status-rejected">
                  已拒绝
                </span>
                <button class="delete-button">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
export default {
  name: 'UserProfileUI',
};
</script>

<style scoped>
/* 基础样式 */
.body {
  font-family: 'Arial', sans-serif;
  margin: 0;
  padding: 0;
  color: #2c3e50;
}

/* 导航栏样式 */
.nav-bar {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.logo-image {
  height: 30px;
  margin-right: 0.5rem;
}

.user-info {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-name {
  margin-right: 0.5rem;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: none;
  min-width: 120px;
}

.user-info:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  width: 100%;
  padding: 0.5rem 1rem;
  text-align: left;
  background: none;
  border: none;
  color: #2c3e50;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

/* 主内容区样式 */
.home-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.main-content {
  display: flex;
  gap: 2rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.upload-container {
  width: 35%;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.image-upload-area {
  border: 2px dashed #a777e3;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-upload-area:hover {
  background: rgba(167, 119, 227, 0.1);
}

.upload-placeholder i {
  font-size: 3rem;
  color: #a777e3;
  margin-bottom: 1rem;
}

.upload-placeholder p {
  margin: 0.5rem 0;
  color: #666;
}

.upload-hint {
  font-size: 0.8rem;
  color: #999;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: bold;
  color: #555;
}

.form-group textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
}

.submit-button {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(110, 142, 251, 0.3);
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 图片网格布局 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}

.image-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.image-card:hover {
  transform: translateY(-5px);
}

.image-thumbnail {
  width: 100%;
  height: 180px;
  object-fit: cover;
  cursor: pointer;
  border-radius: 8px;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0 0 8px 8px;
}

.image-status {
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
}

.status-pending {
  background-color: #ffc107;
  color: #2c3e50;
}

.status-approved {
  background-color: #28a745;
  color: white;
}

.status-rejected {
  background-color: #dc3545;
  color: white;
}

.delete-button {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1rem;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #2c3e50;
}

.modal-image {
  width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.modal-details {
  padding: 1.5rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .upload-container, 
  .glass-card {
    width: 100% !important;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>