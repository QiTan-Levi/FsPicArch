<template>
  <div class="home-container bg-gradient-to-r from-blue-500 to-purple-500">
    <!-- 顶部导航栏 -->
    <nav class="nav-bar">
      <div class="nav-content">
        <div class="nav-left">
          <router-link to="/" class="logo">
            <img src="@/assets/logo.svg" alt="Logo" class="logo-image">
            <span class="logo-text" style="font-family: Maple Mono NF CN;">ByInfo - Fs Picture Archieve</span>
          </router-link>
        </div>
        <div class="nav-right">
          <div v-if="isLoggedIn" class="user-info">
            <span class="user-name">{{ userName }}</span>
            <div class="dropdown-menu">
              <router-link to="/upload" class="dropdown-item">上传照片</router-link>
              <router-link to="/my-profile" class="dropdown-item">个人资料</router-link>
              <button @click="handleLogout" class="dropdown-item logout-button">退出登录</button>
            </div>
          </div>
          <div v-else>
            <router-link to="/account/login" class="nav-button">登录</router-link>
            <router-link to="/account/register" class="nav-button primary">注册</router-link>
          </div>
        </div>
      </div>
    </nav>
    <!-- 主要内容区 -->
    <main class="main-content hgs-container">
      <div class="notice-container glass-card"
        style="width: 51%; margin-right: 0%;margin-top: 70px;margin-bottom: -1px;">
        <h1>上传须知</h1>
        <p>为了打造一个优质的原创平台，在上传照片时，您需要仔细阅读并遵守以下要求：</p>
        <ul style="font-family: 汉仪中园简;font-size: 16px;line-height: 44px">
          <li>
            <strong>格式要求</strong>：仅接受 <span class="maple-mono">JPG/JPEG</span> 格式照片，比例建议 <span class="maple-mono">4:3</span>
          </li>
          <li>
            <strong>大小限制</strong>：单张照片文件大小不得超过 <span class="maple-mono">30MB</span>
          </li>
          <li>
            <strong>内容规范</strong>
            <ul>
              <li>请勿上传带有明显人脸的照片，以及包含网络梗图的内容</li>
              <li>您上传的照片须确保不侵犯任何个人、组织、企业等主体的合法权益</li>
            </ul>
          </li>

          <li>
            <strong>版权声明</strong>：所有上传照片必须为上传者本人拍摄，如上传者侵权与平台无关
          </li>
          <li>
            <strong>信息完整</strong>：任何信息缺失时，都标注 “N/A”
          </li>
          <li>
            <strong>内容合规</strong>：上传需严格遵守国家法律法规，禁止政治敏感、虚假等违规信息
          </li>
        </ul>
        <h1>填写规范</h1>
        <ul style="font-family: hermit;font-size: 16px;line-height: 50px">
          <li>
            <strong>航空器信息</strong>
            <ul>
              <li><strong>注册号、机型</strong>
                <ul>
                  <li>确认是否确实有 <b>“ <span class="maple-mono">-</span> ”</b></li>
                  <li>空客机型需填出Airbus <u><b><span class="maple-mono">A321</span></b></u></li>
                  <li>波音机型需填出Boeing <u><b><span class="maple-mono">777-300ER</span></b></u></li>
                </ul>
              </li>
              <li><strong>航空公司</strong>：除内地航司外，请填写英文全称 </li>
            </ul>
          </li>
          <li>
            <strong>照片信息</strong>
            <ul>
              <li><strong>拍摄时间：</strong>任何时候都允许使用北京时间，国外建议使用拍摄当地时间</li>
              <li><strong>拍摄地点：</strong>中国大陆及港澳台机场填写中文全称，其他填写英文全称</li>
              <li><strong>天气：</strong>建议以当时的<span class="maple-mono">ATIS</span>信息为准，若未知则根据照片实际情况选择</li>
            </ul>
          </li>
        </ul>
      </div>

      <div class=" upload-container glass-card" style="margin-top: 70px">
        <h2>上传照片</h2>
        <form @submit.prevent="handleSubmit" class="upload-form">
          <!-- 照片上传区域 -->
          <div>
            <div>
              <div class="image-upload-area aa"
                style="max-width: 98%; width: 355px; height:200px; display: flex; align-items: center; justify-content: center;margin: auto;margin-left: 1.1%;padding: 8px;"
                @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
                <input type="file" ref="fileInput" @change="handleFileChange" accept="image/jpeg,image/jpg"
                   style="display: none; place-items: center; max-width: 10%; max-height: 10%;">
                <div v-if="!previewImage" class="upload-placeholder r1">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <p>点击或拖拽照片到此处上传</p>
                  <p class="upload-hint">支持 <span class="maple-mono">JPEG</span>、<span class="maple-mono">JPG</span> 格式，最大 <span class="maple-mono">30MB</span></p>
                </div>
                <img v-else :src="previewImage" alt="预览照片" class="preview-image"
                  style="height: 200px;max-width: 80%; width: 80%; min-height: 150px; object-fit: contain;  border-radius: 8px; margin: 0px;">
              </div>
            </div>
          </div>
          <!-- 图片EXIF信息 -->

          <div
            style="display: flex; justify-content: center; align-items: center; width: 468.9px; height: 170px; margin-left: 0.8%;"
            class="upload-container glass-card">
            <div v-if="selectedFile">
              <canvas id="histogramChart" width="350" height="200"
                style="display: block; box-sizing: border-box; max-width: 100%; max-height: 100%;"></canvas>
            </div>
            <div style="width: 222px;font-family: Maple Mono NF CN Light;line-height: 150%;">
              <ul style="list-style-type:''">
                <li v-if="!selectedFile"
                  style="list-style-type:'';padding-left: 0; margin-left: 0; max-width: 200px; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-box-orient: vertical;">
                  当您上传图片后，此处将显示图片的<span class="maple-mono">RGB</span>直方图和<span class="maple-mono">EXIF</span>信息
                </li>
                <li v-else>
                  <ul style="list-style-type:'·';padding-left: 0;margin-left: 0;">
                    <li><strong>{{ exifData.airtistacopryrgt || 'N/A' }}</strong></li>
                    <li><strong>{{ exifData.cameraMake || 'N/A' }}</strong> {{ exifData.cameraModel || 'N/A' }} </li>
                    <li><strong>ISO </strong>{{ exifData.isoSpeed || 'N/A' }}</li>

                    <li><strong>SS&nbsp</strong>{{ exifData.exposureTime || 'N/A' }}</li>
                    <li><strong>F </strong>{{ exifData.apertureValue || 'N/A' }}</li>
                    <li><strong>FL </strong>{{ exifData.focalLength || 'N/A' }}</li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>

          <!-- 照片信息表单 -->
          <div class="upload-container glass-card" style="width: 300px">
            <h3>航空器信息</h3>
            <div class="form-group">
              <label>航班号</label>
              <input type="text" v-model="formData.flightNumber" placeholder="e.g. HU7051 / MU501" style="font-family: osifont;" required>
            </div>
            <div class="form-group">
              <label>注册号</label>
              <input type="text" v-model="formData.registrationNumber" placeholder="e.g. B-2447 / JA383A" style="font-family: osifont;" required>
            </div>
            <div class="form-group">
              <label>机型</label>
              <input type="text" v-model="formData.model" placeholder="e.g. Airbus A320-251N / Boeing 787-8" style="font-family: osifont;" required >
            </div>
            <div class="form-group" style="position: relative; z-index: 100;">
              <label>航空公司</label>
              <input type="text" v-model="formData.airlineOperator" placeholder="e.g. 中国南方航空 / Cathay Pacific" style="font-family: osifont;"
                required>
            </div>
          </div>

          <div class="upload-container glass-card " style="width: 472.1px; margin-left: 0.6%;">
            <div class="photo-section">
              <h3>照片信息</h3>
              <div class="form-group">
                <label>拍摄时间</label>
                <div style="display: flex; gap: 10px; align-items: center;font-family: hermit;">
                  <select v-model="formData.timeZone"
                    style="width: 45%; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 12px; background: rgba(255, 255, 255, 0.3); color: #2c3e50; font-size: 0.95rem; transition: all 0.3s ease;font-family: osifont;">
                    <option value="UTC+12">UTC+12 (奥克兰)</option>
                    <option value="UTC+11">UTC+11 (霍尼亚拉)</option>
                    <option value="UTC+10">UTC+10 (悉尼)</option>
                    <option value="UTC+9">UTC+9 (东京)</option>
                    <option value="UTC+8" selected>UTC+8 (北京)</option>
                    <option value="UTC+7">UTC+7 (曼谷)</option>
                    <option value="UTC+6">UTC+6 (达卡)</option>
                    <option value="UTC+5">UTC+5 (伊斯兰堡)</option>
                    <option value="UTC+4">UTC+4 (阿布扎比)</option>
                    <option value="UTC+3">UTC+3 (莫斯科)</option>
                    <option value="UTC+2">UTC+2 (开罗)</option>
                    <option value="UTC+1">UTC+1 (巴黎)</option>
                    <option value="UTC+0">UTC+0 (伦敦)</option>
                    <option value="UTC-1">UTC-1 (佛得角群岛)</option>
                    <option value="UTC-2">UTC-2 (南乔治亚岛)</option>
                    <option value="UTC-3">UTC-3 (里约热内卢)</option>
                    <option value="UTC-4">UTC-4 (圣地亚哥)</option>
                    <option value="UTC-5">UTC-5 (纽约)</option>
                    <option value="UTC-6">UTC-6 (芝加哥)</option>
                    <option value="UTC-7">UTC-7 (丹佛)</option>
                    <option value="UTC-8">UTC-8 (洛杉矶)</option>
                    <option value="UTC-9">UTC-9 (安克雷奇)</option>
                    <option value="UTC-10">UTC-10 (檀香山)</option>
                    <option value="UTC-11">UTC-11 (中途岛)</option>
                    <option value="UTC-12">UTC-12 (贝克岛)</option>
                  </select>
                  <input type="datetime-local" style="font-family: osifont; width: 60%;"
                    v-model="formData.shootTime" required>

                </div>
              </div>
              <div class="form-group">
                <label>拍摄地点</label>
                <input type="text" v-model="formData.location"
                  placeholder="e.g. 厦门高崎国际机场 / O'Hare International Airport" style="font-family: osifont;" required>
              </div>
              <div class="form-group">
                <label>天气</label>
                <div class="category-suggestions">
                  <button v-for="condition in weatherOptions" :key="condition.label" type="button" style="font-size: 13.5px;"
                    :class="['category-tag', { active: formData.weatherConditions.includes(condition.value) }]"
                    @click="toggleWeatherCondition(condition.value)">
                    {{ condition.label }}
                  </button>
                </div>
              </div>
              <div class="form-group">
                <label>类型（可以留空）</label>
                <div class="category-suggestions">
                  <button v-for="type in imageTypeOptions" :key="type.label" type="button" style="font-size: 13.3px;"
                    :class="['category-tag', { active: formData.imageTypes.includes(type.value) }]"
                    @click="toggleImageType(type.value)">
                    {{ type.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>


          <div class="upload-container glass-card" style="grid-column: span 2;width: 91.1%">
            <div class="form-group">
              <label style="margin-top:1.3rem ;">照片描述</label>
              <textarea v-model="formData.description" rows="4" placeholder="可以填写表单未提及但值得说明的内容"
                style="resize: none;width: 97%;height: 100%;font-size: 15px;margin-left: -1%;font-family:hermit "></textarea>
            </div>
          </div>
          <!-- 上传进度 -->
          <div class="upload-progress" v-if="uploadProgress > 0 && uploadProgress < 100">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span>{{ uploadProgress }}%</span>
          </div>
          <button type="submit" class="submit-button" :disabled="uploading">{{ uploading ? '上传中...' : '提交' }}</button>

        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';

import { useRouter } from 'vue-router';
import axios from 'axios';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const router = useRouter();
const searchQuery = ref('');
// Remove these unnecessary lines:
// const app = createApp(App);
// app.use(Antd);
// app.mount('#app');

// Removed Vuex state dependencies
// const isLoggedIn = computed(() => store.state.isLoggedIn);
// const userName = computed(() => store.state.userName);
// const userAvatar = computed(() => store.state.userAvatar);

// Placeholder for login state (can be replaced with localStorage or other methods)
const isLoggedIn = ref(false); // Example: Default to false
const userName = ref(''); // Example: Default empty


// Simplified onMounted - remove store actions
onMounted(() => {
  // store.dispatch('initLoginState'); // Removed store action
  // Check local storage for login state, for example
  isLoggedIn.value = localStorage.getItem('isLoggedIn') === 'true';
  userName.value = localStorage.getItem('userName') || '';

});
const fileInput = ref(null);
const previewImage = ref('');
const uploadProgress = ref(0);
const uploading = ref(false);

const formData = reactive({
  username: userName.value,
  model: '',
  location: '',
  shootTime: '',
  description: '',
  categories: [],
  registrationNumber: '',
  flightNumber: '',
  airlineOperator: '',
  imageTypes: [],
  weatherConditions: [],
  timeZone: 'UTC+8' // 设置默认时区为北京时间
});


const weatherOptions = [
  { label: '晴', value: 'Sunny' },
  { label: '多云', value: 'Cloudy' },
  { label: '阴', value: 'Overcast' },
  { label: '雨', value: 'Rain' },
  { label: '雪', value: 'Snow' },
  { label: '雾', value: 'Fog' },
  { label: '霾', value: 'Haze' },
  { label: '雹', value: 'Hail' }
];

const imageTypeOptions = [
  { label: '机场', value: 'Airport' },
  { label: '驾驶舱', value: 'Cockpit' },
  { label: '艺术', value: 'Artistic' },
  { label: '地服', value: 'Ground' },
  { label: '货运', value: 'Cargo' },
  { label: '彩绘', value: 'Special_Livery' },
  { label: '夜摄', value: 'Night' },
];

const triggerFileInput = () => {
  //限制input的文件类型
  fileInput.value.click();

};

// 添加一个变量来存储选中的文件
const selectedFile = ref(null);
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    validateAndPreviewFile(file);
    parseExif(file); // 调用解析EXIF信息的函数

    // 读取图像数据并绘制RGB折线图
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.getElementById('histogramChart');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, img.width, img.height);
        drawRGBLineChart(imageData); // 确保每次都调用此函数
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0];
  if (file) {
    selectedFile.value = file;
    validateAndPreviewFile(file);
    parseExif(file); // 调用解析EXIF信息的函数
  }
};

