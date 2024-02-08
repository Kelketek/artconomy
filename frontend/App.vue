<!--suppress JSUnusedGlobalSymbols -->
<template>
  <v-app dark>
    <nav-bar v-if="showNav"/>
    <v-main class="main-content">
      <ac-error/>
      <router-view v-if="displayRoute" :key="routeKey"/>
      <ac-form-dialog
          :modelValue="$store.state.showSupport"
          @update:modelValue="(val: boolean) => $store.commit('supportDialog', val)"
          @submit="supportForm.submitThen(showSuccess)"
          v-bind="supportForm.bind"
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
          :attach="$modalTarget"
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
        :modelValue="$store.state.showAgeVerification"
        @update:modelValue="closeAgeVerification"
        v-if="viewerHandler.user.x"
        @submit="closeAgeVerification"
        :large="true"
      >
        <v-row>
          <v-col cols="12" class="text-center">
            <span class="title">Warning: {{ratingsShort[$store.state.contentRating]}}. Please verify your age and content preferences.</span>
          </v-col>
          <v-col cols="12" md="6">
            <ac-patch-field
                field-type="ac-birthday-field"
                label="Birthday"
                :patcher="birthdayUserHandler.patchers.birthday"
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
      <v-snackbar v-model="showAlert" v-if="$store.getters.latestAlert"
                  :color="$store.getters.latestAlert.category"
                  :timeout="$store.getters.latestAlert.timeout"
                  id="alert-bar"
                  :attach="$snackbarTarget"
                  top
      >
        {{$store.getters.latestAlert.message}}
        <v-btn
            dark
            variant="plain"
            @click="showAlert = false"
        >
          Close
        </v-btn>
      </v-snackbar>
      <ac-markdown-explanation v-model="showMarkdownHelp" />
      <v-snackbar
          :timeout="-1"
          v-if="socketState.x"
          :model-value="!!(socketState.x.serverVersion && (socketState.x.version !== socketState.x.serverVersion))"
          color="green"
          shaped
          width="100vw"
          rounded="pill"
          :attach="$statusTarget"
      >
        <div class="d-flex text-center">
          <div class="align-self-center">
            <strong>Artconomy has updated! Things might not quite work right until you refresh.</strong>
          </div>
          <v-btn color="primary" class="ml-2" icon small @click="location.reload()"><v-icon icon="mdi-update" /></v-btn>
        </div>
      </v-snackbar>
      <v-snackbar
          :timeout="-1"
          :model-value="!!(socketState.x!.serverVersion && socketState.x!.status === CLOSED)"
          color="info"
          shaped
          rounded="pill"
          :attach="$statusTarget"
      >
        <div class="text-center">
          <strong>Reconnecting...</strong>
        </div>
      </v-snackbar>
      <v-row no-gutters class="mb-4">
        <v-col class="text-center">
          <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>
          <span class="mx-3 d-inline-block">|</span>
          <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
        </v-col>
      </v-row>
      <ac-cookie-consent />
    </v-main>
    <div class="dev-mode-overlay text-center" v-if="devMode">
      <v-icon size="50vw" icon="mdi-hammer-wrench" />
    </div>
    <div id="modal-target" />
    <div id="snackbar-target" />
    <div id="status-target" />
    <div id="menu-target" />
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

<script lang="ts">
// Remove the need for these, so we can remove this dependency.
import AcError from '@/components/navigation/AcError.vue'
import NavBar from '@/components/navigation/NavBar.vue'
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import Viewer from '@/mixins/viewer.ts'
import AcMarkdownExplanation from '@/components/fields/AcMarkdownExplination.vue'
import {
  fallback,
  fallbackBoolean,
  genId,
  getCookie,
  paramsKey,
  RATINGS_SHORT,
  searchSchema,
  setCookie,
} from './lib/lib.ts'
import {User} from '@/store/profiles/types/User.ts'
import Nav from '@/mixins/nav.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ConnectionStatus} from '@/types/ConnectionStatus.ts'
import {SocketState} from '@/types/SocketState.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcCookieConsent from '@/components/AcCookieConsent.vue'
import {ListController} from '@/store/lists/controller.ts'
import Product from '@/types/Product.ts'
import Submission from '@/types/Submission.ts'
import {Character} from '@/store/characters/types/Character.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import RatingRefresh from '@/mixins/RatingRefresh.ts'
import Ratings from '@/mixins/ratings.ts'

