<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { API_BASE_URL } from '../config';

const router = useRouter();
const username = ref('');
const password = ref('');
const email = ref('');
const verificationCode = ref('');
const isSendingCode = ref(false);
const countdown = ref(0);
const cookies = ref('');

const showNotification = ref(false);
const notificationMessage = ref('');

const showError = (message) => {
  notificationMessage.value = message;
  showNotification.value = true;
  setTimeout(() => {
    showNotification.value = false;
  }, 3000);
};

const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const sendVerificationCode = async () => {
  if (!email.value) {
    showError('请输入邮箱地址');
    return;
  }
  
  if (!validateEmail(email.value)) {
    showError('邮箱格式不正确');
    return;
  }
  
  isSendingCode.value = true;
  countdown.value = 60;
  
  try {
    await axios.post(`${API_BASE_URL}/send-verification-code`, {
      email: email.value
    });
    
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
        isSendingCode.value = false;
      }
    }, 1000);
  } catch (error) {
    showError('发送验证码失败: ' + error.response?.data?.message || '网络错误');
    isSendingCode.value = false;
  }
};

const register = async () => {
  if (!username.value.trim()) {
    showError('请输入用户名');
    return;
  }
  if (!email.value.trim()) {
    showError('请输入邮箱地址');
    return;
  }
  if (!validateEmail(email.value)) {
    showError('邮箱格式不正确');
    return;
  }
  if (!verificationCode.value.trim()) {
    showError('请输入验证码');
    return;
  }
  if (!password.value.trim()) {
    showError('请输入密码');
    return;
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/register`, {
      username: username.value,
      password: password.value,
      email: email.value,
      verificationCode: verificationCode.value
    });
    
    if (response.data.status === 'success') {
      router.push('/account/login');
    } else {
      showError(response.data.message || '注册失败');
    }
  } catch (error) {
    showError('注册失败: ' + (error.response?.data?.message || '网络错误'));
  }
};
onMounted(() => {
  cookies.value = document.cookie;
});
</script>

<template>
  <div class="auth-container bg-gradient-to-r from-blue-500 to-purple-500">
    <div class="notification-bar" :class="{ show: showNotification }">
      {{ notificationMessage }}
    </div>
    
    <div class="auth-wrapper">
      <div class="glass-card">
        <div class="logo-area">
          <img src="/vite.svg" alt="系统Logo">
        </div>
        <h2>创建ByInfo ID</h2>
        <form @submit.prevent="register" class="auth-form" novalidate>
          <input v-model="username" type="text" placeholder="用户名" required />
          <input v-model="email" type="email" placeholder="邮箱" required />
          <div class="code-input-group">
            <input v-model="verificationCode" type="text" placeholder="验证码" required />
            <button 
              type="button" 
              class="send-code-btn"
              @click="sendVerificationCode"
              :disabled="isSendingCode">
              {{ isSendingCode ? `${countdown}秒后重试` : '获取验证码' }}
            </button>
          </div>
          <input v-model="password" type="password" placeholder="密码" required />
          <button type="submit" class="primary-button">注册</button>
        </form>
        <div class="auth-footer">
          <span>已有账号？</span>
          <router-link to="/account/login">立即登录</router-link>
        </div>
      </div>
    </div>

    <!-- 将 cookie 显示部分移动到这里 -->

  </div>
</template>

<style scoped>
.notification-bar {
  position: fixed;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #ff4d4f;
  color: white;
  padding: 12px 24px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: top 0.5s ease;
  max-width: 80%;
  text-align: center;
}

.notification-bar.show {
  top: 20px;
}

.auth-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.auth-wrapper {
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 520px;
  padding: 2rem;
}
.glass-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  padding: 2.5rem;
  width: 420px;
  margin: 0 auto;
}
.glass-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-weight: 500;
}
.glass-card input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: #2c3e50;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}
.glass-card input:focus {
  outline: none;
  border-color: rgba(0, 122, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.primary-button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 12px;
  background: rgba(38, 45, 145, 0.8);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.primary-button:hover {
  background: rgba(38, 45, 145, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 93.5%;
}

.auth-form input {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: #2c3e50;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.auth-form input:focus {
  outline: none;
  border-color: rgba(0, 122, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}


.auth-footer a {
  color: #262d91;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.25rem;
}
@media (max-width: 768px) {
  .glass-card {
    padding: 1.5rem;
    border-radius: 20px;
  }
  .glass-card h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
}
@media (max-width: 480px) {
  .glass-card {
    padding: 1.25rem;
    border-radius: 16px;
  }
  .glass-card input,
  .primary-button {
    padding: 0.65rem;
  }
  .logo-area img {
    height: 40px;
  }
}
.logo-area {
  text-align: center;
  margin-bottom: 1.5rem;
}

.logo-area img {
  height: 48px;
}

.glass-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-weight: 500;
  gap:1rem;
}

.glass-card input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: #2c3e50;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.glass-card input:focus {
  outline: none;
  border-color: rgba(0, 122, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.primary-button {
  width: 106%;
  padding: 0.75rem;
  border: none;
  border-radius: 12px;
  background: rgba(38, 45, 145, 0.8);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.primary-button:hover {
  background: rgba(38, 45, 145, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.auth-footer a {
  color: rgba(38, 45, 145, 0.8);
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.25rem;
}
.code-input-group {
  display: flex;
  width: 106%;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.code-input-group input {
  flex: 1.1;
  margin: 0;
  width: 10px;
}

.send-code-btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 12px;
  background: rgba(38, 45, 145, 0.15);
  color: #262d91;

  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  width: auto;
}

</style>

