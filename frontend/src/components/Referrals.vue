<template>
  <v-container>
    <v-layout row wrap text-xs-center>
      <v-flex xs12>
        <h1>Refer a Friend and get Rewarded!</h1>
        <p>
          Every time someone registers and buys or sells a <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
          Shield protected</router-link>
          product for the first time, you'll get a <strong>FREE</strong> month of
          <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'portrait-and-landscape'}}">
            Artconomy Portrait or Landscape.</router-link>

        </p>
      </v-flex>
    </v-layout>
    <v-card>
      <v-card-text>
        <v-layout row wrap>
          <v-flex text-xs-center>
            <h2>Use this link to refer other commissioners and artists:</h2>
            <p><a :href="`https://artconomy.com/?referred_by=${username}`"><code v-html="`https://artconomy.com/?referred_by=${username}`"></code></a></p>
            <p>
              You may also make any link to an Artconomy page a referral link by adding <code>{{ `?referred_by=${username}` }}</code> to the end of it.
            </p>
            <h3>Extra Rewards!</h3>
            <p>Follow our <a href="https://twitter.com/ArtconomyArt">Twitter Feed</a> for information on contests for things like <strong>FREE</strong> commissions!</p>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
    <v-layout row wrap>
      <v-flex xs12 v-if="stats" text-xs-center>
        <h2>Your Referral Stats</h2>
        <ul>
          <li>Total People Referred: {{stats.total_referred}}</li>
          <li>Portrait Eligible Referrals: {{stats.portrait_eligible}}</li>
          <li>Landscape Eligible Referrals: {{stats.landscape_eligible}}</li>
        </ul>
        <p class="mt-2">For a referral to be <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'portrait-and-landscape'}}">Portrait</router-link> Eligible, the referred person must commission a <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
          Shield protected</router-link> product.</p>
        <p>For a referral to be <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'portrait-and-landscape'}}">Landscape</router-link> Eligible, the referred person must sell a <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
          Shield protected</router-link> product.</p>
        <p>Your total reflects all referred users, even those who have done no <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
          Shield protected</router-link> transactions.</p>
      </v-flex>
      <v-flex v-else>Loading...</v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import {artCall} from '../lib'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'

  export default {
    name: 'Referrals',
    mixins: [Viewer, Perms],
    data () {
      return {stats: null}
    },
    methods: {
      setStats (data) {
        this.stats = data
      }
    },
    created () {
      artCall(`/api/profiles/v1/account/${this.username}/referral_stats/`, 'GET', undefined, this.setStats, this.$error)
    }
  }
</script>

<style scoped>

</style>