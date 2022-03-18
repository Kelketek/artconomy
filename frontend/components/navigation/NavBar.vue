<!--suppress HtmlUnknownTarget -->
<template>
  <div class="main-navigation">
    <v-navigation-drawer
        fixed
        clipped
        v-model="navSettings.patchers.drawer.model"
        app
        width="300"
        v-if="viewer && !iFrame && fullInterface && !prerendering"
    >
      <v-container fluid class="pa-0 fill-height">
        <v-row no-gutters>
          <v-col cols="12">
            <ac-nav-links :subject-handler="viewerHandler" :is-logged-in="isLoggedIn" :is-registered="isRegistered" :is-superuser="isSuperuser" :is-staff="isStaff" v-model="navSettings.patchers.drawer.model" />
          </v-col>
        </v-row>
        <v-spacer />
        <v-bottom-navigation
          style="height: auto"
        >
          <v-btn
            text
            href="https://twitter.com/ArtconomyArt/"
            rel="nofollow noopener"
            target="_blank"
            :class="{'phone-padding': $vuetify.breakpoint.smAndDown, 'pb-2': $vuetify.breakpoint.mdAndUp}"
            class="pt-2"
          >
            <span>Twitter</span>
            <v-icon medium>fa-twitter</v-icon>
          </v-btn>
          <v-btn
            text
            href="https://artconomy.com/blog/"
            target="_blank"
            :class="{'phone-padding': $vuetify.breakpoint.smAndDown, 'pb-2': $vuetify.breakpoint.mdAndUp}"
            class="pt-2"
          >
            <span>Blog</span>
            <v-icon medium>edit</v-icon>
          </v-btn>
          <v-btn
            text
            href="https://discord.gg/4nWK9mf"
            target="_blank"
            rel="nofollow noopener"
            :class="{'phone-padding': $vuetify.breakpoint.smAndDown, 'pb-2': $vuetify.breakpoint.mdAndUp}"
            class="pt-2"
          >
            <span>Discord</span>
            <v-icon medium>{{discordPath}}</v-icon>
          </v-btn>
          <v-btn
            text
            @click.capture.prevent="showSupport"
            to="#"
            class="support-button pt-2"
            :class="{'phone-padding': $vuetify.breakpoint.smAndDown, 'pb-2': $vuetify.breakpoint.mdAndUp}"
          >
            <span>Feedback</span>
            <v-icon medium>contact_support</v-icon>
          </v-btn>
        </v-bottom-navigation>
      </v-container>
    </v-navigation-drawer>
    <v-app-bar
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
      <v-app-bar-nav-icon v-if="viewer && fullInterface && !prerendering" @click.stop="navSettings.patchers.drawer.model = !navSettings.patchers.drawer.model" name="Main Menu"/>
      <v-row no-gutters class="hidden-xs-only" >
        <v-toolbar-title class="mr-5 align-center hide-sm hide-xs">
          <v-btn text to="/">
            <img src="/static/images/logo.svg" class="header-logo" alt="A"/>
            <div class="title">rtconomy</div>
          </v-btn>
        </v-toolbar-title>
      </v-row>
      <v-row no-gutters class="hidden-sm-and-up"  v-if="isLoggedIn">
        <v-toolbar-title class="align-center">
          <v-btn text to="/" icon>
            <img src="/static/images/logo.svg" class="header-logo" alt="Artconomy"/>
          </v-btn>
        </v-toolbar-title>
      </v-row>
      <v-spacer />
      <v-row no-gutters class="hidden-sm-and-down"  justify="center">
        <!--suppress CheckEmptyScriptTag -->
        <ac-bound-field
            :field="searchForm.fields.q"
            placeholder="Search..."
            single-line
            @keyup="runSearch"
            prepend-icon="search"
            @click:append="runSearch"
            color="white"
            hide-details
            field-id="nav-bar-search"
            v-if="fullInterface"
        />
      </v-row>
      <v-spacer />
      <v-card class="px-2 py-1 hidden-xs-only"
              :color="sfwMode.model? 'blue darken-3' : 'black'"
              v-if="viewer && viewer.rating > 0 && fullInterface"
      >
        <v-switch
          v-model="sfwMode.model"
          @click="sfwMode.model = !sfwMode.model"
          label="SFW"
          color="blue lighten-1"
          :hide-details="true"
        >
        </v-switch>
      </v-card>
      <v-toolbar-items v-if="fullInterface">
        <v-btn text class="hidden-md-and-up px-1" icon :to="{name: 'SearchProducts'}" aria-label="Search">
          <v-icon large>search</v-icon>
        </v-btn>
        <v-btn icon v-if="isRegistered" @click="notificationLoad" class="notifications-button">
          <v-badge overlap right color="red" :value="counts.count">
            <template v-slot:badge>
              <span slot="badge" v-if="counts.count && counts.count < 1000">{{counts.count}}</span>
              <span slot="badge" v-else>*</span>
            </template>
            <v-icon large>notifications</v-icon>
          </v-badge>
        </v-btn>
        <v-btn class="nav-login-item" text v-if="isRegistered"
               :to="profileRoute">
          <v-avatar size="32px">
            <img :src="viewer.avatar_url" :alt="viewer.username">
          </v-avatar>
          <div style="padding-left: 1rem;" v-if="isLoggedIn">{{ viewer.username }}</div>
        </v-btn>
        <v-btn v-else-if="viewer" class="nav-login-item" text :to="loginLink">Login</v-btn>
        <v-btn v-else class="nav-login-item" aria-label="Login button loading."/>
      </v-toolbar-items>
    </v-app-bar>
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

  .phone-padding {
    padding-bottom: 80px !important;
  }

