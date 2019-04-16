<template>
  <div :id="id"></div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'

  @Component
export default class SubjectiveComponent extends mixins(Subjective) {
  public get id() {
    if (this.$route) {
      return (this.$route.name + '-component').toLowerCase()
    } else {
      return 'subjective-component'
    }
  }
}
</script>

<style scoped>

</style>
