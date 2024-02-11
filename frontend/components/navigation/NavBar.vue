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
                          :is-superuser="isSuperuser" :is-staff="isStaff" v-model="drawer"/>
          </v-col>
          <v-col cols="12">
            <v-divider />
          </v-col>
          <v-col cols="12" class="pt-3">
            <v-sheet>
              <v-row>
                <v-col class="bottom-button">
                  <a
                      href="https://twitter.com/ArtconomyArt/"
                      rel="nofollow noopener"
                      target="_blank"
                  >
                    <v-row no-gutters>
                      <v-col cols="12" class="text-center">
                        <ac-icon size="default" :icon="siTwitter"/>
                      </v-col>
                      <v-col cols="12" class="text-center">
                        <small>Twitter</small>
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
                        <v-icon medium icon="mdi-pencil"/>
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
                        <ac-icon size="default" :icon="siDiscord"/>
                      </v-col>
                      <v-col cols="12" class="text-center">
                        <small>Discord</small>
                      </v-col>
                    </v-row>
                  </a>
                </v-col>
                <v-col class="bottom-button" @click.capture.prevent="showSupport">
                  <v-row no-gutters>
                    <v-col cols="12" class="text-center support-button">
                      <v-icon medium icon="mdi-chat-question"/>
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
    <v-app-bar
        color="secondary"
        density="compact"
        fixed
        clipped-left
        app
        dark
        :scroll-off-screen="$vuetify.display.mdAndDown"
        :scroll-threshold="150"
        v-if="!store.state.iFrame"
    >
      <template v-slot:prepend>
        <v-app-bar-nav-icon v-if="viewer && fullInterface"
                            @click.stop="drawer = !drawer"
                            name="Main Menu"/>
      </template>
      <v-toolbar-title class="mr-5 align-center hidden-xs">
        <v-btn variant="text" to="/">
          <img :src="logo" class="header-logo" alt="A"/>
          <div class="title">rtconomy</div>
        </v-btn>
      </v-toolbar-title>
      <v-toolbar-title class="align-center hidden-sm-and-up" v-if="isLoggedIn">
        <v-btn variant="text" to="/" icon>
          <img :src="logo" class="header-logo" alt="Artconomy"/>
        </v-btn>
      </v-toolbar-title>
      <v-btn icon class="hidden-md-and-up" :to="{name: 'SearchProducts'}" aria-label="Search">
        <v-icon x-large icon="mdi-magnify"></v-icon>
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
            <v-icon x-large icon="mdi-magnify"></v-icon>
          </v-btn>
        </template>
      </ac-bound-field>
      <v-card class="px-2 py-1 hidden-xs-only"
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
      <v-toolbar-items v-if="fullInterface">
        <v-btn variant="plain" v-if="isRegistered" @click="notificationLoad" class="notifications-button">
          <template #default>
            <v-badge overlap right color="red" :model-value="!!counts.count">
              <template v-slot:badge>
                <span v-if="counts.count && counts.count < 1000">{{counts.count}}</span>
                <span v-else>*</span>
              </template>
              <v-icon size="x-large" icon="mdi-bell"/>
            </v-badge>
          </template>
        </v-btn>
        <v-btn class="nav-login-item" variant="text" v-if="isRegistered"
               :to="profileRoute">
          <v-avatar size="32px">
            <img :src="registeredUser.avatar_url" :alt="registeredUser.username">
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
import {initDrawerValue, makeQueryParams, BASE_URL} from '@/lib/lib.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {User} from '@/store/profiles/types/User.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useNav} from '@/mixins/nav.ts'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'
import {siDiscord, siTwitter} from 'simple-icons'
import {NavSettings} from '@/types/NavSettings.ts'
import AcIcon from '@/components/AcIcon.vue'
import {computed, onUnmounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'
import {useSearchForm} from '@/components/views/search/hooks.ts'

// Should already have been populated in the root component.
const searchForm = useSearchForm()
const logo = new URL('/static/images/logo.png', BASE_URL).href
const route = useRoute()
const router = useRouter()
const store = useStore<ArtState>()

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

const runSearch = () => {
  if (route.name && (String(route.name).indexOf('Search') !== -1)) {
    return
  }
  console.log('query params are', makeQueryParams(searchForm.rawData))
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
  isStaff,
  isSuperuser,
} = useViewer()

const registeredUser = viewer.value as User

const notificationLoad = () => {
  if (['CommunityNotifications', 'SalesNotifications'].indexOf(String(route.name) + '') !== -1) {
    router.replace({
      name: 'Reload',
      params: {path: route.path},
    })
  } else {
    router.push({name: 'CommunityNotifications'})
  }
}

const showSupport = () => store.commit('supportDialog', true)

watch(isRegistered, (val: boolean) => {
  if (val) {
    store.dispatch('notifications/startLoop').then()
  } else {
    store.dispatch('notifications/stopLoop').then()
  }
}, {immediate: true})

const profileRoute = computed(() => {
  return {
    name: 'AboutUser',
    params: {username: viewer.value.username},
  }
})

const sfwMode = computed(() => viewerHandler.user.patchers.sfw_mode)

const counts = computed(() => store.state.notifications!.stats)

onUnmounted(() => store.dispatch('notifications/stopLoop').then())

// @Component({
//   components: {
//     AcNavLinks,
//     AcBoundField,
//     AcPatchField,
//     AcSettingNav,
//     AcIcon,
//     AcLink,
//   },
// })
// class NavBar extends mixins(Viewer, Nav) {
//   public searchForm: FormController = null as unknown as FormController
//   public drawer = false
//
//   public siDiscord = siDiscord
//   public siTwitter = siTwitter
//   public logo = new URL('/static/images/logo.png', BASE_URL).href
//
//   public get loginLink() {
//     if (this.$route.name === 'Login') {
//       return {
//         name: 'Login',
//       }
//     }
//     return {
//       name: 'Login',
//       query: {next: this.$route.path},
//     }
//   }
//
//   public runSearch() {
//     if (this.$route.name && (String(this.$route.name).indexOf('Search') !== -1)) {
//       return
//     }
//     this.$router.push({
//       name: 'SearchProducts',
//       query: makeQueryParams(this.searchForm.rawData),
//     })
//   }
//
//   public get registeredUser() {
//     return this.viewer as User
//   }
//
//   public created() {
//     this.searchForm = this.$getForm('search')
//   }
//
//   public notificationLoad() {
//     if (['CommunityNotifications', 'SalesNotifications'].indexOf(String(this.$route.name) + '') !== -1) {
//       this.$router.replace({
//         name: 'Reload',
//         params: {path: this.$route.path},
//       })
//     } else {
//       this.$router.push({name: 'CommunityNotifications'})
//     }
//   }
//
//   public showSupport() {
//     this.$store.commit('supportDialog', true)
//   }
//
//   @Watch('isRegistered', {immediate: true})
//   public viewerUpdate(val: boolean) {
//     if (val) {
//       this.$store.dispatch('notifications/startLoop').then()
//     } else {
//       this.$store.dispatch('notifications/stopLoop').then()
//     }
//   }
//
//   public get profileRoute() {
//     const viewer = this.viewer as User
//     return {
//       name: 'AboutUser',
//       params: {username: viewer.username},
//     }
//   }
//
//   public get sfwMode() {
//     return this.viewerHandler.user.patchers.sfw_mode
//   }
//
//   public get counts() {
//     return this.$store.state.notifications!.stats
//   }
//
//   public unmounted() {
//     this.$store.dispatch('notifications/stopLoop').then()
//   }
// }
//
// export default toNative(NavBar)
</script>
