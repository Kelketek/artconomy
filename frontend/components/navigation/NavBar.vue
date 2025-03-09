<!--suppress HtmlUnknownTarget -->
<template>
  <div class="main-navigation">
    <v-navigation-drawer
        fixed
        v-model="drawer"
        app
        temporary
        width="300"
        v-if="viewer && !store.state.iFrame && fullInterface"
    >
      <v-container fluid class="pa-0 fill-height">
        <v-row no-gutters>
          <v-col cols="12">
            <ac-nav-links :subject-handler="viewerHandler" :is-logged-in="isLoggedIn" :is-registered="isRegistered"
                          :is-superuser="isSuperuser" v-model="drawer"/>
          </v-col>
          <v-col cols="12">
            <v-divider />
          </v-col>
          <v-col cols="12" class="pt-3">
            <v-sheet>
              <v-row>
                <v-col class="bottom-button">
                  <a
                      href="https://bsky.app/profile/artconomy.bsky.social"
                      rel="nofollow noopener"
                      target="_blank"
                  >
                    <v-row no-gutters>
                      <v-col cols="12" class="text-center">
                        <v-icon size="default" :icon="siBluesky.path"/>
                      </v-col>
                      <v-col cols="12" class="text-center">
                        <small>Bluesky</small>
                      </v-col>
                    </v-row>
                  </a>
                </v-col>
                <v-col class="bottom-button">
                  <a
                      href="https://artconomy.com/blog/"
                      rel="nofollow noopener"
                      target="_blank"
                  >
                    <v-row no-gutters class="px-2">
                      <v-col cols="12" class="text-center">
                        <v-icon medium :icon="mdiPencil"/>
                      </v-col>
                      <v-col cols="12" class="text-center pt-1">
                        <small>Blog</small>
                      </v-col>
                    </v-row>
                  </a>
                </v-col>
                <v-col class="bottom-button">
                  <a
                      href="https://discord.gg/4nWK9mf"
                      rel="nofollow noopener"
                      target="_blank"
                  >
                    <v-row no-gutters>
                      <v-col cols="12" class="text-center">
                        <v-icon size="default" :icon="siDiscord.path"/>
                      </v-col>
                      <v-col cols="12" class="text-center">
                        <small>Discord</small>
                      </v-col>
                    </v-row>
                  </a>
                </v-col>
                <v-col class="bottom-button" @click.capture.prevent="showSupport" tabindex="0">
                  <v-row no-gutters>
                    <v-col cols="12" class="text-center support-button">
                      <v-icon medium :icon="mdiChatQuestion"/>
                    </v-col>
                    <v-col cols="12" class="text-center pt-1">
                      <small>Support</small>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-navigation-drawer>
    <message-center v-if="isRegistered" :username="rawViewerName" v-model="messagesOpen" />
    <v-app-bar
        color="secondary"
        density="compact"
        fixed
        clipped-left
        app
        dark
        :scroll-off-screen="mdAndDown"
        :scroll-threshold="150"
        v-if="!store.state.iFrame"
    >
      <template v-slot:prepend>
        <v-app-bar-nav-icon v-if="viewer && fullInterface"
                            @click.stop="drawer = !drawer"
                            tabindex="0"
                            aria-label="Open Menu"
                            name="Main Menu"/>
      </template>
      <v-toolbar-title class="mr-5 align-center hidden-xs">
        <v-btn variant="text" to="/">
          <img :src="logo" class="header-logo" alt="A" height="28" width="28"/>
          <div class="title">rtconomy</div>
        </v-btn>
      </v-toolbar-title>
      <v-toolbar-title class="align-center hidden-sm-and-up" v-if="isLoggedIn">
        <v-btn variant="text" to="/" icon>
          <img :src="logo" class="header-logo" alt="A"/>
        </v-btn>
      </v-toolbar-title>
      <v-btn icon class="hidden-md-and-up" :to="{name: 'SearchProducts'}" aria-label="Search">
        <v-icon x-large :icon="mdiMagnify"></v-icon>
      </v-btn>
      <ac-bound-field
          :field="searchForm.fields.q"
          placeholder="Search..."
          single-line
          @keyup="runSearch"
          @click:append="runSearch"
          color="white"
          hide-details
          class="hidden-sm-and-down"
          field-id="nav-bar-search"
          aria-label="Search field"
      >
        <template v-slot:prepend>
          <v-btn icon variant="plain" :to="{name: 'SearchProducts'}" aria-label="Search" class="search-button-offset">
            <v-icon x-large :icon="mdiMagnify"></v-icon>
          </v-btn>
        </template>
      </ac-bound-field>
      <v-card class="px-2 py-1 hidden-xs"
              :color="sfwMode.model? 'blue darken-3' : 'black'"
              v-if="viewer && viewer.rating > 0 && fullInterface"
      >
        <v-switch
            v-model="sfwMode.model"
            @click="sfwMode.model = !sfwMode.model"
            label="SFW"
            :hide-details="true"
        >
        </v-switch>
      </v-card>
      <ac-stats-bar :username="rawViewerName" v-if="viewer && viewer.artist_mode && fullInterface" />
      <v-toolbar-items v-if="fullInterface">
        <ac-notification-indicator :username="rawViewerName" v-if="isRegistered" @click="messagesOpen = !messagesOpen" :key="rawViewerName" />
        <v-btn class="nav-login-item" variant="text" v-if="isRegistered"
               :to="profileRoute">
          <v-avatar size="32px">
            <img :src="registeredUser.avatar_url" aria-hidden="true" width="32" height="32" alt="">
          </v-avatar>
          <div style="padding-left: 1rem;" v-if="isLoggedIn" class="hidden-sm-and-down">{{ viewer!.username }}</div>
        </v-btn>
        <v-btn v-else-if="viewer" class="nav-login-item" variant="text" :to="loginLink">Login</v-btn>
        <v-btn v-else class="nav-login-item" aria-label="Login button loading."/>
      </v-toolbar-items>
    </v-app-bar>
  </div>
