<!--suppress JSUnusedGlobalSymbols -->
<template>
  <v-app dark>
    <nav-bar/>
    <v-main class="main-content">
      <router-view v-if="displayRoute" :key="routeKey"/>
      <ac-error v-else/>
      <ac-form-dialog
          :modelValue="store.state.showSupport"
          @update:modelValue="(val: boolean) => store.commit('supportDialog', val)"
          @submit="supportForm.submitThen(showSuccess)"
          v-bind="supportForm.bind"
          v-if="loadSupport"
          title="Get Support or Give Feedback!"
      >
        <v-row no-gutters>
          <v-col cols="12" class="text-center">
            <span class="headline">We respond to all requests within 24 hours, and often within the same hour!</span>
          </v-col>
          <v-col cols="12">
            <v-text-field
                label="Email"
                placeholder="test@example.com"
                v-bind="supportForm.fields.email.bind"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
                label="How can we help?"
                v-bind="supportForm.fields.body.bind"
            />
          </v-col>
        </v-row>
      </ac-form-dialog>
      <v-dialog
          v-model="showTicketSuccess"
          width="500"
          :attach="modalTarget"
      >
        <v-card id="supportSuccess">
          <v-card-text>
            Your support request has been received, and our team has been contacted! If you do not receive a reply
            soon, try emailing <a href="mailto:support@artconomy.com">support@artconomy.com</a>. Requests are
            responded to on the same day they are received.
          </v-card-text>

          <v-divider />

          <v-card-actions>
            <v-spacer />
            <v-btn
                color="primary"
                variant="plain"
                @click="showTicketSuccess = false"
            >
              OK
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <ac-form-dialog
        :modelValue="store.state.showAgeVerification"
        @update:modelValue="closeAgeVerification"
        v-if="viewerHandler.user.x && loadAgeVerification"
        @submit="closeAgeVerification"
        :large="true"
      >
        <v-row>
          <v-col cols="12" v-if="unverifiedInTheocracy">
            <v-alert type="error">
              You are currently accessing Artconomy from a location that has restrictive laws on adult content.
              You will not be allowed to load adult content unless specific conditions are met.
              <a href="https://artconomy.com/blog/on-the-recent-anti-porn-laws-and-their-impact-on-artconomy/">Please read our blog post for more details.</a>
            </v-alert>
          </v-col>
          <v-col cols="12" class="text-center">
            <span class="title">Warning: {{RATINGS_SHORT[contentRating]}}. Please verify your age and content preferences.</span>
          </v-col>
          <v-col cols="12" md="6">
            <ac-patch-field
                field-type="ac-birthday-field"
                label="Birthday"
                :disabled="unverifiedInTheocracy"
                :patcher="userHandler.patchers.birthday"
                :persistent-hint="true"
                :save-indicator="false"
                hint="You must be at least 18 years old to view adult content."
            />
          </v-col>
          <v-col cols="12" sm="6">
            <ac-patch-field field-type="v-switch" label="SFW Mode"
                            :patcher="viewerHandler.user.patchers.sfw_mode"
                            hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                            :save-indicator="false"
                            color="primary"
                            persistent-hint />
          </v-col>
          <v-col cols="12">
            <v-card-text :class="{disabled: viewerHandler.user.patchers.sfw_mode.model}">
              <ac-patch-field
                  field-type="ac-rating-field"
                  label="Select the maximum content rating you'd like to see when browsing."
                  :patcher="userHandler.patchers.rating"
                  :disabled="!adultAllowed"
                  :persistent-hint="true"
                  hint="You must be at least 18 years old to view adult content."
              />
            </v-card-text>
          </v-col>
          <v-col></v-col>
        </v-row>
        <template v-slot:bottom-buttons>
          <v-card-actions row wrap class="hidden-sm-and-down">
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="flat" type="submit" class="dialog-submit">Done</v-btn>
          </v-card-actions>
        </template>
      </ac-form-dialog>
      <v-snackbar v-model="showAlert" v-if="store.getters.latestAlert"
                  :color="store.getters.latestAlert.category"
                  :timeout="store.getters.latestAlert.timeout"
                  :attach="snackbarTarget"
                  top
      >
        {{latestAlert.message}}
        <v-btn
            dark
            variant="plain"
            class="close-status-alert"
            @click="showAlert = false"
        >
          Close
        </v-btn>
      </v-snackbar>
      <ac-markdown-explanation v-model="showMarkdownHelp" v-if="loadMarkdownHelp" />
      <v-snackbar
          :timeout="-1"
          v-if="socketState.x"
          :model-value="!!(socketState.x.serverVersion && (socketState.x.version !== socketState.x.serverVersion))"
          color="primary"
          shaped
          width="100vw"
          rounded="pill"
          :attach="statusTarget"
      >
        <div class="d-flex text-center">
          <div class="align-self-center">
            <strong>Artconomy has updated! Things might not quite work right until you refresh.</strong>
          </div>
          <v-btn color="green" class="ml-2" icon small @click="location.reload()" aria-label="Refresh Page"><v-icon :icon="mdiUpdate" /></v-btn>
        </div>
      </v-snackbar>
      <v-snackbar
          :timeout="-1"
          :model-value="!!(socketState.x!.serverVersion && socketState.x!.status === ConnectionStatus.CLOSED)"
          color="info"
          shaped
          rounded="pill"
          :attach="statusTarget"
      >
        <v-col class="text-center" id="reconnection-status-bar">
          <strong>Reconnecting...</strong>
        </v-col>
      </v-snackbar>
      <v-row no-gutters class="mb-4" v-if="contentReady">
        <v-col class="text-center">
          <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>
          <span class="mx-3 d-inline-block">|</span>
          <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
        </v-col>
      </v-row>
      <ac-cookie-consent />
    </v-main>
    <div class="dev-mode-overlay text-center" v-if="devMode">
      <v-icon size="50vw" :icon="mdiHammerWrench" />
    </div>
  </v-app>
