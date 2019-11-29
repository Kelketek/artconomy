<template>
  <v-container class="faq">
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'About'}">
        About
      </v-tab>
      <v-tab :to="{name: 'BuyAndSell'}">
        Buying/Selling
      </v-tab>
      <v-tab :to="{name: 'Other'}">
        Other/Misc
      </v-tab>
    </v-tabs>
    <router-view></router-view>
  </v-container>
</template>
<script lang="ts">
import {setMetaContent, updateTitle} from '@/lib'
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'

@Component
export default class FAQ extends mixins(Viewer) {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>

    public created() {
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
      updateTitle(`Frequently Asked Questions -- Artconomy`)
      setMetaContent(
        'description',
        'Learn how Artconomy works, how to buy art safely online, and how to make money selling your art!'
      )
      if (this.$route.name === 'FAQ') {
        this.$router.replace({name: 'About'})
      }
    }
}
</script>
