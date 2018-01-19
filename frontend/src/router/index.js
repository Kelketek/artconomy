import Router from 'vue-router'
import Home from '@/components/Home'
import CommissionAgreement from '@/components/CommissionAgreement'
import RefundPolicy from '@/components/RefundPolicy'
import NotificationCenter from '@/components/NotificationCenter'
import Profile from '@/components/Profile'
import Policies from '@/components/Policies'
import Contact from '@/components/Contact'
import Store from '@/components/Store'
import Product from '@/components/Product'
import Order from '@/components/Order'
import Orders from '@/components/Orders'
import Settings from '@/components/Settings'
import Characters from '@/components/Characters'
import Character from '@/components/Character'
import Submission from '@/components/Submission'
import Search from '@/components/Search'
import CharacterGallery from '@/components/CharacterGallery'
import NotFound from '@/components/NotFound'
import {ErrorHandler} from '@/plugins/error'

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: true
  },
  {
    path: '/legal-and-policies/',
    name: 'Policies',
    component: Policies
  },
  {
    path: '/legal-and-policies/commission-agreement/',
    name: 'CommissionAgreement',
    component: CommissionAgreement
  },
  {
    path: '/legal-and-policies/refund-policy/',
    name: 'RefundPolicy',
    component: RefundPolicy
  },
  {
    path: '/contact/',
    name: 'Contact',
    component: Contact
  },
  {
    path: '/notifications/',
    name: 'Notifications',
    component: NotificationCenter,
    props: true
  },
  {
    path: '/profile/:username/',
    name: 'Profile',
    component: Profile,
    props: true
  },
  {
    path: '/store/:username/',
    name: 'Store',
    component: Store,
    props (route) {
      return {
        username: route.params.username,
        url: `/api/sales/v1/${route.params.username}/products/`
      }
    }
  },
  {
    path: '/profile/:username/settings/:tabName?/:subTabName?/',
    name: 'Settings',
    component: Settings,
    props: true
  },
  {
    path: '/profile/:username/characters/',
    name: 'Characters',
    component: Characters,
    props: true
  },
  {
    path: '/profile/:username/characters/:characterName/',
    name: 'Character',
    component: Character,
    props: true
  },
  {
    path: '/profile/:username/characters/:characterName/gallery/',
    name: 'CharacterGallery',
    component: CharacterGallery,
    props: true
  },
  {
    path: '/submissions/:assetID/',
    name: 'Submission',
    component: Submission,
    props: true
  },
  {
    path: '/store/:username/product/:productID/',
    name: 'Product',
    component: Product,
    props: true
  },
  {
    path: '/orders/:username/order/:orderID/',
    name: 'Order',
    component: Order,
    props: true
  },
  {
    path: '/sales/:username/sale/:orderID/',
    name: 'Sale',
    component: Order,
    props: true
  },
  {
    path: '/cases/:username/sale/:orderID/',
    name: 'Case',
    component: Order,
    props: true
  },
  {
    path: '/orders/:username/:tabName?/',
    name: 'Orders',
    component: Orders,
    props (route) {
      return {
        username: route.params.username,
        url: `/api/sales/v1/${route.params.username}/orders/`,
        buyer: true
      }
    }
  },
  {
    path: '/sales/:username/:tabName?/',
    name: 'Sales',
    component: Orders,
    props (route) {
      return {
        username: route.params.username,
        url: `/api/sales/v1/${route.params.username}/sales/`,
        buyer: false
      }
    }
  },
  {
    path: '/cases/:username/:tabName?/',
    name: 'Cases',
    component: Orders,
    props (route) {
      return {
        username: route.params.username,
        url: `/api/sales/v1/${route.params.username}/cases/`,
        buyer: true
      }
    }
  },
  {
    path: '/search/:tabName?/',
    name: 'Search',
    component: Search,
    props: true
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound
  }
]

export const router = new Router({
  mode: 'history',
  strict: true,
  routes
})

router.beforeEach(ErrorHandler.clearError)