</style>

<script lang="ts">
import {makeQueryParams, initDrawerValue} from '@/lib/lib'
import Viewer from '../../mixins/viewer'
import Component, {mixins} from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import AcSettingNav from './AcSettingNav.vue'
import {User} from '@/store/profiles/types/User'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {FormController} from '@/store/forms/form-controller'
import Nav from '@/mixins/nav'
import {State} from 'vuex-class'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'
import {mdiDiscord} from '@mdi/js'
import PrerenderMixin from '@/mixins/PrerenderMixin'
import {SingleController} from '@/store/singles/controller'
import {NavSettings} from '@/types/NavSettings'

@Component({
  components: {AcNavLinks, AcBoundField, AcPatchField, AcSettingNav},
})
export default class NavBar extends mixins(Viewer, Nav, PrerenderMixin) {
  @State('iFrame') public iFrame!: boolean
  public drawerStore: null|boolean = null
  public searchForm: FormController = null as unknown as FormController
  public navSettings = null as unknown as SingleController<NavSettings>

  @Prop({default: initDrawerValue})
  public initialState!: null|boolean

  public discordPath = mdiDiscord

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
    this.searchForm = this.$getForm('search')
    let drawer: boolean
    if (this.$vuetify.breakpoint.mdAndDown) {
      // Never begin with the drawer open on a small screen.
      drawer = false
    } else {
      if (this.initialState === null) {
        drawer = this.$vuetify.breakpoint.lgAndUp
      } else {
        drawer = this.initialState
      }
    }
    this.navSettings = this.$getSingle('navSettings', {
      endpoint: '#',
      x: {drawer},
    })
    this.updateStorage(drawer)
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

  @Watch('navSettings.patchers.drawer.model')
  public updateStorage(val: boolean | null) {
    if (val === null) {
      val = this.$vuetify.breakpoint.lgAndUp
      this.navSettings.patchers.drawer.model = val
    }
    localStorage.setItem('drawerOpen', val + '')
  }

  public get profileRoute() {
    const viewer = this.viewer as User
    return {name: 'AboutUser', params: {username: viewer.username}}
  }

  public get sfwMode() {
    return this.viewerHandler.user.patchers.sfw_mode
  }

  public get counts() {
    return this.$store.state.notifications.stats
  }

  public destroyed() {
    this.$store.dispatch('notifications/stopLoop').then()
  }
}
</script>
