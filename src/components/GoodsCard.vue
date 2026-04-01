<!-- 子组件：GoodsCard.vue -->
<template>
  <div class="goods-card">
    <h3>{{ goods.name }}</h3>
    <p>¥{{ goods.price }}</p>
  </div>
</template>

<script setup>
const props = defineProps({ goods: Object })
</script>

<style scoped>
.goods-card {
  /* 设置固定宽度，避免组件自适应挤压 */
  width: 200px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
}
</style>