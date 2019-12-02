<template>
  <v-container class="pa-0" fluid>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'Watching', params: {username}}">Watching</v-tab>
      <v-tab :to="{name: 'Watchers', params: {username}}">Watchers</v-tab>
    </v-tabs>
    <router-view :key="$route.fullPath" class="pt-2"/>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'

  @Component
export default class Watchlists extends mixins(Subjective) {
  public created() {
    this.$listenForList(`${this.username}__watching`)
    this.$listenForList(`${this.username}__watchers`)
    if (this.$route.name === 'Watchlists') {
      this.$router.push({name: 'Watching', params: {username: this.username}})
    }
  }
}
</script>
