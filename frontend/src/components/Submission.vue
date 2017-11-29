<template>
  <div class="container">
    <div class="row shadowed" v-if="submission">
      <div class="col-sm-12 character-refsheet-container text-center text-section">
        <img :src="submission.file">
      </div>
      <div class="col-sm-12 col-md-8 text-section pt-3 pl-4">
        <h1>{{ submission.title }}</h1>
        <div v-html="$root.md.render(submission.caption)"></div>
      </div>
      <div class="col-sm-12 col-md-4 text-section pt-3 pl-4">
        <h3>By <router-link :to="{name: 'Profile', params: {username: submission.uploaded_by}}">{{ submission.uploaded_by }}</router-link></h3>
      </div>
      <div class="col-sm-12 text-section mb-2">
        <h2>Featuring</h2>
      </div>
      <ac-character-preview
          v-for="char in submission.characters"
          v-bind:character="char"
          v-bind:expanded="true"
          v-bind:key="char.id"
      >
      </ac-character-preview>
    </div>
    <div class="row shadowed">
      <ac-comment
          v-for="comment in growing"
          :commentobj="comment"
          :key="comment.id"
          :reader="$root.user"
          v-if="growing !== null"
          :nesting="true"
          :toplevel="true"
      >
      </ac-comment>
      <div v-else class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      <div v-if="growing !== null" v-observe-visibility="moreComments"></div>
      <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      <ac-new-comment v-if="(growing !== null && !fetching)" :parent="this" :url="baseURL"></ac-new-comment>
    </div>
  </div>
</template>

<script>
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall } from '../lib'
  import AcCharacterPreview from './ac-character-preview'
  import AcComment from './ac-comment'
  import AcNewComment from './ac-new-comment'
  import Paginated from '../mixins/paginated'

  export default {
    name: 'Home',
    components: {AcCharacterPreview, AcComment, AcNewComment},
    directives: {'observe-visibility': ObserveVisibility},
    mixins: [Paginated],
    data () {
      return {
        submission: null,
        baseURL: `/api/profiles/v1/asset/${this.$route.params.assetID}/comments/`
      }
    },
    methods: {
      populateSubmission (response) {
        this.submission = response
      },
      populateComments (response) {
        this.response = response
        this.growing = response.results
      },
      addComment (comment) {
        this.comments.push(comment)
      },
      moreComments (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      }
    },
    created () {
      this.baseURL = `/api/profiles/v1/asset/${this.$route.params.assetID}/comments/`
      artCall(`/api/profiles/v1/asset/${this.$route.params.assetID}/`, 'GET', undefined, this.populateSubmission)
      artCall(this.baseURL, 'GET', undefined, this.populateComments)
    }
  }
</script>
