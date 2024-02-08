import Empty from '@/specs/helpers/dummy_components/empty.ts'
import FAQ from '@/components/views/faq/FAQ.vue'
import BuyAndSell from '@/components/views/faq/BuyAndSell.vue'
import About from '@/components/views/faq/About.vue'
import Other from '@/components/views/faq/Other.vue'
import {createWebHistory} from 'vue-router'

export const faqRoutes = () => ({
  history: createWebHistory(),
  routes: [{
    path: '/',
    name: 'Home',
    component: Empty,
  }, {
    path: '/faq/',
    name: 'FAQ',
    component: FAQ,
    children: [
      {
        path: 'buying-and-selling/:question?',
        component: BuyAndSell,
        name: 'BuyAndSell',
        props: true,
      },
      {
        path: 'about/:question?',
        component: About,
        name: 'About',
        props: true,
      },
      {
        path: 'other/:question?',
        component: Other,
        name: 'Other',
        props: true,
      },
    ],
  }, {
    path: '/search/products/',
    name: 'SearchProducts',
    component: Empty,
  }],
})
