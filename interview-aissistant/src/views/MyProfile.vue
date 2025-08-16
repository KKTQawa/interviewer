<template>
    <div class="main_all">
        <div class="profile-container">
            <div class="profile-left">
                <user-avatar ref="avatarRef" />
            </div>
            <div class="profile-right">
                <!-- 用户名 -->
                <div class="info-row">
                    <label>用户名:</label>
                    <input v-if="editing.username" v-model="tempUsername" @blur="is_saveEdit('username')"
                        class="info-input" />
                    <div v-else class="info-text">{{ username }}</div>
                    <n-button text @click="toggleEdit('username')" style="color:white;">
                        <n-icon size="18">
                            <Edit />
                        </n-icon>
                    </n-button>
                    <n-button text @click="copyToClipboard(username)" style="color:white;margin-left:10px;">
                        <n-icon size="18">
                            <Copy />
                        </n-icon>
                    </n-button>
                </div>

                <!-- 邮箱 -->
                <div class="info-row">
                    <label>邮箱:</label>
                    <input v-if="editing.email" v-model="tempEmail" @blur="is_saveEdit('email')" class="info-input" />
                    <div v-else class="info-text">{{ email }}</div>
                    <n-button text @click="toggleEdit('email')" style="color:white;">
                        <n-icon size="18">
                            <Edit />
                        </n-icon>
                    </n-button>
                    <n-button text @click="copyToClipboard(email)" style="color:white;margin-left:10px;">
                        <n-icon size="18">
                            <Copy />
                        </n-icon>
                    </n-button>
                </div>

                <!-- 简介 -->
                <div class="info-row">
                    <label>个人简介:</label>
                    <input v-if="editing.bio" v-model="tempBio" @blur="is_saveEdit('bio')" class="info-input" />
                    <div v-else class="bio-text">{{ bio }}</div>
                    <n-button text @click="toggleEdit('bio')" style="color:white;">
                        <n-icon size="18">
                            <Edit />
                        </n-icon>
                    </n-button>
                    <n-button text @click="copyToClipboard(bio)" style="color:white;margin-left:10px;">
                        <n-icon size="18">
                            <Copy />
                        </n-icon>
                    </n-button>
                </div>
            </div>
        </div>
       
            <n-button @click="logout" type="warning" style="position:relative;margin-top: 20%;margin-left:auto;margin-right:auto;">
                退出登录
            </n-button>
      
        <a-modal v-model:open="amodel" title="提示">
            <p>确认修改？</p>
            <template #footer>
                <n-button @click="amodel = false">取消</n-button>
                <n-button type="error" @click="saveEdit">确认</n-button>
            </template>
        </a-modal>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue';
import UserAvatar from '../components/UserAvatar.vue';
import { message } from 'ant-design-vue'
import { NButton, NIcon, NInput, NText, NResult } from 'naive-ui'
import { Edit, Copy } from '@vicons/carbon'
import axios from "../utils/axios";
import { useStore } from '../store';
import { useRouter } from 'vue-router';
import rules from '../utils/rules'

const store = useStore();
const router = useRouter();

const userInfo = ref(store.getUser())
const username = ref(userInfo.value.username || '');
const email = ref(userInfo.value.email || '');
const bio = ref(userInfo.value.bio || '还没有添加任何自我介绍~~~');
// 临时编辑数据
const tempUsername = ref('')
const tempEmail = ref('')
const tempBio = ref('')

// 编辑状态
const editing = ref({
    username: false,
    email: false,
    bio: false
})

// 切换编辑状态
const toggleEdit = (field) => {
    if (editing.value[field] == false) {
        editing.value['username'] = false
        editing.value['email'] = false
        editing.value['bio'] = false
    }
    editing.value[field] = !editing.value[field]
    if (editing.value[field]) {
        // 进入编辑模式时，保存当前值到临时变量
        tempUsername.value = username.value
        tempEmail.value = email.value
        tempBio.value = bio.value
    }
}
const amodel = ref(false)
const is_saveEdit = (field) => {
    let flag = false
    if (field === 'username' && tempUsername.value !== username.value) flag = true
    if (field === 'email' && tempEmail.value !== email.value) flag = true
    if (field === 'bio' && tempBio.value !== bio.value) flag = true
    if (flag) {
        amodel.value = true;
    } else {
        editing.value[field] = false
    }
}

