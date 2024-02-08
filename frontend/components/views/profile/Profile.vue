<template>
  <v-container>
    <ac-load-section :controller="subjectHandler.user">
      <template v-slot:default>
        <ac-profile-header :username="username" :show-edit="$route.name === 'AboutUser'" :dense="true"/>
        <v-card>
          <ac-tab-nav :items="items" label="See more"/>
        </v-card>
        <router-view class="pa-0" :class="{'pt-3': needsSpace}"/>
      </template>
    </ac-load-section>
  </v-container>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective.ts'
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {flatten} from '@/lib/lib.ts'

@Component({
  components: {
    AcTabNav,
    AcLoadSection,
    AcProfileHeader,
    AcLoadingSpinner,
  },
})
class Profile extends mixins(Subjective) {
  @Watch('subject.artist_mode', {immediate: true})
  public setDefaultRoute() {
    if (!this.subject) {
      return
    }
    if (this.$route.name === 'Profile') {
      this.$router.replace({
        name: 'AboutUser',
        params: {username: this.username},
      })
    }
  }

  @Watch('$route.name')
  public routeNameCheck() {
    this.setDefaultRoute()
  }

  public get needsSpace() {
    return [
      'Gallery', 'Art', 'ManageArt', 'Collection', 'ManageCollection', 'Watchers', 'Watching', 'Watchlists',
    ].indexOf(String(this.$route.name) + '') === -1
  }

  public get items() {
    const items = [
      {
        value: {
          name: 'AboutUser',
          params: {username: this.username},
        },
        icon: 'mdi-account',
        title: 'About',
      },
    ]
    if (this.subject && this.subject.artist_mode) {
      items.push(
          {
            value: {
              name: 'Products',
              params: {username: this.username},
            },
            icon: 'mdi-basket',
            title: 'Products',
          },
      )
    }
    items.push({
      value: {
        name: 'Characters',
        params: {username: this.username},
      },
      icon: 'mdi-account-multiple',
      title: 'Characters',
    }, {
      value: {
        name: 'Gallery',
        params: {username: this.username},
      },
      icon: 'mdi-image-album',
      title: 'Gallery',
    }, {
      value: {
        name: 'Favorites',
        params: {username: this.username},
      },
      icon: 'mdi-heart',
      title: 'Favorites',
    }, {
      value: {
        name: 'Watchlists',
        params: {username: this.username},
      },
      icon: 'mdi-eye',
      title: 'Watchlists',
    })
    return items
  }

  public created() {
    this.subjectHandler.artistProfile.get().catch(this.setError)
    this.$listenForList(`${flatten(this.username)}-products`)
    this.$listenForList(`${flatten(this.username)}-art`)
    this.$listenForList(`${flatten(this.username)}-collection`)
    this.$listenForList(`${flatten(this.username)}-characters`)
    this.$listenForList(`${flatten(this.username)}-journals`)
    this.$listenForForm(`${flatten(this.username)}-newJournal`)
    this.$listenForForm('newUpload')
    this.$listenForProfile('.*')
  }
}

export default toNative(Profile)
</script>
