import Router from 'vue-router'
import Home from '@/components/Home'
import CommissionAgreement from '@/components/CommissionAgreement'
import NotificationCenter from '@/components/NotificationCenter'
import Profile from '@/components/Profile'
import Store from '@/components/Store'
import Product from '@/components/Product'
import Order from '@/components/Order'
import Orders from '@/components/Orders'
import Settings from '@/components/Settings'
import Characters from '@/components/Characters'
import Character from '@/components/Character'
import Submission from '@/components/Submission'
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
    path: '/legal/commission-agreement/',
    name: 'CommissionAgreement',
    component: CommissionAgreement
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
