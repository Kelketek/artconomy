<template>
  <div :id="id"></div>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'

@Component
class SubjectiveComponent extends mixins(Subjective) {
  public get id() {
    if (this.$route) {
      return (String(this.$route.name) + '-component').toLowerCase()
    } else {
      return 'subjective-component'
    }
  }
}
export default toNative(SubjectiveComponent)
</script>

<style scoped>

</style>
