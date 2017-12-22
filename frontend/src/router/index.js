import Router from 'vue-router'
import Home from '@/components/Home'
import NotificationCenter from '@/components/NotificationCenter'
import Profile from '@/components/Profile'
import Store from '@/components/Store'
import Settings from '@/components/Settings'
import Characters from '@/components/Characters'
import Character from '@/components/Character'
import Submission from '@/components/Submission'
import CharacterGallery from '@/components/CharacterGallery'

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: true
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
    props: true
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
    path: '/profile/:username/characters/:character/',
    name: 'Character',
    component: Character,
    props: true
  },
  {
    path: '/profile/:username/characters/:character/gallery/',
    name: 'CharacterGallery',
    component: CharacterGallery,
    props: true
  },
  {
    path: '/submissions/:assetID/',
    name: 'Submission',
    component: Submission,
    props: true
  }
]

export const router = new Router({
  mode: 'history',
  strict: true,
  routes
})