const validateAndPreviewFile = (file) => {
  // 验证文件类型
  if (!['image/jpeg'].includes(file.type)) {
    alert('请上传 JPEG 格式的照片');
    return;
  }

  // 验证文件大小（30MB）
  if (file.size > 30 * 1024 * 1024) {
    alert('照片大小不能超过 30MB');
    return;
  }

  // 预览照片
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const toggleCategory = (category) => {
  const index = formData.categories.indexOf(category);
  if (index === -1) {
    formData.categories.push(category);
  } else {
    formData.categories.splice(index, 1);
  }
};

const handleSubmit = async () => {
  if (!selectedFile.value) {
    alert('请选择要上传的照片');
    return;
  }

  if (!formData.model || !formData.location || !formData.shootTime) {
    alert('请填写完整的照片信息');
    return;
  }

  if (!isLoggedIn.value) {
    alert('请先登录再上传照片');
    router.push('/account/login');
    return;
  }

  if (!localStorage.getItem('token')) {
    alert('登录状态已过期，请重新登录');
    router.push('/account/login');
    return;
  }

  uploading.value = true;
  uploadProgress.value = 0;

  const uploadData = new FormData();
  uploadData.append('username', userName.value);
  uploadData.append('timeZone', formData.timeZone);
  uploadData.append('shootTime', formData.shootTime);
  uploadData.append('registrationNumber', formData.registrationNumber);
  uploadData.append('flightNumber', formData.flightNumber || 'N/A');
  uploadData.append('model', formData.model);
  uploadData.append('weatherConditions', JSON.stringify(formData.weatherConditions || [])); // 确保不为空
  uploadData.append('description', formData.description);
  uploadData.append('location', formData.location);
  uploadData.append('imagedata', selectedFile.value);
  uploadData.append('categories', JSON.stringify(formData.imageTypes || [])); // 确保不为空
  uploadData.append('file', selectedFile.value);
  uploadData.append('airlineOperator', formData.airlineOperator);
  try {
    const response = await axios.post('/api/upload', uploadData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      }
    });

    if (response.status === 200 || response.status === 201) {
      alert('上传成功！');
      console.log('Upload response:', response.data);
      formData.model = '';
      formData.location = '';
      formData.shootTime = '';
      formData.description = '';
      formData.categories = [];
      previewImage.value = '';
      selectedFile.value = null;
      fileInput.value.value = '';
      router.push('/upload')//刷新页面
    } else {
      throw new Error(response.data.message || '上传失败');
    }
  } catch (error) {
    console.error('上传失败:', error);
    alert(`上传失败: ${error.response?.data?.message || error.message || '请重试'}`);
  } finally {
    uploading.value = false;
    uploadProgress.value = 0;
  }
};

