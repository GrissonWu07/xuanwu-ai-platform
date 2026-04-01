<template>
  <div class="shell">
    <slot />
  </div>
</template>

<style scoped>
.shell {
  width: min(1440px, calc(100vw - 2rem));
  margin: 0 auto;
}
</style>
