<template>
  <v-container fluid class="pa-0" :id="id">
    <ac-tab-nav :items="items"></ac-tab-nav>
    <router-view class="pa-0 pt-3" v-if="subject" :key="`${username}-${$route.name}`"></router-view>
    <ac-add-button v-model="showUpload" v-if="controls">New Submission</ac-add-button>
    <ac-new-submission ref="newSubmissionForm" :username="username" v-model="showUpload"></ac-new-submission>
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
import {genId, newUploadSchema} from '@/lib'
import AcTab from '@/components/AcTab.vue'
import AcAddButton from '@/components/AcAddButton.vue'
import Upload from '@/mixins/upload'
import AcNewSubmission from '@/components/AcNewSubmission.vue'
import {Watch} from 'vue-property-decorator'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
  @Component({
    components: {AcTabNav, AcNewSubmission, AcAddButton, AcTab},
  })
export default class Gallery extends mixins(Subjective, Upload) {
    public art: ListController<Submission> = null as unknown as ListController<Submission>
    public collection: ListController<Submission> = null as unknown as ListController<Submission>
    public newSubmission: FormController = null as unknown as FormController
    public id = genId()

    @Watch('showUpload')
    public setOwnership() {
      (this.$refs.newSubmissionForm as any).isArtist = this.artPage
    }

    public get items() {
      return [{
        value: {
          name: 'Art', params: {username: this.username}},
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
      this.newSubmission = this.$getForm(`${this.username}-newSubmission`, newUploadSchema(this.subjectHandler.user))
      this.art = this.$getList(`${this.username}-art`, {
        endpoint: `/api/profiles/v1/account/${this.username}/submissions/art/`,
      })
      this.collection = this.$getList(`${this.username}-collection`, {
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