</template>

<style scoped>
  .main-content {
    min-height: 90vh;
  }
  .dev-mode-overlay {
    width: 100vw;
    height: 100vh;
    position: fixed;
    top: 0;
    z-index: 1000000;
    display: flex;
    justify-content: center;
    align-content: center;
    opacity: .1;
    pointer-events: none;
  }
</style>

<script setup lang="ts">
// Remove the need for these, so we can remove this dependency.
import {computed, defineAsyncComponent, nextTick, ref, watch} from 'vue'

const AcError = defineAsyncComponent(() => import('@/components/navigation/AcError.vue'))
import NavBar from '@/components/navigation/NavBar.vue'
const AcFormDialog = defineAsyncComponent(() => import('@/components/wrappers/AcFormDialog.vue'))
import {useViewer} from '@/mixins/viewer.ts'
const AcMarkdownExplanation = defineAsyncComponent(() => import('@/components/fields/AcMarkdownExplination.vue'))
import {
  fallback,
  fallbackBoolean,
  genId,
  getCookie,
  paramsKey,
  RATINGS_SHORT,
  searchSchema as baseSearchSchema,
  setCookie, useLazyInitializer,
} from './lib/lib.ts'
import {User} from '@/store/profiles/types/User.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ConnectionStatus} from '@/types/ConnectionStatus.ts'
const AcPatchField = defineAsyncComponent(() => import('@/components/fields/AcPatchField.vue'))
const AcCookieConsent = defineAsyncComponent(() => import('@/components/AcCookieConsent.vue'))
import Product from '@/types/Product.ts'
import Submission from '@/types/Submission.ts'
import {Character} from '@/store/characters/types/Character.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {useRoute, useRouter} from 'vue-router'
import {useForm} from '@/store/forms/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'
import {useList} from '@/store/lists/hooks.ts'
import {ArtState} from '@/store/artState.ts'
import {useTargets} from '@/plugins/targets.ts'
import {mdiHammerWrench, mdiUpdate} from '@mdi/js'

