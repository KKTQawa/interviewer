<template>
  <div class="main_content">
    <div class="about_card">
      <ul class="tech_list">
        <li>
          <span class="icon"><i class="fa-brands fa-vuejs"></i></span>
          使用 <strong>Vue 3</strong> 开发前端界面
        </li>
        <li>
          <span class="icon"><i class="fa-solid fa-server"></i></span>
          使用 <strong>FastAPI</strong> 开发后端
        </li>
        <li>
          <span class="icon"><i class="fa-solid fa-brain"></i></span>
          由 <strong>讯飞星火大模型</strong>🔥 提供支持
        </li>
        <li>
          <span class="icon"><i class="fa-brands fa-github"></i></span>
          GitHub 地址：
          <a href="https://github.com/KKTQawa" target="_blank">
            github.com/KKTQawa
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 无需特殊脚本
</script>

<style scoped lang="scss">
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

.main_content {
  height: 100%;
  width: 100%;
  padding: 40px;
  background-image: url('../assets/interviewRealTimeBack2.png');
  background-attachment: fixed;
  background-size: 100% 100%;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  color: #fff;
  font-family: 'Segoe UI', sans-serif;
}

.about_card {
    position: relative;
    top: 20%;
    background: rgba(0, 0, 0, 0.6);
    padding: 30px 40px;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
    max-width: 600px;
}

.about_card h1 {
  font-size: 28px;
  margin-bottom: 20px;
  color: #f0f0f0;
}

.tech_list {
  list-style: none;
  padding: 0;
  line-height: 2;
}

.tech_list li {
  display: flex;
  align-items: center;
  font-size: 16px;
  margin-bottom: 10px;
}

.icon {
  margin-right: 12px;
  font-size: 18px;
  color: #61dafb;
}

a {
  color: #7dd3fc;
  text-decoration: underline;
  word-break: break-all;
}
</style>
