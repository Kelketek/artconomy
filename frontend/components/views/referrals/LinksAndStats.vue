<template>
  <v-container>
    <v-layout row wrap text-xs-center>
      <v-flex xs12>
        <h1>Refer a Friend and get Rewarded!</h1>
        <p>
          Every time someone registers and buys or sells a
          <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
            Shield protected
          </router-link>
          product for the first time, you'll get a <strong>FREE</strong> month of
          <router-link
              :to="{name: 'BuyAndSell', params: {question: 'portrait-and-landscape'}}">
            Artconomy Portrait or Landscape.
          </router-link>
        </p>
      </v-flex>
    </v-layout>
    <v-card>
      <v-card-text>
        <v-layout row wrap>
          <v-flex text-xs-center>
            <h2>Use this link to refer other commissioners and artists:</h2>
            <p><a :href="`https://artconomy.com/?referred_by=${username}`"><code
                v-html="`https://artconomy.com/?referred_by=${username}`"></code></a></p>
            <p>
              You may also make any link to an Artconomy page a referral link by adding <code>{{
              `?referred_by=${username}` }}</code> to the end of it.
            </p>
            <h3>Extra Rewards!</h3>
            <p>Follow our <a href="https://twitter.com/ArtconomyArt">Twitter Feed</a> for information on contests
              for things like <strong>FREE</strong> commissions!</p>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
    <ac-load-section :controller="stats">
      <template v-slot:default>
        <v-layout row wrap>
          <v-flex xs12 text-xs-center>
            <h2>Your Referral Stats</h2>
            <ul>
              <li>Total People Referred: {{stats.x.total_referred}}</li>
              <li>Portrait Eligible Referrals: {{stats.x.portrait_eligible}}</li>
              <li>Landscape Eligible Referrals: {{stats.x.landscape_eligible}}</li>
            </ul>
            <p class="mt-2">For a referral to be
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'portrait-and-landscape'}}">
                Portrait
              </router-link>
              Eligible, the referred person must commission a
              <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                Shield protected
              </router-link>
              product.
            </p>
            <p>For a referral to be
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'portrait-and-landscape'}}">
                Landscape
              </router-link>
              Eligible, the referred person must sell a
              <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                Shield protected
              </router-link>
              product.
            </p>
            <p>Your total reflects all referred users, even those who have done no
              <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                Shield protected
              </router-link>
              transactions.
            </p>
          </v-flex>
        </v-layout>
      </template>
    </ac-load-section>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller'
import ReferralStats from '@/types/ReferralStats'
  @Component({
    components: {AcLoadSection},
  })
export default class Referrals extends mixins(Subjective) {
    public stats: SingleController<ReferralStats> = null as unknown as SingleController<ReferralStats>
    public privateView = true
    public created() {
      this.stats = this.$getSingle(
        `ReferralStats__${this.username}`, {endpoint: `/api/profiles/v1/account/${this.username}/referral_stats/`}
      )
      this.stats.get()
    }
}
</script>
