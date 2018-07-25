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
          >
            <v-card>
              <v-card-text>
                <p>
                  This account is protected by Two Factor Authentication. Please use your
                  authentication device to generate a login token.
                </p>
                <vue-form-generator id="tokenForm" ref="tokenForm" :schema="tokenSchema" :model="loginModel"
                                    :options="loginOptions" />
                <div class="text-xs-center">
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
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'Password',
            model: 'password',
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        loginOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        forgotSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Username or Email',
            model: 'email',
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
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'v-text',
            inputType: 'password',
            label: 'Password',
            model: 'password',
            min: 8,
            required: true,
            featured: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'recaptcha',
            model: 'recaptcha',
            label: "Prove you're human",
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
        if (this.tab.sendToProfile) {
          this.$root.$loadUser(true)
        } else if (this.$route.query.next) {
          this.$root.$loadUser()
          this.$router.push(this.$route.query.next)
        } else {
          this.$root.$loadUser()
          this.$router.push({'name': 'Home'})
        }
      },
      logoutHandler () {
        this.$root.user = {}
        this.$router.push({'name': 'Home'})
        this.$root.userCache = {}
      },
      loginFailure (response) {
        let form = this.$refs[this.tab.form]
        if (response.responseJSON.token.length && !this.showTokenPrompt) {
          this.showTokenPrompt = true
          return
        } else if (this.showTokenPrompt) {
          setErrors(this.$refs.tokenForm, response.responseJSON)
        }
        setErrors(form, response.responseJSON)
      },
      forgotHandler (response) {
        this.resetSent = true
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
    created () {
      window.login = this
    }
  }
</script>