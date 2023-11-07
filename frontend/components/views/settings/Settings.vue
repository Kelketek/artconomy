<!--suppress JSUnusedLocalSymbols -->
<template>
  <ac-load-section :controller="subjectHandler.user">
    <v-navigation-drawer
        temporary
        v-model="drawer"
        right
        absolute
        width="300"
    >
      <v-list>
        <ac-setting-nav :username="username"/>
      </v-list>
    </v-navigation-drawer>
    <v-container>
      <v-toolbar v-if="!isCurrent" color="red" class="settings-nav-toolbar">
        <v-toolbar-title>Settings for
          <ac-link :to="profileLink(subject)">{{username}}</ac-link>
        </v-toolbar-title>
        <v-spacer/>
        <ac-avatar :username="username" :show-name="false"/>
      </v-toolbar>
      <v-toolbar color="secondary" class="settings-nav-toolbar">
        <v-toolbar-title>{{$route.name}}</v-toolbar-title>
        <v-spacer/>
        <v-toolbar-items>
          <v-btn color="primary" id="more-settings-button" @click="drawer=true" variant="flat">More Settings...</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <router-view/>
    </v-container>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({
  components: {
    AcLoadSection,
    AcLink,
    AcAvatar,
    AcLoadingSpinner,
    AcSettingNav,
  },
})
class Settings extends mixins(Subjective, Formatting) {
  public privateView = true
  public drawer = false

  public created() {
    if (this.$route.name === 'Settings') {
      this.$router.replace({
        name: 'Options',
        params: {username: this.username},
      })
    }
  }
}

export default toNative(Settings)
</script>

<style scoped>

</style>
