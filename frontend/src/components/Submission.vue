<template>
  <div class="container">
    <div class="row shadowed" v-if="submission">
      <div class="col-sm-12 character-refsheet-container text-center text-section">
        <img :src="submission.file">
      </div>
      <div class="col-sm-12 col-md-8 text-section pt-3 pl-4">
        <ac-patchfield v-model="submission.title" name="title" styleclass="name-edit" :editmode="editing" :url="url"></ac-patchfield>
        <div class="card-block submission-description"><ac-patchfield v-model="submission.caption" name="caption" :multiline="true" :editmode="editing" :url="url"></ac-patchfield></div>
      </div>
      <div class="col-sm-12 col-md-4 text-section pt-3 pl-4">
        <h3>By <router-link :to="{name: 'Profile', params: {username: submission.uploaded_by.username}}">{{ submission.uploaded_by.username }}</router-link></h3>
        <i v-if="controls && !editing" class="ml-2 fa fa-2x fa-lock clickable pull-right" @click="edit"></i>
        <i v-if="controls && editing" class="ml-2 fa fa-2x fa-unlock clickable pull-right" @click="lock"></i>
        <div v-if="controls" class="pull-right">
          <ac-action :button="false"
                     variant="danger" :confirm="true" :success="goBack"
                     :url="`/api/profiles/v1/asset/${submission.id}/`"
                     method="DELETE" class="fg-dark"
          ><i class="fg-light fa fa-trash-o fa-2x"></i>
            <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this submission? This cannot be undone!</div>
          </ac-action>
        </div>
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
      <ac-new-comment v-if="(growing !== null && !fetching)" :parent="this" :url="commentURL"></ac-new-comment>
    </div>
  </div>
</template>

<script>
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall, setMetaContent, textualize } from '../lib'
  import AcCharacterPreview from './ac-character-preview'
  import AcComment from './ac-comment'
  import AcNewComment from './ac-new-comment'
  import Paginated from '../mixins/paginated'
  import Editable from '../mixins/editable'
  import AcPatchfield from './ac-patchfield'

  export default {
    name: 'Home',
    components: {AcCharacterPreview, AcComment, AcNewComment, AcPatchfield},
    directives: {'observe-visibility': ObserveVisibility},
    mixins: [Paginated, Editable],
    data () {
      return {
        submission: null,
        url: `/api/profiles/v1/asset/${this.$route.params.assetID}/`
      }
    },
    computed: {
      controls () {
        return this.submission.uploaded_by.username === this.$root.user.username
      }
    },
    methods: {
      populateSubmission (response) {
        this.submission = response
        this.setMeta()
      },
      setMeta () {
        document.title = `${this.submission.title} -- by ${this.submission.uploaded_by.username}`
        setMetaContent('description', textualize(this.submission.caption).slice(0, 160))
      },
      populateComments (response) {
        this.response = response
        this.growing = response.results
      },
      addComment (comment) {
        this.comments.push(comment)
      },
      goBack () {
        if (this.$router.history.length) {
          this.$router.go(-1)
        } else {
          this.$router.history.push({name: 'Profile', params: {username: this.submission.uploaded_by.username}})
        }
      },
      moreComments (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      }
    },
    created () {
      this.commentURL = `/api/profiles/v1/asset/${this.$route.params.assetID}/comments/`
      artCall(`/api/profiles/v1/asset/${this.$route.params.assetID}/`, 'GET', undefined, this.populateSubmission)
      artCall(this.commentURL, 'GET', undefined, this.populateComments)
    }
  }
</script>
