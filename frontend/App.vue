<!--suppress JSUnusedGlobalSymbols -->
<template>
  <v-app dark>
    <nav-bar/>
    <v-content class="pb-5 main-content">
      <ac-error></ac-error>
      <router-view v-if="displayRoute" :key="routeKey"/>
      <ac-form-dialog
          :value="$store.state.showSupport"
          @input="setSupport"
          @submit="supportForm.submitThen(showSuccess)"
          v-bind="supportForm.bind"
      >
        <div slot="header">
          <v-flex class="text-xs-center">
            <h1>We respond to all support requests within 24 hours, and often within the same hour!</h1>
          </v-flex>
        </div>
        <v-layout row wrap>
          <v-flex xs12>
            <v-text-field
                label="Email"
                placeholder="test@example.com"
                v-bind="supportForm.fields.email.bind"
                v-on="supportForm.fields.email.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12>
            <v-textarea
                label="How can we help?"
                v-bind="supportForm.fields.body.bind"
                v-on="supportForm.fields.body.on"
            ></v-textarea>
          </v-flex>
        </v-layout>
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

          <v-divider></v-divider>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
                color="primary"
                flat
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
            flat
            @click="showAlert = false"
        >
          Close
        </v-btn>
      </v-snackbar>
      <ac-markdown-explanation v-model="showMarkdownHelp"></ac-markdown-explanation>
    </v-content>
    <v-content>
      <v-layout row wrap>
        <v-flex text-xs-right px-2>
          <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>
        </v-flex>
        <v-flex d-flex shrink><v-divider vertical /></v-flex>
        <v-flex text-xs-left px-2>
          <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
        </v-flex>
      </v-layout>
    </v-content>
  </v-app>
</template>

<style scoped>
  .main-content {
    min-height: 90vh;
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
import {fallback, fallbackBoolean, searchSchema} from './lib'
import {User} from '@/store/profiles/types/User'

  @Component({components: {AcMarkdownExplanation, AcError, AcFormDialog, NavBar}})
export default class App extends mixins(Viewer) {
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

    public created() {
      this.supportForm = this.$getForm('supportRequest', {
        endpoint: '/api/lib/v1/support/request/',
        fields: {
          body: {value: '', validators: [{name: 'required'}]},
          email: {value: '', validators: [{name: 'email'}, {name: 'required'}]},
          referring_url: {value: this.$route.fullPath},
        },
      }
      )
      const query = this.$route.query
      this.searchForm = this.$getForm('search', searchSchema())
      this.searchForm.fields.q.update(fallback(query, 'q', ''))
      this.searchForm.fields.watch_list.update(fallbackBoolean(query, 'watch_list', null))
      this.searchForm.fields.shield_only.update(fallbackBoolean(query, 'shield_only', null))
      this.searchForm.fields.featured.update(fallbackBoolean(query, 'featured', null))
      this.searchForm.fields.rating.update(fallbackBoolean(query, 'rating', null))
      this.searchForm.fields.max_price.update(fallback(query, 'max_price', ''))
      this.searchForm.fields.min_price.update(fallback(query, 'min_price', ''))
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

    public get routeKey() {
      // Dynamically changes the key for the route in such a way that we only force Vue to recreate the component
      // when absolutely necessary and it wouldn't otherwise detect.
      //
      // If we don't do this, then the component won't be recreated when we, say, jump from one profile page to another.
      // If we use the standard advice of 'make $route.fullPath the key', we'll be recreating far too often, since
      // we have many nested routes.
      let key = ''
      const params = Object.keys(this.$route.params)
      params.sort()
      for (const param of params) {
        if (param.endsWith('Id') || param.endsWith('Name') || param === 'username') {
          key += `${param}:${this.$route.params[param]}|`
        }
      }
      return key
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