</template>

<style>
.header-logo {
  height: 1.75rem;
  vertical-align: middle;
}

.title {
  display: inline-block;
  vertical-align: middle;
}

.phone-padding {
  padding-bottom: 80px !important;
}
.search-button-offset {
  right: -1rem;
}

.bottom-button {
  opacity: .7;
}

.bottom-button:hover {
  opacity: 1
}

#app .bottom-button a {
  text-decoration: none;
  font-weight: normal;
}

</style>

<script setup lang="ts">
import {makeQueryParams, BASE_URL} from '@/lib/lib.ts'
import {useViewer} from '@/mixins/viewer.ts'
const AcBoundField = defineAsyncComponent(() => import('@/components/fields/AcBoundField.ts'))
import {useNav} from '@/mixins/nav.ts'
const AcNavLinks = defineAsyncComponent(() => import('@/components/navigation/AcNavLinks.vue'))
import {siDiscord, siBluesky} from 'simple-icons'
import {computed, defineAsyncComponent, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'
import {useSearchForm} from '@/components/views/search/hooks.ts'
import {useDisplay} from 'vuetify'
import {mdiChatQuestion, mdiMagnify, mdiPencil} from '@mdi/js'
import {User} from '@/store/profiles/types/main'
const AcNotificationIndicator = defineAsyncComponent(() => import('@/components/navigation/AcNotificationIndicator.vue'))
const AcStatsBar = defineAsyncComponent(() => import('@/components/navigation/AcStatsBar.vue'))
const MessageCenter = defineAsyncComponent(() => import('@/components/navigation/MessageCenter.vue'))

// Should already have been populated in the root component.
const searchForm = useSearchForm()
const logo = new URL('/static/images/mini-logo.png', BASE_URL).href
const route = useRoute()
const router = useRouter()
const store = useStore<ArtState>()
const {mdAndDown} = useDisplay()

const drawer = ref(false)

const loginLink = computed(() => {
  if (route.name === 'Login') {
    return {
      name: 'Login',
    }
  }
  return {
    name: 'Login',
    query: {next: route.path},
  }
})

const runSearch = (event: KeyboardEvent) => {
  if (event.key === 'Tab') {
    return
  }
  if (route.name && (String(route.name).indexOf('Search') !== -1)) {
    return
  }
  router.push({
    name: 'SearchProducts',
    query: makeQueryParams(searchForm.rawData),
  })
}

const {fullInterface} = useNav()

const {
  viewer,
  isRegistered,
  viewerHandler,
  isLoggedIn,
  isSuperuser,
  rawViewerName,
} = useViewer()

const registeredUser = computed(() => viewer.value as User)

const showSupport = () => store.commit('supportDialog', true)

const profileRoute = computed(() => {
  return {
    name: 'AboutUser',
    params: {username: viewer.value.username},
  }
})

const sfwMode = computed(() => viewerHandler.user.patchers.sfw_mode)

const messagesOpen = computed<boolean>({
  get: () => store.state.messagesOpen,
  set: (val: boolean) => store.commit('setMessagesOpen', val)
})
</script>
