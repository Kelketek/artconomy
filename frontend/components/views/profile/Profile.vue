<template>
  <v-container>
    <ac-load-section :controller="subjectHandler.user">
      <ac-profile-header :username="username"></ac-profile-header>
      <ac-tab-nav :items="items"></ac-tab-nav>
      <router-view class="pa-0" :class="{'pt-3': needsSpace}"></router-view>
    </ac-load-section>
  </v-container>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import {Watch} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcTabNav from '@/components/navigation/AcTabNav.vue'

  @Component({
    components: {
      AcTabNav,
      AcLoadSection,
      AcProfileHeader,
      AcLoadingSpinner},
  })
export default class Profile extends mixins(Subjective) {
    @Watch('subject.artist_mode', {immediate: true})
  public setDefaultRoute() {
    if (!this.subject) {
      return
    }
    if (this.$route.name === 'Profile') {
      if (this.subject.artist_mode) {
        this.$router.replace({name: 'Products', params: {username: this.username}})
      } else {
        this.$router.replace({name: 'AboutUser', params: {username: this.username}})
      }
    }
  }
    @Watch('$route.name')
    public routeNameCheck() {
      this.setDefaultRoute()
    }
    public get needsSpace() {
      return [
        'Gallery', 'Art', 'Collection', 'Watchers', 'Watching', 'Watchlists',
      ].indexOf(this.$route.name + '') === -1
    }
    public get items() {
      const items = [
        {value: {name: 'AboutUser', params: {username: this.username}}, icon: 'person', text: 'About'},
      ]
      if (this.subject && this.subject.artist_mode) {
        items.push(
          {value: {name: 'Products', params: {username: this.username}}, icon: 'shopping_basket', text: 'Products'}
        )
      }
      items.push({
        value: {name: 'Characters', params: {username: this.username}}, icon: 'people', text: 'Characters',
      }, {
        value: {name: 'Gallery', params: {username: this.username}}, icon: 'image', text: 'Gallery',
      }, {
        value: {name: 'Favorites', params: {username: this.username}}, icon: 'favorite', text: 'Favorites',
      }, {
        value: {name: 'Watchlists', params: {username: this.username}}, icon: 'visibility', text: 'Watchlists',
      })
      return items
    }
    public created() {
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.$listenForList(`${this.username}-products`)
      this.$listenForList(`${this.username}-art`)
      this.$listenForList(`${this.username}-collection`)
      this.$listenForList(`${this.username}-characters`)
      this.$listenForList(`${this.username}-journals`)
      this.$listenForForm(`${this.username}-newJournal`)
      this.$listenForForm(`${this.username}-newSubmission`)
      this.$listenForProfile('.*')
    }
}
</script>