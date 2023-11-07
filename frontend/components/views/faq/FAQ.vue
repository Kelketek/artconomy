<template>
  <v-container class="faq">
    <ac-tab-nav :items="items" label="Category"/>
    <router-view/>
  </v-container>
</template>
<script lang="ts">
import {setMetaContent, updateTitle} from '@/lib/lib'
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import StripeCountryList from '@/types/StripeCountryList'

@Component({
  components: {AcTabNav},
})
class FAQ extends mixins(Viewer) {
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public stripeCountries: SingleController<StripeCountryList> = null as unknown as SingleController<StripeCountryList>

  public get items() {
    return [
      {
        value: {name: 'About'},
        title: 'About',
      },
      {
        value: {name: 'BuyAndSell'},
        title: 'Buying/Selling',
      },
      {
        value: {name: 'Other'},
        title: 'Other/Misc',
      },
    ]
  }

  @Watch('$route')
  public updateTracker() {
    /* istanbul ignore if */
    if (!this.$route.params.question) {
      return
    }
    window._paq.push(['trackPageView'])
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.stripeCountries = this.$getSingle('stripeCountries', {
      endpoint: '/api/sales/stripe-countries/',
      persist: true,
      x: {countries: []},
    })
    this.stripeCountries.get()
    updateTitle('Frequently Asked Questions -- Artconomy')
    setMetaContent(
        'description',
        'Learn how Artconomy works, how to buy art safely online, and how to make money selling your art!',
    )
    if (this.$route.name === 'FAQ') {
      this.$router.replace({name: 'About'})
    }
  }
}

export default toNative(FAQ)
</script>