const router = useRouter()
const route = useRoute()
const {viewer, viewerHandler, adultAllowed, unverifiedInTheocracy} = useViewer()

const sock = useSocket()
const store = useStore<ArtState>()

const showTicketSuccess = ref(false)

const supportForm = useForm('supportRequest', {
  endpoint: '/api/lib/support/request/',
  fields: {
    body: {value: '', validators: [{name: 'required'}]},
    email: {value: '', validators: [{name: 'email'}, {name: 'required'}]},
    referring_url: {value: route.fullPath},
  },
})

const contentRating = computed(() => store.state.contentRating)

const latestAlert = computed(() => store.getters.latestAlert)

const searchSchema = baseSearchSchema()

// Build the search form, which can be used at any time, and thus must be set up in the root.
const query = Object.fromEntries(new URLSearchParams(window.location.search).entries())
searchSchema.fields.q.value = fallback(query, 'q', '')
searchSchema.fields.content_ratings.value = fallback(query, 'content_ratings', '')
searchSchema.fields.minimum_content_rating.value = fallback(query, 'minimum_content_rating', 0)
searchSchema.fields.watch_list.value = fallbackBoolean(query, 'watch_list', false)
searchSchema.fields.shield_only.value = fallbackBoolean(query, 'shield_only', false)
searchSchema.fields.featured.value = fallbackBoolean(query, 'featured', false)
searchSchema.fields.rating.value = fallbackBoolean(query, 'rating', false)
searchSchema.fields.commissions.value = fallbackBoolean(query, 'commissions', false)
searchSchema.fields.artists_of_color.value = fallbackBoolean(query, 'artists_of_color', false)
searchSchema.fields.lgbt.value = fallbackBoolean(query, 'lgbt', false)
searchSchema.fields.max_price.value = fallback(query, 'max_price', '')
searchSchema.fields.min_price.value = fallback(query, 'min_price', '')
searchSchema.fields.max_turnaround.value = fallback(query, 'max_turnaround', '')
searchSchema.fields.page.value = fallback(query, 'page', 1)
// This variable is accessed in the tests to verify it's set up correctly, even though it does not appear to be used.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const searchForm = useForm('search', searchSchema)

watch(() => route.fullPath, (newPath: string) => {
  supportForm.fields.referring_url.update(newPath)
})

const forceRecompute = ref(0)

// Do we still need this?
store.commit('setSearchInitialized', true)

const socketState = useSingle('socketState', {
  endpoint: '#',
  persist: true,
  x: {
    status: ConnectionStatus.CONNECTING,
    // @ts-ignore
    // eslint-disable-next-line no-undef
    version: process.env['__COMMIT_HASH__'],
    serverVersion: '',
  },
})

const loadSupport = useLazyInitializer(() => store.state.showSupport)
const loadAgeVerification = useLazyInitializer(() => store.state.showAgeVerification)

watch(() => viewer.value?.username, (newName: string, oldName: string) => {
  if (oldName && (oldName !== '_') && (newName === '_')) {
    router.push('/')
  }
})

const getVersion = (versionData: {version: string}) => {
  socketState.updateX({serverVersion: versionData.version})
}


const socketStart = () => {
  sock.addListener('version', 'App', getVersion)
  sock.addListener('viewer', 'App', viewerHandler.user.makeReady)
  sock.addListener('error', 'App', console.error)
  sock.addListener('reset', 'App', (payload: {exclude?: string[]}) => {
    sock.socket!.close()
    // Wait a second to reconnect to give a chance for all outstanding requests to complete.
    // We'll probably want to find a better way to handle this later.
    setTimeout(() => { sock.socket!.reconnect() }, 2000)
  })
  sock.connectListeners.initialize = () => {
    socketState.updateX({status: ConnectionStatus.CONNECTED})
    sock.send('version', {})
    sock.send('viewer', {socket_key: getCookie('ArtconomySocketKey')})
  }
  sock.disconnectListeners.disconnected = () => {
    socketState.updateX({status: ConnectionStatus.CLOSED})
  }
  sock.open()
}

