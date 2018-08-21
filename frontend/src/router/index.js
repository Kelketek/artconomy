import Router from 'vue-router'
import Home from '@/components/Home'
import Reload from '@/components/Reload'
import Login from '@/components/Login'
import CommissionAgreement from '@/components/CommissionAgreement'
import CharacterTransferAgreement from '@/components/CharacterTransferAgreement'
import RefundPolicy from '@/components/RefundPolicy'
import TermsOfService from '@/components/TermsOfService'
import PrivacyPolicy from '@/components/PrivacyPolicy'
import NotificationCenter from '@/components/NotificationCenter'
import Profile from '@/components/Profile'
import Policies from '@/components/Policies'
import Contact from '@/components/Contact'
import Store from '@/components/Store'
import Ratings from '@/components/Ratings'
import Journal from '@/components/Journal'
import WhoIsOpen from '@/components/WhoIsOpen'
import Transfers from '@/components/Transfers'
import Product from '@/components/Product'
import Order from '@/components/Order'
import Orders from '@/components/Orders'
import Upgrade from '@/components/Upgrade'
import FAQ from '@/components/FAQ'
import Settings from '@/components/Settings'
import RecentArt from '@/components/RecentArt'
import Character from '@/components/Character'
import Submission from '@/components/Submission'
import Search from '@/components/Search'
import CharacterGallery from '@/components/CharacterGallery'
import CharacterTransfer from '@/components/CharacterTransfer'
import NotFound from '@/components/NotFound'
import SessionSettings from '@/components/SessionSettings.vue'
import Messages from '@/components/Messages.vue'
import Message from '@/components/Message.vue'
import PasswordReset from '@/components/PasswordReset.vue'
import {ErrorHandler} from '@/plugins/error'
import {setMetaContent} from '../lib'

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: true
  },
  { path: '/Reload/:path',
    name: 'Reload',
    component: Reload
  },
  {
    path: '/auth/:tabName?/',
    name: 'Login',
    component: Login
  },
  {
    path: '/set-password/:username/:resetToken/',
    props: true,
    component: PasswordReset
  },
  {
    path: '/legal-and-policies/',
    name: 'Policies',
    component: Policies
  },
  {
    path: '/recent-art/:tabName?/',
    name: 'RecentArt',
    props: true,
    component: RecentArt
  },
  {
    path: '/legal-and-policies/character-transfer-agreement/',
    name: 'CharacterTransferAgreement',
    component: CharacterTransferAgreement
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
    path: '/legal-and-policies/terms-of-service/',
    name: 'TermsOfService',
    component: TermsOfService
  },
  {
    path: '/legal-and-policies/privacy-policy/',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy
  },
  {
    path: '/contact/',
    name: 'Contact',
    component: Contact
  },
  {
    path: '/notifications/:tabName?/',
    name: 'Notifications',
    component: NotificationCenter,
    props: true
  },
  {
    path: '/store/:username/',
    name: 'Store',
    component: Store,
    props (route) {
      return {
        username: route.params.username,
        endpoint: `/api/sales/v1/account/${route.params.username}/products/`
      }
    }
  },
  {
    path: '/upgrade/',
    name: 'Upgrade',
    component: Upgrade,
    props: true
  },
  {
    path: '/faq/:tabName?/:subTabName?/',
    name: 'FAQ',
    component: FAQ,
    props: true
  },
  {
    path: '/who-is-open/:tabName?/',
    name: 'WhoIsOpen',
    props: true,
    component: WhoIsOpen
  },
  {
    path: '/profile/:username/settings/:tabName?/:subTabName?/:tertiaryTabName?/',
    name: 'Settings',
    component: Settings,
    props: true
  },
  {
    path: '/profile/:username/ratings/',
    name: 'Ratings',
    component: Ratings,
    props: true
  },
  {
    path: '/profile/:username/journals/:journalID/',
    name: 'Journal',
    component: Journal,
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
    path: '/profile/:username/:tabName?/:subTabName?/',
    name: 'Profile',
    component: Profile,
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
    path: '/cases/:username/case/:orderID/',
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
        url: `/api/sales/v1/account/${route.params.username}/orders/`,
        buyer: true
      }
    }
  },
  {
    path: '/sales/:username/:tabName?/:subTabName?/',
    name: 'Sales',
    component: Orders,
    props (route) {
      return {
        username: route.params.username,
        url: `/api/sales/v1/account/${route.params.username}/sales/`,
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
        url: `/api/sales/v1/account/${route.params.username}/cases/`,
        buyer: true
      }
    }
  },
  {
    path: '/transfers/:username/:tabName?/',
    name: 'Transfers',
    component: Transfers,
    props: true
  },
  {
    path: '/transfers/:username/characters/:transferID/',
    name: 'CharacterTransfer',
    component: CharacterTransfer,
    props: true
  },
  {
    path: '/search/:tabName?/',
    name: 'Search',
    component: Search,
    props: true
  },
  {
    path: '/session/settings/',
    name: 'SessionSettings',
    component: SessionSettings
  },
  {
    path: '/messages/:username/:tabName?/',
    name: 'Messages',
    component: Messages,
    props: true
  },
  {
    path: '/messages/:username/message/:messageID/',
    name: 'Message',
    component: Message,
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

router.beforeEach((to, from, next) => {
  if (from.name !== to.name) {
    document.title = 'Artconomy-- Where artists and commissioners meet!'
    setMetaContent('description', 'Artconomy lets you find artists to draw your personal characters.')
  }
  next()
})
