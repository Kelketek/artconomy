<template>
  <v-container class="faq">
    <v-row>
      <v-col cols="12" class="text-center">
        <h1>Frequently Asked Questions</h1>
      </v-col>
    </v-row>
    <ac-tab-nav :items="items" label="Category" :heading-level="2"/>
    <router-view/>
  </v-container>
</template>
<script setup lang="ts">
import {setMetaContent, updateTitle} from '@/lib/lib.ts'
import {useRoute, useRouter} from 'vue-router'
import {defineAsyncComponent, onMounted, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import type {StripeCountryList} from '@/types/main'
const AcTabNav = defineAsyncComponent(() => import('@/components/navigation/AcTabNav.vue'))


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
