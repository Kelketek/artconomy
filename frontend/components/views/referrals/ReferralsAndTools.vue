<template>
  <v-container fluid>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'LinksAndStats', params: {username}}">Referrals</v-tab>
      <v-tab :to="{name: 'Tools', params: {username}}">Tools</v-tab>
    </v-tabs>
    <router-view></router-view>
  </v-container>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'

  @Component
export default class ReferralsAndTools extends mixins(Subjective) {
  public created() {
    if (this.$route.name === 'ReferralsAndTools') {
      this.$router.replace({name: 'LinksAndStats', params: {username: this.username}})
    }
  }
}
</script>
