<!--suppress JSUnusedLocalSymbols -->
<template>
  <v-layout>
    <v-flex v-if="subject">
      <v-navigation-drawer
          temporary
          v-model="drawer"
          right
          absolute
      >
        <v-list>
          <ac-setting-nav :username="username"></ac-setting-nav>
        </v-list>
      </v-navigation-drawer>
      <v-container>
        <v-toolbar v-if="!isCurrent" color="red">
          <v-toolbar-title>Settings for {{username}}</v-toolbar-title><v-spacer></v-spacer>
          <ac-avatar :username="username" :show-name="false"></ac-avatar>
        </v-toolbar>
        <v-toolbar color="secondary">
          <v-toolbar-title>{{$route.name}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn color="primary" id="more-settings-button" @click="drawer=true">More Settings...</v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <router-view></router-view>
      </v-container>
    </v-flex>
    <ac-loading-spinner v-else></ac-loading-spinner>
  </v-layout>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {paramHandleMap} from '@/lib'
import Subjective from '@/mixins/subjective'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcAvatar from '@/components/AcAvatar.vue'

  @Component({
    components: {AcAvatar, AcLoadingSpinner, AcSettingNav},
  })
export default class Settings extends mixins(Subjective) {
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
