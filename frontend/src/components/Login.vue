<template>
  <div class="container">
    <div class="row-centered">
      <div class="col-12 col-md-6 col-lg-4 col-centered text-center">
        <form>
          <b-tabs class="inverse" v-model="loginTab">
            <b-tab title="Login" id="loginTab">
              <div class="pt-2"></div>
              <vue-form-generator id="loginForm" ref="loginForm" :schema="loginSchema" :model="loginModel"
                                  :options="loginOptions" />
            </b-tab>
            <b-tab title="Register" id="registerTab">
              <div class="pt-2"></div>
              <vue-form-generator id="registerForm" ref="registerForm" :schema="registerSchema" :model="loginModel"
                                  :options="loginOptions" />
            </b-tab>
          </b-tabs>
          <div>
            <b-button type="submit" id="loginSubmit" variant="primary" @click.prevent="sendLogin">
              {{ tab.label }}
            </b-button>
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
    0: {url: '/api/profiles/v1/login/', label: 'Login', form: 'loginForm'},
    1: {url: '/api/profiles/v1/register/', label: 'Register', form: 'registerForm'}
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