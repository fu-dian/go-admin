<!-- 父组件：Home.vue（二手交易平台首页） -->
<template>
 
</template>

<script setup>

</script>

<style scoped>
/* 父容器核心样式 */
.component-container {
  /* 核心：开启Flex布局，子元素自动同行 */
  display: flex;
  /* 可选：子元素之间的间距 */
  gap: 20px;
  /* 可选：换行（防止组件挤在一起） */
  flex-wrap: wrap;
  /* 可选：垂直居中 */
  align-items: center;
  /* 可选：水平居中 */
  justify-content: center;
  /* 可选：容器内边距 */
  padding: 20px;
}
</style>