<!--suppress HtmlUnknownTarget -->
<template>
  <div>
    <v-navigation-drawer
        fixed
        clipped
        v-model="drawer"
        app
        v-if="viewer && !iFrame && fullInterface && !prerendering"
    >
      <ac-nav-links :subject-handler="viewerHandler" :is-logged-in="isLoggedIn" :is-registered="isRegistered" :is-superuser="isSuperuser" :is-staff="isStaff" v-model="drawer" />
      <v-bottom-nav
      >
        <v-btn
            flat
            href="https://twitter.com/ArtconomyArt/"
            rel="nofollow"
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
          href="https://t.me/Artconomy"
          target="_blank"
          rel="nofollow"
          >
          <span>Telegram</span>
          <v-icon medium>fa-telegram</v-icon>
        </v-btn>
        <v-btn
            flat
            @click.capture.prevent="showSupport"
            to="#"
            class="support-button"
        >
          <span>Support</span>
          <v-icon medium>contact_support</v-icon>
        </v-btn>
      </v-bottom-nav>
    </v-navigation-drawer>
    <v-toolbar
        color="secondary"
        dense
        fixed
        clipped-left
        app
        dark
        :scroll-off-screen="$vuetify.breakpoint.mdAndDown"
        :scroll-threshold="150"
        v-if="!iFrame"
    >
      <v-toolbar-side-icon v-if="viewer && fullInterface && !prerendering" @click.stop="drawer = !drawer"/>
      <v-layout hidden-xs-only>
        <v-toolbar-title class="mr-5 align-center hide-sm hide-xs">
          <v-btn flat to="/">
            <img src="/static/images/logo.svg" class="header-logo" alt="A"/>
            <div class="title">rtconomy</div>
          </v-btn>
        </v-toolbar-title>
      </v-layout>
      <v-layout hidden-sm-and-up row v-if="isLoggedIn">
        <v-toolbar-title class="align-center">
          <v-btn flat to="/" icon>
            <img src="/static/images/logo.svg" class="header-logo" alt="Artconomy"/>
          </v-btn>
        </v-toolbar-title>
      </v-layout>
      <v-spacer></v-spacer>
      <v-layout hidden-sm-and-down row justify-center>
        <!--suppress CheckEmptyScriptTag -->
        <ac-bound-field
            :field="searchForm.fields.q"
            placeholder="Search..."
            single-line
            @keyup="runSearch"
            append-icon="search"
            @click:append="() => {}"
            color="white"
            hide-details
            v-if="fullInterface"
        />
      </v-layout>
      <v-spacer></v-spacer>
      <v-btn
          class="hidden-xs-only"
          v-if="viewer && viewer.rating > 0 && fullInterface"
          v-model="sfwMode.model"
          :color="sfwMode.model? 'blue' : 'black'"
          @click="sfwMode.model = !sfwMode.model"
      ><span v-if="!sfwMode.model">N</span>SFW
      </v-btn>
      <v-toolbar-items v-if="fullInterface">
        <v-btn flat class="hidden-md-and-up px-1" icon :to="{name: 'SearchProducts'}">
          <v-icon large>search</v-icon>
        </v-btn>
        <v-btn icon v-if="isRegistered" @click="notificationLoad" class="notifications-button">
          <v-badge overlap right color="red">
            <span slot="badge" v-if="counts.count && counts.count < 1000">{{counts.count}}</span>
            <span slot="badge" v-else-if="counts.count > 999">*</span>
            <v-icon large>notifications</v-icon>
          </v-badge>
        </v-btn>
        <v-btn class="nav-login-item" flat v-if="isRegistered"
               :to="profileRoute">
          <v-avatar size="32px">
            <img :src="viewer.avatar_url" :alt="viewer.username">
          </v-avatar>
          <div style="padding-left: 1rem;" v-if="isLoggedIn">{{ viewer.username }}</div>
        </v-btn>
        <v-btn v-else-if="viewer" class="nav-login-item" flat :to="loginLink">Login</v-btn>
        <v-btn v-else class="nav-login-item"/>
      </v-toolbar-items>
    </v-toolbar>
  </div>