@Component({
  components: {AcCookieConsent, AcPatchField, AcForm, AcMarkdownExplanation, AcError, AcFormDialog, NavBar},
})
class App extends mixins(Viewer, Nav, RatingRefresh, Ratings) {
  public OFFENSIVE = 3
  public showTicketSuccess = false
  public ratingsShort = RATINGS_SHORT
  public loaded = false
  public supportForm: FormController = null as unknown as FormController
  public alertDismissed: boolean = false
  public searchForm: FormController = null as unknown as FormController
  public socketState: SingleController<SocketState> = null as unknown as SingleController<SocketState>
  // Search lists
  public productSearch: ListController<Product> = null as unknown as ListController<Product>
  public submissionSearch: ListController<Submission> = null as unknown as ListController<Submission>
  public characterSearch: ListController<Character> = null as unknown as ListController<Character>
  public profileSearch: ListController<TerseUser> = null as unknown as ListController<TerseUser>
  public searchInitialized = false
  // For testing.
  public forceRecompute = 0
  public location = location
  public CLOSED = ConnectionStatus.CLOSED
  public showNav = false
  public Infinity = Infinity

  public refreshLists = ['submissionSearch', 'characterSearch', 'productSearch']

  @Watch('viewer.username')
  public sendHome(newName: string, oldName: string) {
    if (oldName && (oldName !== '_') && (newName === '_')) {
      this.$router.push('/')
    }
  }

  @Watch('$route.name', {immediate: true})
  public initializeSearch(nameVal: null|string) {
    /* istanbul ignore if */
    if (!nameVal) {
      return
    }
    /* istanbul ignore if */
    if (this.$store.state.searchInitialized) {
      this.searchForm = this.$getForm('search')
      this.$nextTick(() => { this.showNav = true })
      return
    }
    const query = {...this.$route.query}
    this.searchForm = this.$getForm('search', searchSchema())
    this.searchForm.fields.q.update(fallback(query, 'q', ''))
    this.searchForm.fields.content_ratings.update(fallback(query, 'content_ratings', ''))
    this.searchForm.fields.minimum_content_rating.update(fallback(query, 'minimum_content_rating', 0))
    this.searchForm.fields.watch_list.update(fallbackBoolean(query, 'watch_list', false))
    this.searchForm.fields.shield_only.update(fallbackBoolean(query, 'shield_only', false))
    this.searchForm.fields.featured.update(fallbackBoolean(query, 'featured', false))
    this.searchForm.fields.rating.update(fallbackBoolean(query, 'rating', false))
    this.searchForm.fields.commissions.update(fallbackBoolean(query, 'commissions', false))
    this.searchForm.fields.artists_of_color.update(fallbackBoolean(query, 'artists_of_color', false))
    this.searchForm.fields.lgbt.update(fallbackBoolean(query, 'lgbt', false))
    this.searchForm.fields.max_price.update(fallback(query, 'max_price', ''))
    this.searchForm.fields.min_price.update(fallback(query, 'min_price', ''))
    this.searchForm.fields.max_turnaround.update(fallback(query, 'max_turnaround', ''))
    this.searchForm.fields.page.update(fallback(query, 'page', 1))
    this.$store.commit('setSearchInitialized', true)
    // Make damn sure that the NavBar doesn't load before we have fully initialized search.
    this.$nextTick(() => { this.showNav = true })
  }

