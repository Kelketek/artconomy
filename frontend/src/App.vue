<template>
  <v-app dark>
    <nav-bar />
    <v-content>
      <v-container fluid>
        <div v-if="$root.errorCode !== null" class="container error-container">
          <div class="row">
            <div class="col-12 text-xs-center">
              <img class="error-logo" :src="errorLogo"/>
            </div>
            <div class="col-12 text-xs-center home-title">
              <h1>Whoops!</h1>
              <p v-if="$root.errorCode === 500">
                Something went wrong. We've notified our developers and will get it fixed as soon as we can!
              </p>
              <p v-if="$root.errorCode === 503">
                Artconomy is currently updating or under maintenance. Please refresh in a few minutes and try again!
              </p>
              <p v-else-if="$root.errorCode === 400">
                Something seems wrong with your request. Could you check the URL?
              </p>
              <p v-else-if="$root.errorCode === 404">
                We couldn't find that page. It might not exist or you might not have the right privileges to see it.
              </p>
              <p v-else-if="$root.errorCode === 403">
                Access to this page is restricted. Please make sure you're logged into an account that has access to it.
              </p>
              <p v-else>
                Something weird happened. Could you please contact support and tell us about it?
              </p>
            </div>
          </div>
        </div>
        <router-view v-else-if="$root.user !== null" />
      </v-container>
      <v-container>
        <v-layout row wrap>
          <v-flex v-if="$root.user && !$root.user.username" xs12 text-xs-center>
            <p>Please read our <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link> and <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>.</p>
            <p>Check out our <a href="/blog/" target="_blank">blog</a> for updates, or read the <router-link :to="{name: 'FAQ'}">FAQ</router-link> for more information.</p>
            <p>If you're having trouble, please <a @click="showSupport = true">Contact support.</a></p>
          </v-flex>
        </v-layout>
      </v-container>
      <ac-form-dialog
          v-model="showSupport"
          :schema="supportSchema"
          :model="supportModel"
          url="/api/lib/v1/support/request/"
          title="Contact Support!"
          :success="showSuccess"
          :reset-after="false"
      >
        <div slot="header">
          <v-flex class="text-xs-center">
            <h1>We respond to all support requests the same day we receive them, often within the same hour!</h1>
          </v-flex>
        </div>
      </ac-form-dialog>
      <v-dialog
          v-model="showTicketSuccess"
          width="500"
      >
        <v-card>
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
    </v-content>
  </v-app>
</template>

<script>
  import NavBar from './components/NavBar'
  import VueFormGenerator from 'vue-form-generator'
  import {EventBus, genId, setMetaContent} from './lib'
  import AcFormDialog from './components/ac-form-dialog'
  import Viewer from './mixins/viewer'
  export default {
    name: 'app',
    mixins: [Viewer],
    data () {
      return {
        showSupport: false,
        showTicketSuccess: false,
        supportModel: {
          email: (this.viewer && this.viewer.email) || '',
          body: '',
          referring_url: this.$route.fullPath
        },
        supportSchema: {
          fields: [
            {
              type: 'v-text',
              inputType: 'text',
              label: 'How can we help?',
              model: 'body',
              featured: true,
              required: true,
              multiLine: true,
              validator: VueFormGenerator.validators.string
            },
            {
              type: 'v-text',
              inputType: 'text',
              label: 'Email',
              model: 'email',
              id: 'login-email',
              placeholder: 'example@example.com',
              featured: true,
              required: true,
              validator: VueFormGenerator.validators.email
            }
          ]
        }
      }
    },
    components: {
      AcFormDialog,
      NavBar
    },
    methods: {
      showSuccess () {
        this.showSupport = false
        this.showTicketSuccess = true
        this.supportModel.body = ''
      },
    },
    watch: {
      '$root.errorCode' (val) {
        if (val) {
          setMetaContent('prerender-status-code', val)
        }
      },
      '$route': {
        deep: true,
        handler () {
          console.log(this.$route)
          this.supportModel.referring_url = this.$route.fullPath
        }
      },
      viewer: {
        deep: true,
        immediate: true,
        handler () {
          if (this.viewer && this.viewer.email){
            this.supportModel.email = this.viewer.email
          }
          this.supportModel.email = ''
        }
      }
    },
    created () {
      EventBus.$on('showSupport', () => {this.showSupport = true})
      if (this.viewer && this.viewer.email) {
        this.supportModel.email = this.viewer.email
      }
    }
  }
</script>

<style>
  a {
    text-decoration: none;
  }
  .error-logo {
    width: 25%;
    margin-bottom: 2rem;
  }
  .pb-10 {
    padding-bottom: 6rem !important;
  }
  .error-title {
    margin-bottom: 2rem;
  }
</style>
