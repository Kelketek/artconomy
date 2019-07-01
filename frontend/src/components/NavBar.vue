<template>
  <div>
    <v-navigation-drawer
        fixed
        clipped
        v-model="drawer"
        app
        v-if="viewer && viewer.username && notFramed"
    >
      <v-list dense>
        <v-list v-if="viewer && viewer.username">
          <v-list-tile to="/" exact>Home</v-list-tile>
          <v-list-tile :to="{name: 'WhoIsOpen'}">Who's Open?</v-list-tile>
          <v-list-tile :to="{name: 'RecentArt'}">Recent Art</v-list-tile>
          <v-list-tile :to="{name: 'Orders', params: {username: viewer.username}}">Orders</v-list-tile>
          <v-list-tile :to="{name: 'Sales', params: {username: viewer.username}}">Sales</v-list-tile>
          <v-list-tile v-if="viewer.is_staff" :to="{name: 'Cases', params: {username: viewer.username}}">Cases</v-list-tile>
          <v-list-tile :to="{name: 'Store', params: {username: viewer.username}}">My Products</v-list-tile>
          <v-list-tile :to="{name: 'Messages', params: {username: viewer.username}}">Private Messages</v-list-tile>
        </v-list>
        <ac-patchbutton
            class="hidden-sm-and-up"
            v-if="viewer && viewer.username && viewer.rating > 0"
            :url="`/api/profiles/v1/account/${this.viewer.username}/settings/`"
            :classes="{'btn-sm': true, 'm-0': true}"
            name="sfw_mode"
            v-model="viewer.sfw_mode"
            true-text="NSFW"
            true-variant="success"
            false-text="SFW"
            :toggle="true"
            style="padding-left: 16px"
        />
        <v-list-tile class="mt-3" :to="{name: 'Settings', params: {'username': viewer.username}}">
          <v-list-tile-action>
            <v-icon>settings</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Settings</v-list-tile-title>
        </v-list-tile>
        <v-list-tile :to="{name: 'Upgrade'}" v-if="!landscape">
          <v-list-tile-action>
            <v-icon>arrow_upward</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Upgrade!</v-list-tile-title>
        </v-list-tile>
        <v-list-tile :to="{name: 'Referrals', params: {username: viewer.username}}">
          <v-list-tile-action>
            <v-icon>star</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Referrals, Rewards, and Tools!</v-list-tile-title>
        </v-list-tile>
        <v-list-tile :to="{name: 'FAQ'}">
          <v-list-tile-action>
            <v-icon>question_answer</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>FAQ</v-list-tile-title>
        </v-list-tile>
        <v-list-tile @click.prevent="logout()">
          <v-list-tile-action>
            <v-icon>exit_to_app</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Log out</v-list-tile-title>
        </v-list-tile>
        <v-list-tile class="mt-3" :to="{name: 'Policies'}">
          <v-list-tile-action>
            <v-icon>info</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Privacy and Legal</v-list-tile-title>
        </v-list-tile>
      </v-list>
      <v-bottom-nav style="margin-top: -4.5em;"
      >
        <v-btn
            flat
            href="https://twitter.com/ArtconomyArt/"
            target="_blank"
        >
          <span>Twitter</span>
          <v-icon medium>fa-twitter</v-icon>
        </v-btn>
        <v-btn
            flat
            href="https://artconomy.com/blog/"
            target="_blank"
        >
          <span>Blog</span>
          <v-icon medium>edit</v-icon>
        </v-btn>
        <v-btn
            flat
            @click="showSupport"
        >
          <span>Support</span>
          <v-icon medium>contact_support</v-icon>
        </v-btn>
      </v-bottom-nav>
    </v-navigation-drawer>
    <v-toolbar
        color="purple"
        dense
        fixed
        clipped-left
        app
        v-if="notFramed"
    >
      <v-toolbar-side-icon v-if="viewer && viewer.username" @click.stop="drawer = !drawer" />
      <v-layout hidden-xs-only>
        <v-toolbar-title class="mr-5 align-center hide-sm hide-xs">
          <v-btn flat to="/">
            <img src="/static/images/logo.svg" class="header-logo"/><div class="title">rtconomy</div>
          </v-btn>
        </v-toolbar-title>
      </v-layout>
      <v-layout hidden-sm-and-up row v-if="viewer && !viewer.username">
        <v-toolbar-title class="align-center">
          <v-btn flat to="/">
            <img src="/static/images/logo.svg" class="header-logo"/>
          </v-btn>
        </v-toolbar-title>
      </v-layout>
      <v-layout hidden-sm-and-down row justify-center>
        <v-text-field
            placeholder="Search..."
            single-line
            v-model="query"
            @input="performSearch"
            @keyup.enter="performSearch"
            append-icon="search"
            @click:append="() => {}"
            color="white"
            hide-details
        />
      </v-layout>
      <ac-patchbutton
          class="hidden-xs-only"
          v-if="viewer && viewer.username && viewer.rating > 0"
          :url="`/api/profiles/v1/account/${this.viewer.username}/settings/`"
          :classes="{'btn-sm': true, 'm-0': true}"
          name="sfw_mode"
          v-model="viewer.sfw_mode"
          true-text="NSFW"
          true-variant="success"
          false-text="SFW"
      />
      <v-toolbar-items>
        <v-btn flat class="hidden-md-and-up" :to="{name: 'Search'}">
          <v-icon large>search</v-icon>
        </v-btn>
        <v-btn flat v-if="viewer && viewer.username" @click="notificationLoad">
          <v-badge overlap right color="red">
            <span slot="badge" v-if="unread && unread < 1000">{{unread}}</span>
            <span slot="badge" v-else-if="unread > 999">*</span>
            <v-icon large>notifications</v-icon>
          </v-badge>
        </v-btn>
        <v-btn class="nav-login-item" flat v-if="viewer && viewer.username" :to="{name: 'Profile', params: {username: viewer.username}}">
          <v-avatar size="32px">
            <img :src="viewer.avatar_url">
          </v-avatar>
          <div style="padding-left: 1rem;" v-if="viewer && viewer.username">{{ viewer.username }}</div>
        </v-btn>
        <v-btn v-else-if="viewer" class="nav-login-item" flat :to="loginLink">Login</v-btn>
        <v-btn v-else class="nav-login-item" />
      </v-toolbar-items>
    </v-toolbar>
  </div>
