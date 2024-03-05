<template>
  <v-container class="faq">
    <ac-tab-nav :items="items" label="Category"/>
    <router-view/>
  </v-container>
</template>
<script setup lang="ts">
import {setMetaContent, updateTitle} from '@/lib/lib.ts'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import StripeCountryList from '@/types/StripeCountryList.ts'
import {useRoute, useRouter} from 'vue-router'
import {onMounted, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'


const route = useRoute()
const router = useRouter()

const items = [
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

watch(route, () => {
  /* istanbul ignore if */
  if (!route.params.question) {
    return
  }
  window._paq.push(['trackPageView'])
})

const stripeCountries = useSingle<StripeCountryList>('stripeCountries', {
  endpoint: '/api/sales/stripe-countries/',
  persist: true,
  x: {countries: []},
})
stripeCountries.get()

onMounted(() => {
  updateTitle('Frequently Asked Questions -- Artconomy')
  setMetaContent(
      'description',
      'Learn how Artconomy works, how to buy art safely online, and how to make money selling your art!',
  )
  if (route.name === 'FAQ') {
    router.replace({name: 'About'})
  }
})
</script>