if (!getCookie('ArtconomySocketKey')) {
  // Note: This cookie isn't secure from potential code injection attacks, so we only use it to determine
  // if we should reset the connection upon a login/logout event. The login cookie is HTTPS only.
  setCookie('ArtconomySocketKey', genId())
}

nextTick(socketStart)

const closeAgeVerification = () => {
  store.commit('setShowAgeVerification', false)
}

const showSuccess = () => {
  store.commit('supportDialog', false)
  showTicketSuccess.value = true
}

const mode = () => {
  return process.env.NODE_ENV
}

const userHandler = computed(() => {
  return viewerHandler.user as SingleController<User>
})

const devMode = computed(() => {
  // Accessing a property registers that property as a listener. Even if we do nothing with it, changing its value
  // will force recomputation of this value.
  // eslint-disable-next-line no-unused-expressions
  forceRecompute.value
  return mode() === 'development'
})

const routeKey = computed(() => {
  // Dynamically changes the key for the route in such a way that we only force Vue to recreate the component
  // when absolutely necessary and it wouldn't otherwise detect.
  //
  // If we don't do this, then the component won't be recreated when we, say, jump from one profile page to another.
  // If we use the standard advice of 'make route.fullPath the key', we'll be recreating far too often, since
  // we have many nested routes.
  return paramsKey(route.params)
})

const showMarkdownHelp = computed({
  get: () => {
    return store.state.markdownHelp
  },
  set: (val: boolean) => {
    store.commit('setMarkdownHelp', val)
  }
})

// We have a conditional on the loading of the markdown component to avoid pulling down the
// parser library when we don't have to.
const loadMarkdownHelp = useLazyInitializer(showMarkdownHelp)

const alertDismissed = ref(false)

const showAlert = computed({
  get: () => {
    if (alertDismissed.value) {
      return false
    }
    return Boolean(store.getters.latestAlert)
  },
  set: (val: boolean) => {
    alertDismissed.value = !val
    if (!val) {
      alertDismissed.value = true
      nextTick(() => {
        store.commit('popAlert')
        alertDismissed.value = false
      })
    }
  }
})

// Set up search list entries as early as possible.
useList<Submission>('searchSubmissions', {
  endpoint: '/api/profiles/search/submission/',
  persistent: true,
})
useList<Product>('searchProducts', {
  endpoint: '/api/sales/search/product/',
  persistent: true,
})
useList<Character>('searchCharacters', {
  endpoint: '/api/profiles/search/character/',
  persistent: true,
})
useList<TerseUser>('searchProfiles', {
  endpoint: '/api/profiles/search/user/',
  persistent: true,
})

const displayRoute = computed(() => !store.state.errors!.code)

watch(() => (viewer.value as User)?.email, (val?: string) => {
  if (viewer.value && (viewer.value as User).guest_email) {
    // Let the other watcher handle this.
    return
  }
  supportForm.fields.email.update(val || '', false)
})

watch(() => (viewer.value as User)?.guest_email, (val?: string) => {
  if (!val) {
    return
  }
  supportForm.fields.email.update(val, false)
})

watch(() => route.fullPath, (newPath: string, oldPath?: string) => {
    nextTick(() => {
    window._paq.push(['setCustomUrl', window.location.origin + newPath])
    window._paq.push(['setDocumentTitle', document.title])
    if (oldPath) {
      window._paq.push(['setReferrerUrl', window.location.origin + oldPath])
    }
    const excluded: any[] = ['FAQ', 'Profile', 'About', 'BuyAndSell', 'Other']
    if (excluded.includes(route.name)) {
      return
    }
    window._paq.push(['trackPageView'])
    window.fbq('track', 'PageView')
  })
}, {immediate: true})

const {modalTarget, snackbarTarget, statusTarget} = useTargets()

const location = window.location

const contentReady = ref(false)

router.isReady().then(() => contentReady.value = true)
</script>
