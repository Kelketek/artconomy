<template>
  <div class="container" id="navbar">
    <b-navbar toggleable type="dark" class="fixed-top" variant="primary">

      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-navbar-brand to="/"><img src="/static/images/logo.svg" class="header-logo"/><div class="logo-header-text">rtconomy</div></b-navbar-brand>

      <b-collapse is-nav id="nav_collapse">

        <b-navbar-nav v-if="viewer !== null && viewer.username">
          <b-nav-item :to="{name: 'Characters', params: {username: viewer.username}}">Characters</b-nav-item>
          <b-nav-item :to="{name: 'Orders', params: {username: viewer.username}}">Orders</b-nav-item>
          <b-nav-item :to="{name: 'Sales', params: {username: viewer.username}}">Sales</b-nav-item>
          <b-nav-item v-if="viewer.is_staff" :to="{name: 'Cases', params: {username: viewer.username}}">Cases</b-nav-item>
          <b-nav-item :to="{name: 'Store', params: {username: viewer.username}}">Sell</b-nav-item>
        </b-navbar-nav>


        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto" v-if="viewer !== null">
          <div class="form-inline">
            <input class="mr-sm-2 form-control form-control-sm" type="text" v-model="query" @input="performSearch" @keydown.enter="performSearch" placeholder="Search"/>
          </div>
          <!-- Navbar dropdowns -->
          <b-nav-item v-if="viewer.username" :to="{name: 'Profile', params: {username: viewer.username}}">
            <span class="nav-login-item">
              <img style="height:1.5rem" :src="viewer.avatar_url"> {{ viewer.username }}
            </span>
          </b-nav-item>
          <ac-patchbutton v-if="viewer.username && viewer.rating > 0" :url="`/api/profiles/v1/account/${this.viewer.username}/settings/`" :classes="{'btn-sm': true, 'm-0': true}" name="sfw_mode" v-model="viewer.sfw_mode" true-text="NSFW" true-variant="success" false-text="SFW" />
          <b-nav-item class="mr-3" v-if="viewer.username" :to="{name: 'Notifications'}">
            <span><i class="fa fa-bell"></i><div class="notification-count" v-if="unread">
              <span v-if="unread < 999">{{unread}}</span>
              <span v-else>*</span>
            </div></span>
          </b-nav-item>
          <b-nav-item-dropdown v-if="viewer.username" text="<i class='fa fa-ellipsis-h'></i>" right>
            <b-dropdown-item :to="{name: 'Settings', params: {username: viewer.username}}"><i
              class="fa fa-gear"></i> Settings</b-dropdown-item>
            <b-dropdown-item v-if="viewer.username" @click.prevent="logout()">Signout</b-dropdown-item>
          </b-nav-item-dropdown>
          <b-nav-item :to="{name: 'Login'}" v-else>
            <span class="nav-login-item">Login</span>
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<style>
  .header-logo {
    height: 1.5rem;
    margin-top: -.20rem;
  }
  .notification-count {
    background-color: #fa3e3e;
    color: white;
    position: absolute;
    display: inline-block;
    font-size: 1rem;
    line-height: 1rem;
    border-radius: 2px;
    padding: 1px 3px
  }
  .logo-header-text {
    margin-left: -.35rem;
    display: inline-block;
  }
</style>

<script>
  import { artCall, EventBus } from '../lib'
  import AcPatchbutton from './ac-patchbutton'

  export default {
    components: {AcPatchbutton},
    name: 'NavBar',
    data () {
      let data = {
        loopNotifications: false,
        unread: 0,
        queryData: []
      }
      if (this.$route.name === 'Search') {
        data.queryData = this.$route.query.q || []
        if (!Array.isArray(data.queryData)) {
          data.queryData = [data.queryData]
        }
      }
      return data
    },
    computed: {
      query: {
        get () {
          return this.queryData.join(' ')
        },
        set (value) {
          this.queryData = value.split(' ')
        }
      }
    },
    methods: {
      performSearch () {
        let query = []
        for (let val of this.queryData) {
          if (val !== '') {
            query.push(val)
          }
        }
        this.$router.history.push({name: 'Search', query: {q: query}})
      },
      setNotificationStats (response) {
        if (this.loopNotifications) {
          this.unread = response.count
          this.$setTimer('getUnreadNotifications', this.monitorNotifications, 30000)
        }
      },
      monitorNotifications () {
        if (this.loopNotifications) {
          artCall('/api/profiles/v1/data/notifications/?unread=1&size=0',
            'GET', undefined, this.setNotificationStats,
            () => { this.$setTimer('getUnreadNotifications', this.monitorNotifications, 30000) })
        }
      },
      logoutHandler () {
        this.$root.user = {}
        this.$router.push({'name': 'Home'})
        this.$root.userCache = {}
      },
      logout () {
        artCall(
          '/api/profiles/v1/logout/',
          'POST',
          undefined,
          this.logoutHandler
        )
      }
    },
    watch: {
      viewer (newValue) {
        if (newValue && newValue.username) {
          if (!this.loopNotifications) {
            this.loopNotifications = true
            this.monitorNotifications()
          }
        } else {
          this.loopNotifications = false
        }
      }
    },
    created () {
      EventBus.$on('notifications-updated', this.monitorNotifications)
    },
    destroyed () {
      EventBus.$off('notifications-updated', this.monitorNotifications)
    }
  }
</script>