</template>

<style>
  .header-logo {
    height: 1.75rem;
    vertical-align: middle;
  }

  .title {
    display: inline-block;
    vertical-align: middle;
  }

</style>

<script lang="ts">
import {makeQueryParams} from '@/lib'
import Viewer from '../../mixins/viewer'
import Component, {mixins} from 'vue-class-component'
import {Watch} from 'vue-property-decorator'
import AcSettingNav from './AcSettingNav.vue'
import {User} from '@/store/profiles/types/User'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {FormController} from '@/store/forms/form-controller'
import Nav from '@/mixins/nav'
import {State} from 'vuex-class'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'

const startValue = localStorage.getItem('drawerOpen')
let initDrawerValue: boolean|null = null
/* istanbul ignore next */
if (startValue !== null) {
  initDrawerValue = JSON.parse(startValue) as boolean
}
  @Component({
    components: {AcNavLinks, AcBoundField, AcPatchField, AcSettingNav},
  })
export default class NavBar extends mixins(Viewer, Nav) {
    @State('iFrame') public iFrame!: boolean
    public drawerStore: null|boolean = null
    public searchForm: FormController = null as unknown as FormController
    public prerendering = false

    public get loginLink() {
      if (this.$route.name === 'Login') {
        return {name: 'Login', params: {tabName: 'login'}}
      }
      return {name: 'Login', params: {tabName: 'login'}, query: {next: this.$route.path}}
    }

    public runSearch() {
      if (this.$route.name && (this.$route.name.indexOf('Search') !== -1)) {
        return
      }
      this.$router.push({name: 'SearchProducts', query: makeQueryParams(this.searchForm.rawData)})
    }

    public created() {
      this.prerendering = Boolean(window.PRERENDERING || 0)
      this.searchForm = this.$getForm('search')
      if (this.$vuetify.breakpoint.mdAndDown) {
        // Never begin with the drawer open on a small screen.
        this.drawer = false
      } else {
        this.drawer = initDrawerValue
      }
    }

    public notificationLoad() {
      if (['CommunityNotifications', 'SalesNotifications'].indexOf(this.$route.name + '') !== -1) {
        this.$router.replace({name: 'Reload', params: {path: this.$route.path}})
      } else {
        this.$router.push({name: 'CommunityNotifications'})
      }
    }

    public showSupport() {
      this.$store.commit('supportDialog', true)
    }

    @Watch('isRegistered')
    public viewerUpdate(val: boolean) {
      if (val) {
        this.$store.dispatch('notifications/startLoop').then()
      } else {
        this.$store.dispatch('notifications/stopLoop').then()
      }
    }

    public get profileRoute() {
      const viewer = this.viewer as User
      if (viewer.artist_mode) {
        return {name: 'Products', params: {username: viewer.username}}
      }
      return {name: 'Profile', params: {username: viewer.username}}
    }

    @Watch('drawer', {immediate: true})
    public defaultDrawer(val: null|boolean) {
      if (val === null) {
        this.drawer = this.$vuetify.breakpoint.lgAndUp
      }
    }

    public get sfwMode() {
      return this.viewerHandler.user.patchers.sfw_mode
    }

    public get drawer() {
      return this.drawerStore
    }

    public set drawer(val: boolean|null) {
      if (val === null) {
        localStorage.removeItem('drawerOpen')
        this.drawerStore = null
        return
      }
      localStorage.setItem('drawerOpen', val + '')
      this.drawerStore = val
    }

    public get counts() {
      return this.$store.state.notifications.stats
    }

    public destroyed() {
      this.$store.dispatch('notifications/stopLoop').then()
    }
}
</script>
