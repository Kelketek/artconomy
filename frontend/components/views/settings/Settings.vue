<!--suppress JSUnusedLocalSymbols -->
<template>
  <v-row no-gutters>
    <v-col v-if="subject">
      <v-navigation-drawer
          temporary
          v-model="drawer"
          right
          absolute
          width="300"
      >
        <v-list>
          <ac-setting-nav :username="username" />
        </v-list>
      </v-navigation-drawer>
      <v-container>
        <v-toolbar v-if="!isCurrent" color="red">
          <v-toolbar-title>Settings for <ac-link :to="profileLink(subject)">{{username}}</ac-link></v-toolbar-title><v-spacer />
          <ac-avatar :username="username" :show-name="false" />
        </v-toolbar>
        <v-toolbar color="secondary">
          <v-toolbar-title>{{$route.name}}</v-toolbar-title>
          <v-spacer />
          <v-toolbar-items>
            <v-btn color="primary" id="more-settings-button" @click="drawer=true">More Settings...</v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <router-view />
      </v-container>
    </v-col>
    <ac-loading-spinner v-else />
  </v-row>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {paramHandleMap, profileLink} from '@/lib/lib'
import Subjective from '@/mixins/subjective'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'

  @Component({
    components: {AcLink, AcAvatar, AcLoadingSpinner, AcSettingNav},
  })
export default class Settings extends mixins(Subjective, Formatting) {
    public privateView = true
    private drawer = false

    @paramHandleMap('tabName', ['subTabName'])
    private tab!: string

    @paramHandleMap('subTabName', undefined, ['tab-purchase', 'tab-disbursement', 'tab-transactions'], 'tab-purchase')
    private paymentTab!: string

    @paramHandleMap('subTabName', undefined, ['tab-authentication', 'tab-two-factor'], 'tab-authentication')
    private credentialsTab!: string

    public created() {
      if (this.$route.name === 'Settings') {
        this.$router.replace({name: 'Options', params: {username: this.username}})
      }
    }
}
</script>

<style scoped>

</style>
