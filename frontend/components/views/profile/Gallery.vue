<template>
  <v-container fluid class="pa-0" :id="id">
    <v-card>
      <ac-tab-nav :items="items" label="Select gallery" />
    </v-card>
    <v-row class="d-flex align-content-end" v-if="controls">
      <v-col class="text-center mt-3 text-md-right">
        <v-btn @click="showUpload = true" v-if="artPage || collectionPage" color="green" class="mx-2" variant="flat">
          <v-icon left icon="mdi-plus"/>
          New Submission
        </v-btn>
        <v-btn @click="managing = !managing" color="primary" variant="flat">
          <v-icon left icon="mdi-cog"/>
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
    </v-row>
    <router-view class="pa-0 pt-3" v-if="subject" :key="`${username}-${String($route.name)}`"></router-view>
    <ac-new-submission
        ref="newSubmissionForm"
        :username="username"
        v-model="showUpload"
        @success="postAdd"
        :allow-multiple="true"
    />
  </v-container>
</template>

<style>
.gallery-container {
  position: relative;
}
</style>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {ListController} from '@/store/lists/controller.ts'
import Submission from '@/types/Submission.ts'
import {flatten, genId} from '@/lib/lib.ts'
import AcTab from '@/components/AcTab.vue'
import Upload from '@/mixins/upload.ts'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import ArtistTag from '@/types/ArtistTag.ts'
import {defineAsyncComponent} from 'vue'
const AcNewSubmission = defineAsyncComponent(() => import('@/components/AcNewSubmission.vue'))

@Component({
  components: {
    AcTabNav,
    AcNewSubmission,
    AcTab,
  },
})
class Gallery extends mixins(Subjective, Upload) {
  public art = null as unknown as ListController<ArtistTag>
  public collection = null as unknown as ListController<Submission>
  public id = genId()

  @Watch('showUpload')
  public setOwnership() {
    (this.$refs.newSubmissionForm as any).isArtist = this.artPage
  }

  public get managing() {
    return String(this.$route.name).includes('Manage')
  }

  public postAdd(submission: Submission) {
    const routeName = String(this.$route.name) + ''
    for (const group of (['collection', 'art'] as Array<keyof Gallery & string>)) {
      if (routeName.toLowerCase().includes(group) && this[group].currentPage === 1) {
        this[group].unshift(submission)
      }
    }
  }

  public set managing(val) {
    const route = {
      name: String(this.$route.name) + '',
      params: this.$route.params,
      query: this.$route.query,
    }
    if (val && !this.managing) {
      route.name = `Manage${route.name}`
    } else if (!val && this.managing) {
      for (const group of (['collection', 'art'] as Array<keyof Gallery & string>)) {
        if (route.name.toLowerCase().includes(group)) {
          this[group].get()
        }
      }
      this.collection.get()
      this.art.get()
      route.name = route.name.replace('Manage', '')
    }
    this.$router.replace(route)
  }

  public get items() {
    return [{
      value: {
        name: 'Art',
        params: {username: this.username},
      },
      count: this.art.count,
      icon: 'mdi-palette',
      title: `${this.possessive} Art`,
    }, {
      value: {
        name: 'Collection',
        params: {username: this.username},
      },
      count: this.collection.count,
      icon: 'mdi-image-multiple',
      title: `${this.possessive} Collection`,
    }]
  }

  public get artPage() {
    return this.$route.name === 'Art'
  }

  public get collectionPage() {
    return this.$route.name === 'Collection'
  }

  public get possessive() {
    if (this.username.endsWith('s')) {
      return `${this.username}'`
    } else {
      return `${this.username}'s`
    }
  }

  public created() {
    this.art = this.$getList(`${this.username}-art`, {
      endpoint: `/api/profiles/account/${this.username}/submissions/art/`,
    })
    this.collection = this.$getList(`${flatten(this.username)}-collection`, {
      endpoint: `/api/profiles/account/${this.username}/submissions/collection/`,
    })
    // Conditionally fetch. If we're on these pages, we want to give the paginator a chance to set the page before
    // fetching. Otherwise we want to prefetch in case the user switches tabs.
    if (!this.artPage) {
      this.art.firstRun().then()
    }
    if (!this.collectionPage) {
      this.collection.firstRun().then()
    }
    if (this.$route.name === 'Gallery') {
      this.$router.push({
        name: 'Art',
        params: {username: this.username},
      })
    }
  }
}

export default toNative(Gallery)
</script>