// Simplified logout - remove store action
const handleLogout = async () => {
  try {
    // Clear all authentication related data
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userName');
    localStorage.removeItem('token');

    // Reset state
    isLoggedIn.value = false;
    userName.value = '';

    // Redirect to home
    router.push('/');
  } catch (error) {
    console.error('登出操作失败:', error);
    // Ensure redirect even if error occurs
    router.push('/');
  }
};


// Define toggleImageType and toggleWeatherCondition methods
const toggleImageType = (type) => {
  const index = formData.imageTypes.indexOf(type);
  if (index === -1) {
    formData.imageTypes.push(type);
  } else {
    formData.imageTypes.splice(index, 1);
  }
};

const toggleWeatherCondition = (condition) => {
  const index = formData.weatherConditions.indexOf(condition);
  if (index === -1) {
    formData.weatherConditions.push(condition);
  } else {
    formData.weatherConditions.splice(index, 1);
  }
};

import { useScrollLock } from 'vue-scroll-lock';

onMounted(() => {
  document.body.style.overflow = 'hidden';
});
const exifData = reactive({
  cameraModel: '',
  exposureTime: '',
  apertureValue: '',
  isoSpeed: '',

});

import exifr from 'exifr';

async function parseExif(file) {
  try {
    function formatShutterSpeed(exposureTime) {
      if (exposureTime < 1) {
        const denominator = Math.round(1 / exposureTime);
        return `1/${denominator}`;
      } else {
        return `${Math.round(exposureTime)}''`;
      }
    }
    const exifDataa = await exifr.parse(file);
    console.log('EXIF Data:', exifDataa); // 输出EXIF数据
    if (exifDataa.Artist == exifDataa.Copyright) {
      exifData.airtistacopryrgt = exifDataa.Artist || 'N/A';
    } else {
      exifData.airtistacopryrgt = exifDataa.Artist + " / " + exifDataa.Copyright || 'N/A';
    };
    const datelsy = exifDataa.DateTimeOriginal || 'N/A';
    function formatDateToISO(date) {
      if (typeof date === 'string') {
        date = new Date(date);
      }
      if (isNaN(date.getTime())) {
        return 'N/A';
      }
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    const shootTimeValue = exifDataa.DateTimeOriginal || 'N/A';
    formData.shootTime = formatDateToISO(shootTimeValue);

    exifData.focalLength = exifDataa.FocalLength + 'mm' || 'N/A';
    exifData.cameraMake = exifDataa.Make || 'N/A';
    exifData.cameraModel = exifDataa.Model || 'N/A';
    exifData.exposureTime = formatShutterSpeed(exifDataa.ExposureTime) || 'N/A';
    exifData.apertureValue = exifDataa.FNumber || 'N/A'; exifData.apertureValue = exifDataa.FNumber || 'N/A';
    exifData.isoSpeed = exifDataa.ISO || 'N/A';
    exifData.OffsetTime = exifDataa.OffsetTime || 'N/A';

    function convertTimeZone(offset) {
      if (!offset) {
        return 'UTC+8';
      }
      const sign = offset[0];
      const hours = offset.slice(1, 3);
      return `UTC${sign}${parseInt(hours)}`;
    }

    formData.timeZone = convertTimeZone(exifDataa.OffsetTime) || 'UTC+8';

  } catch (error) {
    console.error('Error reading EXIF data:', error);
    alert('无法读取EXIF数据，请检查文件格式。');
  }
}

import Chart from 'chart.js/auto'; // 引入chart.js

// ... existing code ...


const calculateRGBHistogram = (imageData) => {
  const redHistogram = new Array(256).fill(0);
  const greenHistogram = new Array(256).fill(0);
  const blueHistogram = new Array(256).fill(0);

  for (let i = 0; i < imageData.data.length; i += 4) {
    redHistogram[imageData.data[i]]++;
    greenHistogram[imageData.data[i + 1]]++;
    blueHistogram[imageData.data[i + 2]]++;
  }

  return { redHistogram, greenHistogram, blueHistogram };
};
let chartInstance = null; // 用于存储图表实例

const drawRGBLineChart = (imageData) => {
  const ctx = document.getElementById('histogramChart').getContext('2d');

  // 如果已有图表实例，先销毁它
  if (chartInstance) {
    chartInstance.destroy();
  }

  const { redHistogram, greenHistogram, blueHistogram } = calculateRGBHistogram(imageData);

  chartInstance = new Chart(ctx, {
    type: 'line', // 修改为折线图
    data: {
      labels: Array.from({ length: 256 }, (_, i) => i),
      datasets: [
        {
          // label: '红色通道',
          data: redHistogram,
          borderColor: 'rgba(255, 99, 132, 0.5)',
          fill: false, // 不填充
          borderWidth: 1.2, // 设置红色线条粗细
        },
        {
          // label: '绿色通道', 
          data: greenHistogram,
          borderColor: 'rgba(75, 192, 192, 0.5)',
          fill: false, // 不填充
          borderWidth: 1.2, // 设置绿色线条粗细
        },
        {
          // label: '蓝色通道',
          data: blueHistogram,
          borderColor: 'rgba(54, 162, 235, 0.5)',
          fill: false, // 不填充
          borderWidth: 1.2, // 设置蓝色线条粗细
        }
      ]
    },
    options: {
      plugins: {
        legend: {
          display: false // 不显示图例
        },
        title: {
          display: true,
          text: 'RGB直方图',
          font: {
            size: 15,
            weight: 'hermit'
          }
        }
      },
      scales: {
        x: { display: false },
        y: { display: false },
      },
      animation: {
        duration: 0 // 禁用动画
      }
    }
  });
};

</script>


<style scoped>
input:not([type="file"]) {
  outline: none;
}

/* 基础样式 */
.body {
  overflow: hidden;
}

/* 布局容器 */
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding-top: 10px;
  padding-left: 1rem;
  overflow: hidden;
  height: 80vh;
  margin: 0;
}

