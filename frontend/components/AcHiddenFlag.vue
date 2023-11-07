<template>
  <div class="hidden-marker-container" v-if="value">
    <v-icon class="ml-2 mt-2 elevation-20 background-black" icon="mdi-eye-off"/>
  </div>
</template>

<style scoped>
.hidden-marker-container {
  position: absolute;
  height: 100%;
  width: 100%;
  z-index: 1;
}

.background-black {
  background-color: #000;
  border-radius: 20px;
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'

@Component
class AcHiddenFlag extends Vue {
  @Prop({required: true})
  public value!: boolean
}

export default toNative(AcHiddenFlag)
</script>
