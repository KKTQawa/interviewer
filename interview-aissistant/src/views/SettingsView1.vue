<template> 
<div class="note">{{ sendtime }}后开始</div>
</template>
<script setup>
import{computed, ref}from'vue'
import {NButton}from'naive-ui'
const x=ref(5);
const sendtime=computed(()=>{
  return x.value+5;
})
setInterval(()=>{
  x.value--;
},1000)
</script>
<style scoped lang="scss">
.note{
  color:white;
}

</style>