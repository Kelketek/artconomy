<template>
  <div></div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Mutation} from 'vuex-class'

  @Component
export default class App extends Vue {
    @Mutation('setError', {namespace: 'errors'}) public setError: any

    public mounted() {
      this.setError({response: {status: 404}})
    }
}
</script>

<style scoped>

</style>
