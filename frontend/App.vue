<!--suppress JSUnusedGlobalSymbols -->
<template>
  <v-app dark>
    <nav-bar/>
    <v-main class="main-content">
      <ac-error/>
      <router-view v-if="displayRoute" :key="routeKey"/>
      <ac-form-dialog
          :value="$store.state.showSupport"
          @input="setSupport"
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
                v-on="supportForm.fields.email.on"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
                label="How can we help?"
                v-bind="supportForm.fields.body.bind"
                v-on="supportForm.fields.body.on"
            />
          </v-col>
        </v-row>
      </ac-form-dialog>
      <v-dialog
          v-model="showTicketSuccess"
          width="500"
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
                text
                @click="showTicketSuccess = false"
            >
              OK
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-snackbar v-model="showAlert" v-if="latestAlert"
                  :color="latestAlert.category"
                  :timeout="latestAlert.timeout"
                  id="alert-bar"
                  top
      >
        {{latestAlert.message}}
        <v-btn
            dark
            text
            @click="showAlert = false"
        >
          Close
        </v-btn>
      </v-snackbar>
      <ac-markdown-explanation v-model="showMarkdownHelp" />
    </v-main>
    <v-main>
      <v-snackbar
          :timeout="-1"
          :value="socketState.x.serverVersion && (socketState.x.version !== socketState.x.serverVersion)"
          color="green"
          shaped
          width="100vw"
          rounded="pill"
      >
        <div class="d-flex text-center">
          <div class="align-self-center">
            <strong>Artconomy has updated! Things might not quite work right until you refresh.</strong>
          </div>
          <v-btn color="primary" class="ml-2" fab small @click="location.reload()"><v-icon>update</v-icon></v-btn>
        </div>
      </v-snackbar>
      <v-snackbar
          :timeout="-1"
          :value="socketState.x.serverVersion && socketState.x.status === CLOSED"
          color="info"
          shaped
          rounded="pill"
      >
        <div class="text-center">
          <strong>Reconnecting...</strong>
        </div>
      </v-snackbar>
      <v-row no-gutters class="mb-4">
        <v-col class="text-right px-2">
          <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>
        </v-col>
        <v-col class="d-flex shrink"><v-divider vertical /></v-col>
        <v-col class="text-left px-2">
          <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
        </v-col>
      </v-row>
    </v-main>
    <div class="dev-mode-overlay text-center" v-if="devMode">
      <v-icon size="50vw">construction</v-icon>
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
    opacity: .25;
    pointer-events: none;
  }
</style>

<script lang="ts">
import {Getter, Mutation, State} from 'vuex-class'
import AcError from '@/components/navigation/AcError.vue'
import NavBar from '@/components/navigation/NavBar.vue'
import Component, {mixins} from 'vue-class-component'
import {ErrorState} from '@/store/errors/types'
import {FormController} from '@/store/forms/form-controller'
import {Watch} from 'vue-property-decorator'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import Viewer from '@/mixins/viewer'
import {UserStoreState} from '@/store/profiles/types/UserStoreState'
import {Alert} from '@/store/state'
import AcMarkdownExplanation from '@/components/fields/AcMarkdownExplination.vue'
import {fallback, fallbackBoolean, paramsKey, searchSchema} from './lib/lib'
import {User} from '@/store/profiles/types/User'
import Nav from '@/mixins/nav'
import {SingleController} from '@/store/singles/controller'
import {ConnectionStatus} from '@/types/ConnectionStatus'
import {SocketState} from '@/types/SocketState'

