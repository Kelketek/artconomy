<template>
  <div></div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'

@Component
class NotFound extends ArtVue {

  public mounted() {
    this.$store.commit('errors/setError', {response: {status: 404}})
  }
}

export default toNative(NotFound)
</script>

<style scoped>

</style>
