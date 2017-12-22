<template>
  <div class="container" id="navbar">
    <b-navbar toggleable type="dark" class="fixed-top" variant="primary">

      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-navbar-brand to="/"><img src="/static/images/logo.svg" class="header-logo"/><div class="logo-header-text">rtconomy</div></b-navbar-brand>

      <b-collapse is-nav id="nav_collapse">

        <b-navbar-nav v-if="user !== null && user.username">
          <b-nav-item :to="{name: 'Characters', params: {'username': user.username}}">Characters</b-nav-item>
          <b-nav-item disabled>Orders</b-nav-item>
        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto" v-if="user !== null">
          <!-- Navbar dropdowns -->
          <b-nav-item v-if="user.username" :to="{name: 'Profile', params: {username: user.username}}">
            <span class="nav-login-item">
              <img style="height:1.5rem" :src="user.avatar_url"> {{ user.username }}
            </span>
          </b-nav-item>
          <ac-patchbutton v-if="user.username && user.rating > 0" :url="`/api/profiles/v1/${this.user.username}/settings/`" :classes="{'btn-sm': true, 'm-0': true}" name="sfw_mode" v-model="user.sfw_mode" true-text="NSFW" true-variant="success" false-text="SFW"></ac-patchbutton>
          <b-nav-item v-if="user.username" :to="{name: 'Notifications'}">
            <span><i class="fa fa-bell"></i></span>
          </b-nav-item>
          <b-nav-item-dropdown v-if="user.username" text="<i class='fa fa-ellipsis-h'></i>" right>
            <b-dropdown-item :to="{name: 'Settings', params: {username: user.username}}"><i
              class="fa fa-gear"></i> Settings</b-dropdown-item>
            <b-dropdown-item v-if="user.username" @click.prevent="logout()">Signout</b-dropdown-item>
          </b-nav-item-dropdown>
          <b-nav-item v-else @click="$refs.loginModal.show()">
            <span class="nav-login-item">Login</span>
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <form>
      <b-modal
        ref="loginModal" id="loginModal" class="inverse"
      >
        <b-tabs class="inverse" v-model="loginTab">
          <b-tab title="Login" id="loginTab">
            <div class="pt-2"></div>
            <vue-form-generator id="loginForm" ref="loginForm" :schema="loginSchema" :model="loginModel"
                                :options="loginOptions"></vue-form-generator>
          </b-tab>
          <b-tab title="Register" id="registerTab">
            <div class="pt-2"></div>
            <vue-form-generator id="registerForm" ref="registerForm" :schema="registerSchema" :model="loginModel"
                                :options="loginOptions"></vue-form-generator>
          </b-tab>
        </b-tabs>
        <div slot="modal-footer">
          <b-button @click="$refs.loginModal.hide()" id="loginCancel">Cancel</b-button>
          <b-button type="submit" id="loginSubmit" variant="primary" @click.prevent="sendLogin">
            {{ tab.label }}
          </b-button>
        </div>
        <div slot="modal-header"></div>
      </b-modal>
    </form>
  </div>
</template>

<style>
  .header-logo {
    height: 1.5rem;
    margin-top: -.20rem;
  }
  .logo-header-text {
    margin-left: -.35rem;
    display: inline-block;
  }
</style>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import { artCall, setErrors, setCookie } from '../lib'
  import AcPatchbutton from './ac-patchbutton'

  const TAB_MAP = {
    0: {url: '/api/profiles/v1/login/', label: 'Login', form: 'loginForm'},
    1: {url: '/api/profiles/v1/register/', label: 'Register', form: 'registerForm'}
  }

  function loginDefault () {
    return {
      email: '',
      username: '',
      password: ''
    }
  }

  export default {
    components: {AcPatchbutton},
    name: 'NavBar',
    props: ['user'],
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
          }]
        },
        loginOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        loginTab: 0
      }
    },
    computed: {
      tab: function () {
        return TAB_MAP[this.loginTab]
      }
    },
    methods: {
      sendLogin () {
        artCall(
          this.tab.url,
          'POST',
          this.loginModel,
          this.loginHandler,
          this.loginFailure
        )
      },
      loginHandler (response) {
        setCookie('csrftoken', response.csrftoken)
        this.$refs.loginModal.hide()
        this.loginTab = 0
        this.$root.loadUser(true)
        this.loginModel = loginDefault()
      },
      logoutHandler () {
        this.$root.user = {}
        this.$router.push({'name': 'Home'})
        this.$root.usercache = {}
      },
      loginFailure (response) {
        let form = this.$refs[this.tab.form]
        console.log(response.responseJSON)
        setErrors(form, response.responseJSON)
      },
      logout () {
        artCall(
          '/api/profiles/v1/logout/',
          'POST',
          undefined,
          this.logoutHandler
        )
      }
    }
  }
</script>