</template>

<style>
  .header-logo {
    height: 1.75rem;
    vertical-align: middle;
  }
  .mini-logo {
    height: 100%
  }
  .title {
    display: inline-block;
    vertical-align: middle;
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
</style>

<script>
  import { artCall, EventBus } from '../lib'
  import AcPatchbutton from './ac-patchbutton'
  import Viewer from '../mixins/viewer'
  import AcFormDialog from './ac-form-dialog'

  export default {
    components: {AcFormDialog, AcPatchbutton},
    mixins: [Viewer],
    name: 'NavBar',
    data () {
      let data = {
        loopNotifications: false,
        unread: 0,
        queryData: [],
        drawer: false
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
      },
      loginLink () {
        if (this.$route.name === 'Login') {
          return {name: 'Login', params: {tabName: 'login'}}
        }
        return {name: 'Login', params: {tabName: 'login'}, query: {next: this.$route.path}}
      },
      notFramed () {
        return this.$route.path.indexOf('/iframe/') === -1
      },
    },
    methods: {
      performSearch () {
        let query = []
        for (let val of this.queryData) {
          if (val !== '') {
            query.push(val)
          }
        }
        if (this.$route.name !== 'Search') {
          this.$router.history.push({name: 'Search', params: {tabName: 'products'}})
          return
        }
        let newQuery = {...this.$route.query}
        newQuery.q = query
        this.$router.history.replace({name: 'Search', query: newQuery, params: this.$route.params})
      },
      notificationLoad () {
        if (this.$route.name === 'Notifications') {
          this.$router.replace({name: 'Reload', params: {path: this.$route.path}})
        } else {
          this.$router.push({name: 'Notifications'})
        }
      },
      setNotificationStats (response) {
        if (this.loopNotifications) {
          this.unread = response.count
          EventBus.$emit('notification-count', response)
          this.$setTimer('getUnreadNotifications', this.monitorNotifications, 10000)
        }
      },
      monitorNotifications () {
        if (this.loopNotifications) {
          artCall('/api/profiles/v1/data/notifications/unread/',
            'GET', undefined, this.setNotificationStats,
            () => { this.$setTimer('getUnreadNotifications', this.monitorNotifications, 10000) })
        }
      },
      logoutHandler (response) {
        this.$root.user = response
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
      },
      showSupport () {
        EventBus.$emit('showSupport')
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
      },
      '$route.query.q': function (val) {
        if (val !== undefined) {
          // Not sure why this happens.
          this.queryData = val
        }
      }
    },
    created () {
      // https://stackoverflow.com/questions/3437786/get-the-size-of-the-screen-current-web-page-and-browser-window
      let w = window
      let d = document
      let e = d.documentElement
      let g = d.getElementsByTagName('body')[0]
      let x = w.innerWidth || e.clientWidth || g.clientWidth
      if (x >= 1264) {
        this.drawer = true
      }
      EventBus.$on('notifications-updated', this.monitorNotifications)
    },
    destroyed () {
      EventBus.$off('notifications-updated', this.monitorNotifications)
    }
  }
</script>
