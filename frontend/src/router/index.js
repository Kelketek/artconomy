import Router from 'vue-router'
import Home from '@/components/Home'
import Profile from '@/components/Profile'
import Characters from '@/components/Characters'
import Character from '@/components/Character'
import Submission from '@/components/Submission'
import CharacterGallery from '@/components/CharacterGallery'

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/profile/:username/',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/profile/:username/characters/',
    name: 'Characters',
    component: Characters
  },
  {
    path: '/profile/:username/characters/:character/',
    name: 'Character',
    component: Character
  },
  {
    path: '/profile/:username/characters/:character/gallery/',
    name: 'CharacterGallery',
    component: CharacterGallery
  },
  {
    path: '/submissions/:assetID/',
    name: 'Submission',
    component: Submission
  }
]

export const router = new Router({
  mode: 'history',
  strict: true,
  routes
})
