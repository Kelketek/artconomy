<template>
  <v-container fluid class="pa-0" :id="id">
    <ac-tab-nav :items="items" label="Select gallery"></ac-tab-nav>
    <v-row class="d-none d-md-flex align-content-end" v-if="controls">
      <v-col class="text-right">
        <v-btn @click="showUpload = true" v-if="artPage || collectionPage" color="green" class="mx-2"><v-icon left>add</v-icon>New Submission</v-btn>
        <v-btn @click="managing = !managing" color="primary"><v-icon left>settings</v-icon>
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="d-flex d-md-none" v-if="controls">
      <v-col class="text-center">
        <v-btn @click="managing = !managing" color="primary"><v-icon left>settings</v-icon>
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
    </v-row>
    <router-view class="pa-0 pt-3" v-if="subject" :key="`${username}-${$route.name}`"></router-view>
    <ac-add-button v-model="showUpload" v-if="controls && (artPage || collectionPage)">New Submission</ac-add-button>
    <ac-new-submission
        ref="newSubmissionForm"
        :username="username"
        v-model="showUpload"
        :post-add="postAdd"
        :allow-multiple="true"
    ></ac-new-submission>
  </v-container>
</template>

<style>
  .gallery-container {
    position: relative;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import {FormController} from '@/store/forms/form-controller'
import {flatten, genId, newUploadSchema} from '@/lib/lib'
import AcTab from '@/components/AcTab.vue'
import AcAddButton from '@/components/AcAddButton.vue'
import Upload from '@/mixins/upload'
import AcNewSubmission from '@/components/AcNewSubmission.vue'
import {Watch} from 'vue-property-decorator'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import Editable from '@/mixins/editable'
import ArtistTag from '@/types/ArtistTag'
@Component({
  components: {AcTabNav, AcNewSubmission, AcAddButton, AcTab},
})
export default class Gallery extends mixins(Subjective, Upload) {
  public art: ListController<Submission> = null as unknown as ListController<Submission>
  public collection: ListController<Submission> = null as unknown as ListController<Submission>
  public id = genId()

  @Watch('showUpload')
  public setOwnership() {
    (this.$refs.newSubmissionForm as any).isArtist = this.artPage
  }

  public get managing() {
    return !!this.$route.name?.includes('Manage')
  }

  public postAdd(submission: Submission) {
    const routeName = this.$route.name + ''
    for (const group of (['collection', 'art'] as Array<keyof Gallery>)) {
      if (routeName.toLowerCase().includes(group) && this[group].currentPage === 1) {
        this[group].unshift(submission)
      }
    }
  }

  public set managing(val) {
    const route = {name: this.$route.name + '', params: this.$route.params, query: this.$route.query}
    if (val && !this.managing) {
      route.name = `Manage${route.name}`
    } else if (!val && this.managing) {
      for (const group of (['collection', 'art'] as Array<keyof Gallery>)) {
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
      value: {name: 'Art', params: {username: this.username}},
      count: this.art.count,
      icon: 'palette',
      text: `${this.possessive} Art`,
    }, {
      value: {
        name: 'Collection', params: {username: this.username},
      },
      count: this.collection.count,
      icon: 'collections',
      text: `${this.possessive} Collection`,
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
      endpoint: `/api/profiles/v1/account/${this.username}/submissions/art/`,
    })
    this.collection = this.$getList(`${flatten(this.username)}-collection`, {
      endpoint: `/api/profiles/v1/account/${this.username}/submissions/collection/`,
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
      this.$router.push({name: 'Art', params: {username: this.username}})
    }
  }
}
</script>
