<template>
  <div class="container">
    <div class="row-centered">
      <div class="col-12 col-md-6 col-lg-4 col-centered text-xs-center">
        <form @submit.prevent="sendLogin">
          <v-tabs class="inverse" v-model="loginTab">
            <v-tab href="#tab-login" id="set-login">
              Login
            </v-tab>
            <v-tab href="#tab-register" id="set-register">
              Register
            </v-tab>
            <v-tab href="#tab-forgot" id="set-forgot">
              Forgot
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="loginTab">
            <v-tab-item id="tab-login">
              <div class="pt-2"></div>
              <vue-form-generator id="loginForm" ref="loginForm" :schema="loginSchema" :model="loginModel"
                                  :options="loginOptions" />
              <v-btn type="submit" id="loginSubmit" color="primary" @click.prevent="sendLogin">
                Login
              </v-btn>
            </v-tab-item>
            <v-tab-item id="tab-register">
              <div class="pt-2"></div>
              <vue-form-generator id="registerForm" ref="registerForm" :schema="registerSchema" :model="loginModel"
                                  :options="loginOptions" />
              <p>
                By Registering, you are agreeing to be bound by Artconomy's <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
                and <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>.
              </p>
              <v-btn type="submit" id="registerSubmit" color="primary" @click.prevent="sendLogin">
                Register
              </v-btn>
            </v-tab-item>
            <v-tab-item id="tab-forgot">
              <div class="pt-2"></div>
              <p>Enter your username or email address below, and we will send you a link to reset your password.</p>
              <vue-form-generator id="forgotForm" ref="forgotForm" :schema="forgotSchema" :model="loginModel"
                                  :options="loginOptions" />
              <div v-if="resetSent" class="email-sent">
                Email sent! Please check your inbox!
              </div>
              <v-btn type="submit" id="forgotSubmit" color="primary" @click.prevent="sendLogin">
                Reset
              </v-btn>
            </v-tab-item>
          </v-tabs-items>
          <div>
          </div>
          <v-dialog
              v-model="showTokenPrompt"
              width="500"
              @keydown.enter="sendLogin"
          >
            <v-card>
              <v-card-text>
                <p>
                  This account is protected by Two Factor Authentication. Please use your
                  authentication device to generate a login token, or check your Telegram messages if you've set
                  up Telegram 2FA.
                </p>
                <p>If you have lost your 2FA device/service, please contact support@artconomy.com with the subject 'Lost 2FA'.</p>
                <vue-form-generator id="tokenForm" ref="tokenForm" :schema="tokenSchema" :model="loginModel"
                                    :options="loginOptions" />
                <div class="text-xs-center">
                  <v-btn @click="showTokenPrompt = false">Cancel</v-btn>
                  <v-btn type="submit" id="tokenSubmit" color="primary" @click.prevent="sendLogin">
                    Verify
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-dialog>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .email-sent {
    color: red;
    text-align: center;
  }
</style>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import { artCall, paramHandleMap, recaptchaSiteKey, setCookie, setErrors } from '../lib'

  const TAB_MAP = {
    'tab-login': {url: '/api/profiles/v1/login/', label: 'Login', form: 'loginForm', sendToProfile: false},
    'tab-register': {url: '/api/profiles/v1/register/', label: 'Register', form: 'registerForm', sendToProfile: true},
    'tab-forgot': {url: '/api/profiles/v1/forgot-password/', label: 'Reset', form: 'forgotForm'}
  }

  function loginDefault () {
    return {
      email: '',
      username: '',
      password: '',
      recaptcha: '',
      registration_code: '',
      mail: true,
      token: ''
    }
  }

  export default {
    name: 'Login',
    data () {
      return {
        resetSent: false,
        loginModel: loginDefault(),
        showTokenPrompt: false,
        loginSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Email',
            model: 'email',
            id: 'login-email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'Password',
            id: 'login-password',
            model: 'password',
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        loginOptions: {
          validateAfterLoad: false,
          validateAfterChanged: false
        },
        forgotSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Username or Email',
            model: 'email',
            id: 'forgot-email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        tokenSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            label: 'Verification Code',
            name: 'token',
            model: 'token'
          }]
        },
        registerSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Username',
            id: 'register-username',
            model: 'username',
            placeholder: '',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Email',
            model: 'email',
            id: 'register-email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'Password',
            id: 'register-password',
            model: 'password',
            min: 8,
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Promo Code',
            model: 'registration_code',
            hint: "If you've been given a promo code, please enter it here!"
          }, {
            type: 'v-checkbox',
            label: 'Keep up to Date',
            hint: 'Keep up to date with the latest news on Artconomy using our mailing list',
            model: 'mail'
          }, {
            type: 'recaptcha',
            model: 'recaptcha',
            label: "Prove you're human",
            id: 'register-recaptcha',
            required: true,
            featured: true,
            siteKey: recaptchaSiteKey,
            validator: VueFormGenerator.validators.string
          }]
        }
      }
    },
    methods: {
      loginHandler (response) {
        setCookie('csrftoken', response.csrftoken)
        setCookie('authtoken', response.authtoken)
        if (this.$route.query.next) {
          if (this.$route.query.next === '/') {
            this.$root.$loadUser(this.sendToProfile)
            return
          }
          this.$root.$loadUser(this.$router.push(this.$route.query.next))
        } else if (this.tab.sendToProfile) {
          this.$root.$loadUser(this.sendToProfile)
        } else {
          this.$root.$loadUser()
          this.$router.push({'name': 'Home'})
        }
      },
      sendToProfile () {
        this.$root.$loadUser((response) => {this.$router.push({name: 'Profile', params: {username: response.username}, query: {editing: true}})})
      },
      logoutHandler () {
        this.$root.user = {}
        this.$router.push({'name': 'Home'})
        this.$root.userCache = {}
      },
      loginFailure (response) {
        let form = this.$refs[this.tab.form]
        if (response.responseJSON && response.responseJSON.token && response.responseJSON.token.length && !this.showTokenPrompt) {
          setErrors(this.$refs.tokenForm, {})
          this.showTokenPrompt = true
          return
        } else if (this.showTokenPrompt) {
          setErrors(this.$refs.tokenForm, response.responseJSON)
        }
        setErrors(form, response.responseJSON)
      },
      forgotHandler (response) {
        this.resetSent = true
        this.showTokenPrompt = false
      },
      sendLogin () {
        artCall(
          this.tab.url,
          'POST',
          this.loginModel,
          this.successHandler,
          this.loginFailure
        )
      }
    },
    computed: {
      tab: function () {
        return TAB_MAP[this.loginTab]
      },
      loginTab: paramHandleMap('tabName'),
      successHandler () {
        if (this.loginTab === 'tab-forgot') {
          return this.forgotHandler
        } else {
          return this.loginHandler
        }
      }
    },
    watch: {
      showTokenPrompt (newVal) {
        if (newVal) {
          this.$nextTick(() => {
            document.getElementById('field-token').focus()
          })
        } else {
          setErrors(this.$refs.tokenForm, {})
        }
      }
    },
    created () {
      window.login = this
    }
  }
</script>