@Component({components: {AcMarkdownExplanation, AcError, AcFormDialog, NavBar}})
export default class App extends mixins(Viewer, Nav) {
  @State('profiles') public p!: UserStoreState
  @Mutation('supportDialog') public setSupport: any
  @Mutation('popAlert') public popAlert: any
  @Mutation('setMarkdownHelp') public setMarkdownHelp: any
  @State('markdownHelp') public markdownHelp!: boolean
  @State('errors') public errors!: ErrorState
  @Getter('logo', {namespace: 'errors'}) public errorLogo!: string
  @Getter('latestAlert') public latestAlert!: Alert | null
  @State('iFrame') public iFrame!: boolean
  public showTicketSuccess = false
  public loaded = false
  public supportForm: FormController = null as unknown as FormController
  public alertDismissed: boolean = false
  public searchForm: FormController = null as unknown as FormController
  public socketState: SingleController<SocketState> = null as unknown as SingleController<SocketState>
  public searchInitialized = false
  // For testing.
  public forceRecompute = 0
  public location = location
  public CLOSED = ConnectionStatus.CLOSED

  @Watch('$route.name', {immediate: true})
  public initializeSearch(nameVal: null|string) {
    /* istanbul ignore if */
    if (!nameVal) {
      return
    }
    /* istanbul ignore if */
    if (this.$store.state.searchInitialized) {
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
    this.searchForm.fields.artists_of_color.update(fallbackBoolean(query, 'artists_of_color', false))
    this.searchForm.fields.lgbt.update(fallbackBoolean(query, 'lgbt', false))
    this.searchForm.fields.max_price.update(fallback(query, 'max_price', ''))
    this.searchForm.fields.min_price.update(fallback(query, 'min_price', ''))
    this.$store.commit('setSearchInitialized', true)
  }

  public created() {
    this.supportForm = this.$getForm('supportRequest', {
      endpoint: '/api/lib/v1/support/request/',
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
        version: __COMMIT_HASH__,
        serverVersion: '',
      },
    })
    this.$sock.addListener('version', this.getVersion)
    // To listen in to all messages, uncomment the following.
    // this.$sock.addListener('*', (data: any) => console.log(data))
    this.$sock.connectListeners.push(() => {
      this.socketState.updateX({status: ConnectionStatus.CONNECTED})
      this.$sock.send('version', {})
    })
    this.$sock.disconnectListeners.push(() => {
      this.socketState.updateX({status: ConnectionStatus.CLOSED})
    })
    window.pintrk('load', '2614118947445')
  }

  public getVersion(versionData: {version: string}) {
    this.socketState.updateX({serverVersion: versionData.version})
  }

  public showSuccess() {
    this.setSupport(false)
    this.showTicketSuccess = true
  }

  public get displayRoute() {
    return this.viewer !== null && !this.errors.code
  }

  public get showMarkdownHelp() {
    return this.markdownHelp
  }

  public set showMarkdownHelp(val: boolean) {
    this.setMarkdownHelp(val)
  }

  public get showAlert() {
    if (this.alertDismissed) {
      return false
    }
    return Boolean(this.latestAlert)
  }

  public set showAlert(val) {
    this.alertDismissed = !val
    if (!val) {
      this.alertDismissed = true
      this.$nextTick(() => {
        this.popAlert()
        this.alertDismissed = false
      })
    }
  }

  // To make testing easier via spies without doing anything to the environment.
  public mode() {
    return process.env.NODE_ENV
  }

  public get devMode() {
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
  private trackPage(newPath, oldPath) {
    // Let's do next tick since sometimes meta information is modified on route load.
    this.$nextTick(() => {
      window._paq.push(['setCustomUrl', window.location + ''])
      window._paq.push(['setDocumentTitle', document.title])
      if (oldPath) {
        window._paq.push(['setReferrerUrl', window.location.origin + oldPath])
      }
      window._paq.push(['trackPageView'])
      window.pintrk('track', 'pagevisit', {url: window.location + ''})
    })
  }

  @Watch('$route', {immediate: true, deep: true})
  private updateReferringUrl() {
    if (!this.supportForm) {
      return
    }
    this.supportForm.fields.referring_url.update(this.$route.fullPath)
  }
}
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
