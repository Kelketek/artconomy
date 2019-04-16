<template>
  <v-layout row wrap>
    <v-flex xs12>
      <router-view></router-view>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {FormController} from '@/store/forms/form-controller'

  @Component
export default class Payment extends mixins(Subjective) {
    public ccForm: FormController = null as unknown as FormController
    public created() {
      if (this.$route.name === 'Payment') {
        this.$router.replace({name: 'Purchase', params: {username: this.username}})
      }
    }
}
</script>

<style scoped>

</style>