.hgs-container {
  gap: 1rem;
  height: auto;
}

.home-container .hgs-container {
  height: auto
}

.main-content {
  max-width: 1750px;
  padding: 0.2rem;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 2rem;
  height: 100%;
  width: 100%;
}

.glass-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  padding: 2.5rem;
  margin: 10 auto;
  z-index: 11;
}

.glass-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-weight: 500;
}


/* 导航栏相关 */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  padding: 0 2rem;
  z-index: 1000;
  backdrop-filter: blur(12px);
}

.nav-content {
  max-width: 1750px;
  height: 100%;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-right {
  display: flex;
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #262d91;
}

.logo-image {
  height: 32px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-button {
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  text-decoration: none;
  color: #262d91;
  transition: all 0.3s ease;
}

.nav-button.primary {
  background: rgba(38, 45, 145, 0.8);
  color: white;
}

/* 表单组件 */
.form-group {
  position: relative;
  z-index: 1;
  margin-bottom: 10rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #262d91;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 93.5%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: #2c3e50;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  gap: 15rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: rgba(0, 122, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

/* 上传区域样式 */
.upload-container {
  width: 82%;
  z-index: 10;
}

.upload-container.glass-card {
  padding-top: 1.1rem;
  padding-bottom: 2rem;
}

.upload-container.glass-card .form-group {
  margin-bottom: 0.6rem;
}

.upload-container h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #262d91;
}

.upload-form {
  display: grid;
  gap: 1rem;
}

.image-upload-area {
  border: 2px dashed rgba(38, 45, 145, 0.3);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  grid-column: span 2;
}

.image-upload-area:hover {
  border-color: rgba(38, 45, 145, 0.8);
}

/* 图片预览和上传提示 */
.upload-placeholder {
  display: center;
  color: #666;
}

.upload-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #262d91;
  display: center;
}

.upload-hint {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.5rem;
}

.preview-image {
  max-width: 100%;
  min-width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

/* 分类标签 */
.category-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-tag {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #262d91;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-tag.active {
  background: rgba(38, 45, 145, 0.8);
  color: white;
}

/* 上传进度 */
.upload-progress {
  margin-top: 1rem;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #262d91;
  transition: width 0.3s ease;
}

/* 按钮样式 */
.submit-button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 12px;
  background: rgba(38, 45, 145, 0.8);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  grid-column: span 2;
}

.submit-button:hover {
  background: rgba(38, 45, 145, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 用户信息和下拉菜单 */
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  padding: 10px;
}

.user-name {
  font-weight: 500;
  color: #262d91;
}

.dropdown-menu {
  position: absolute;
  top: 20px;
  right: 0;
  transform: translateX(3%);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 0.45rem;
  box-shadow: 3px 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  display: none;
  z-index: 1000;
  margin-top: 25px;
  transition: opacity 0.3s ease;
  opacity: 10;
}

.user-info:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  padding: 0.75rem 1rem;
  color: #262d91;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.3s ease;
  text-align: left;
  border: none;
  background: none;
  font-size: 1rem;
  cursor: pointer;
}
.logout-button {
  display: block;
  padding: 0.75rem 1rem;
  color: #262d91;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.3s ease;
  text-align: left;
  border: none;
  background: none;
  font-size: 1rem;
  cursor: pointer;
  width: 100%;
}
.dropdown-item:hover {
  background: rgba(38, 45, 145, 0.1);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .nav-content {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
  }

  .nav-bar {
    height: auto;
  }
}

@media (max-width: 480px) {
  .nav-left {
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }

  .nav-right {
    width: 100%;
    justify-content: center;
  }

  .upload-container {
    padding: 1rem;
    margin: 0;
  }

  .form-group input,
  .form-group textarea {
    font-size: 16px;
  }
}

/* 其他工具类 */
.v-select {
  width: 100%;
}

select {
  background: transparent;
}

select option {
  scrollbar-width: none;
}

select::-webkit-scrollbar {
  display: none;
}
.maple-mono {
  font-family: 'Maple Mono NF CN Regular', monospace;
}
</style>
