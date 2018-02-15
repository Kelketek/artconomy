<template>
  <div class="container">
    <div class="row-centered">
      <div class="col-12 col-md-6 col-lg-4 col-centered text-xs-center">
        <form>
          <v-tabs class="inverse" v-model="loginTab">
            <v-tab href="#tab-login">
              Login
            </v-tab>
            <v-tab href="#tab-register">
              Register
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="loginTab">
            <v-tab-item id="tab-login">
              <div class="pt-2"></div>
              <vue-form-generator id="loginForm" ref="loginForm" :schema="loginSchema" :model="loginModel"
                                  :options="loginOptions" />
              <v-btn type="submit" color="primary" @click.prevent="sendLogin">
                Login
              </v-btn>
            </v-tab-item>
            <v-tab-item id="tab-register">
              <div class="pt-2"></div>
              <vue-form-generator id="registerForm" ref="registerForm" :schema="registerSchema" :model="loginModel"
                                  :options="loginOptions" />
              <v-btn type="submit" color="primary" @click.prevent="sendLogin">
                Register
              </v-btn>
            </v-tab-item>
          </v-tabs-items>
          <div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import { artCall, recaptchaSiteKey, setCookie, setErrors } from '../lib'

  const TAB_MAP = {
    'tab-login': {url: '/api/profiles/v1/login/', label: 'Login', form: 'loginForm'},
    'tab-register': {url: '/api/profiles/v1/register/', label: 'Register', form: 'registerForm'}
  }

  function loginDefault () {
    return {
      email: '',
      username: '',
      password: '',
      recaptcha: ''
    }
  }

  export default {
    name: 'Login',
    data () {
      return {
        loginModel: loginDefault(),
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
        registerSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Username',
            model: 'username',
            placeholder: '',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Email',
            model: 'email',
            placeholder: 'example@example.com',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.email
          }, {
            type: 'input',
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
        },
        loginTab: 0
      }
    },
    methods: {
      loginHandler (response) {
        setCookie('csrftoken', response.csrftoken)
        setCookie('authtoken', response.authtoken)
        this.loginTab = 0
        this.$root.$loadUser(true)
        this.loginModel = loginDefault()
      },
      logoutHandler () {
        this.$root.user = {}
        this.$router.push({'name': 'Home'})
        this.$root.userCache = {}
      },
      loginFailure (response) {
        let form = this.$refs[this.tab.form]
        setErrors(form, response.responseJSON)
      },
      sendLogin () {
        artCall(
          this.tab.url,
          'POST',
          this.loginModel,
          this.loginHandler,
          this.loginFailure
        )
      }
    },
    computed: {
      tab: function () {
        return TAB_MAP[this.loginTab]
      }
    },
    created () {
      window.login = this
    }
  }
</script>