function validate() {
    let is_username = true;
    let is_email = true;
    if (username.value != '')
        is_username = rules.usernameRegex.test(tempUsername.value)
    if (email.value != '')
        rules.emailRegex.test(tempEmail.value)
    return is_username && is_email
}
const logout = () => {
  // 清理本地存储
  ['id', 'refreshToken', 'accessToken'].forEach(key => {
    localStorage.removeItem(key)
  })

  router.push({ path: '/login' })  
}
let avatarRef = null
onMounted(async () => {
    userInfo.value = store.getUser()
    username.value = userInfo.value.username || '';
    email.value = userInfo.value.email || '';
    bio.value = userInfo.value.bio || '还没有添加任何自我介绍~~~';
    let avatarSrc = ''

    try {
        const res = await axios.get('/user/query_info',{
            params: {
                user_id: localStorage.getItem('id')
            }
        })
        console.log('获取初始化信息: ', res.data)
        username.value = res.data.username
        email.value = res.data.email
        bio.value = res.data.preference?.bio || '还没有添加任何自我介绍~~~'
        avatarSrc = res.data.preference?.avatar || ''
        store.userInfo.avatarSrc = avatarSrc
        store.userInfo.bio = bio.value
      if(avatarRef){
        avatarRef.seturl(avatarSrc)
      }
    } catch (e) {
        console.error('获取初始化信息失败:', e)
    }
})

// 保存编辑
async function saveEdit() {
    const isValid = validate()
    if (!isValid) {
        message.error('信息格式不正确！')
        return
    }
    const preferences = ref({
        id: localStorage.getItem('id'),
        username: tempUsername.value,
        email: tempEmail.value,
        preferences: {
            bio: tempBio.value
        }
    })
    //console.log('执行更新操作',preferences.value)
    try {
        const res = await axios.post('/user/update', preferences.value)
        if (res?.code == 0) {
            message.error('更改失败')
            editing.value['username'] = false
            editing.value['email'] = false
            editing.value['bio'] = false
            return
        }
        username.value = tempUsername.value
        email.value = tempEmail.value
        bio.value = tempBio.value
        message.success('更改成功')
    } catch (error) {
        console.log(error)
        message.error('更改失败')
    }
    editing.value['username'] = false
    editing.value['email'] = false
    editing.value['bio'] = false
    amodel.value = false
}
// 复制到剪贴板函数
const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
        .then(() => {
            message.success('复制成功')
        })
}

</script>
<style scoped lang="scss">
.main_all {
    width: 100%;
    height: 100%;
    padding: 20px;
    color: white;
    background-image: url('../assets/interviewRealTimeBack2.png');
    background-attachment: fixed;
    background-size: 100% 100%;
    background-repeat: no-repeat;

    display: flex;
    flex-direction: column;
}

.profile-container {
    background: rgba(0, 0, 0, 0.6);
    padding: 0px;
    border-radius: 12px;

    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
    height: 150px;
    position: relative;
    top: 30%;

    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
}
.quit{
margin: 30px auto 0;
height:100px;
width:200px;
position:relative;
background-color: blue;
}
.profile-left {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 150px;
}

.profile-right {
    height: 100%;
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-top: 5px;
    gap: 0;
    min-width: 280px;
}

.info-row {
    width: 100%;
    height: 45px;
    padding: 10px 5px;
    position: relative;
    background-color: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
    display: flex;

    label {
        width: 90px;
        height: 100%;
        user-select: none;
        font-weight: bold;
    }

    .info-text {
        width: 80%;
        height: 100%;
        overflow: hidden;
        user-select: none;
        white-space: nowrap; // 不换行
        text-overflow: ellipsis; // 超出显示 "..."
    }

    .bio-text {
        width: 80%;
        height: 100%;
        overflow: hidden;
        user-select: none;
        white-space: nowrap; // 不换行
        text-overflow: ellipsis; // 超出显示 "..."
    }

    .info-input {
        width: 80%;
        height: 100%;
        border-radius: 4px;
        white-space: nowrap; // 不换行
        text-overflow: ellipsis; // 超出显示 "..."
        background-color: transparent;
        border: 1px solid #1890ff;
        box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
        color: white;

        &:focus {
            border: 1px solid #1890ff;
        }
    }
}
</style>