  public created() {
    /* istanbul ignore if */
    if (window.USER_PRELOAD) {
      this.setUser(window.USER_PRELOAD)
    }
    this.supportForm = this.$getForm('supportRequest', {
      endpoint: '/api/lib/support/request/',
      fields: {
        body: {value: '', validators: [{name: 'required'}]},
        email: {value: '', validators: [{name: 'email'}, {name: 'required'}]},
        referring_url: {value: this.$route.fullPath},
      },
    })
    this.socketState = this.$getSingle('socketState', {
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
    // If several tabs are open at once (like restoring from a crash), they might set this key rapidly next to each
    // other. Defer to next tick to severely reduce the chance of a race condition.
    if (!getCookie('ArtconomySocketKey')) {
      // Note: This cookie isn't secure from potential code injection attacks, so we only use it to determine
      // if we should reset the connection upon a login/logout event. The login cookie is HTTPS only.
      setCookie('ArtconomySocketKey', genId())
      this.$nextTick(this.socketStart)
    } else {
      this.$nextTick(this.socketStart)
    }
    // Set up search list entries as early as possible.
    this.submissionSearch = this.$getList('searchSubmissions', {
      endpoint: '/api/profiles/search/submission/',
      persistent: true,
    })
    this.productSearch = this.$getList('searchProducts', {
      endpoint: '/api/sales/search/product/',
      persistent: true,
    })
    this.characterSearch = this.$getList('searchCharacters', {
      endpoint: '/api/profiles/search/character/',
      persistent: true,
    })
    this.profileSearch = this.$getList('searchProfiles', {
      endpoint: '/api/profiles/search/user/',
      persistent: true,
    })
  }

  public get birthdayUserHandler() {
    return this.viewerHandler.user as SingleController<User|AnonUser>
  }

  public get userHandler() {
    return this.viewerHandler.user as SingleController<User|AnonUser>
  }

  public socketStart() {
    this.$sock.addListener('version', 'App', this.getVersion)
    this.$sock.addListener('viewer', 'App', this.setUser)
    this.$sock.addListener('error', 'App', console.error)
    this.$sock.addListener('reset', 'App', (payload: {exclude?: string[]}) => {
      this.$sock.socket!.close()
      // Wait a second to reconnect to give a chance for all outstanding requests to complete.
      // We'll probably want to find a better way to handle this later.
      setTimeout(() => { this.$sock.socket!.reconnect() }, 2000)
    })
    this.$sock.connectListeners.initialize = () => {
      this.socketState.updateX({status: ConnectionStatus.CONNECTED})
      this.$sock.send('version', {})
      this.$sock.send('viewer', {socket_key: getCookie('ArtconomySocketKey')})
    }
    this.$sock.disconnectListeners.disconnected = () => {
      this.socketState.updateX({status: ConnectionStatus.CLOSED})
    }
    this.$sock.open()
  }

  public getVersion(versionData: {version: string}) {
    this.socketState.updateX({serverVersion: versionData.version})
  }

  public setUser(user: AnonUser|User) {
    this.viewerHandler.user.makeReady(user)
  }

  public showSuccess() {
    this.$store.commit('supportDialog', false)
    this.showTicketSuccess = true
  }

  public get displayRoute() {
    return this.viewer !== null && !this.$store.state.errors!.code
  }

  public get showMarkdownHelp() {
    return this.$store.state.markdownHelp
  }

  public set showMarkdownHelp(val: boolean) {
    this.$store.commit('setMarkdownHelp', val)
  }

  public get showAlert() {
    if (this.alertDismissed) {
      return false
    }
    return Boolean(this.$store.getters.latestAlert)
  }

  public set showAlert(val) {
    this.alertDismissed = !val
    if (!val) {
      this.alertDismissed = true
      this.$nextTick(() => {
        this.$store.commit('popAlert')
        this.alertDismissed = false
      })
    }
  }

  // To make testing easier via spies without doing anything to the environment.
  public mode() {
    return process.env.NODE_ENV
  }

  public closeAgeVerification() {
    this.$store.commit('setShowAgeVerification', false)
  }

  public get devMode() {
    // Accessing a property registers that property as a listener. Even if we do nothing with it, changing its value
    // will force recomputation of this value.
    // eslint-disable-next-line no-unused-expressions
    this.forceRecompute
    return this.mode() === 'development'
  }

  public get routeKey() {
    // Dynamically changes the key for the route in such a way that we only force Vue to recreate the component
    // when absolutely necessary and it wouldn't otherwise detect.
    //
    // If we don't do this, then the component won't be recreated when we, say, jump from one profile page to another.
    // If we use the standard advice of 'make $route.fullPath the key', we'll be recreating far too often, since
    // we have many nested routes.
    return paramsKey(this.$route.params)
  }

  @Watch('viewer.email')
  private updateSupportEmail(val: string|undefined) {
    const viewer = this.viewer as User
    if (viewer && viewer.guest_email) {
      // Let the other watcher handle this.
      return
    }
    this.supportForm.fields.email.update(val || '', false)
  }

  @Watch('viewer.guest_email')
  private updateSupportEmailGuest(val: string|undefined) {
    if (!val) {
      return
    }
    this.supportForm.fields.email.update(val, false)
  }

  @Watch('$route.fullPath', {immediate: true})
  private trackPage(newPath: string, oldPath: string|undefined) {
    this.$nextTick(() => {
      window._paq.push(['setCustomUrl', window.location.origin + newPath])
      window._paq.push(['setDocumentTitle', document.title])
      if (oldPath) {
        window._paq.push(['setReferrerUrl', window.location.origin + oldPath])
      }
      const excluded: any[] = ['FAQ', 'Profile', 'About', 'BuyAndSell', 'Other']
      if (!this.$route || excluded.includes(this.$route.name)) {
        return
      }
      window._paq.push(['trackPageView'])
    })
  }

  @Watch('$route.fullPath', {immediate: true, deep: true})
  private updateReferringUrl() {
    // Let's do next tick since sometimes meta information is modified on route load.
    if (!this.supportForm) {
      return
    }
    this.supportForm.fields.referring_url.update(this.$route.fullPath)
  }
}

export default toNative(App)
</script>

<style scoped>
  a {
    text-decoration: none;
  }
</style>

<style>
  body {
    background-color: rgb(48, 48, 48)
  }
</style>
