<template>
  <div class="container">
    <div class="row shadowed" v-if="submission">
      <div class="col-sm-12 character-refsheet-container text-center text-section">
        <ac-asset :asset="submission" thumb-name="gallery" :rating="rating" />
      </div>
      <div class="col-sm-12 col-md-8 text-section pt-3 pl-4">
        <ac-patchfield v-model="submission.title" name="title" styleclass="name-edit" placeholder="Set the title" :editmode="editing" :url="url" />
        <div class="card-block submission-description"><ac-patchfield v-model="submission.caption" name="caption" placeholder="Add a caption" :multiline="true" :editmode="editing" :url="url" /></div>
      </div>
      <div class="col-sm-12 col-md-4 text-section pt-3 pl-4 text-center">
        <div class="info-block" v-if="!ownWork">
          <h4>Added By</h4>
          <ac-avatar :user="submission.uploaded_by" />
        </div>
        <div v-if="submission.artist" class="info-block">
          <h4>Artist</h4>
          <ac-avatar :user="submission.artist" />
        </div>
        <div>
          <ac-patchdropdown v-model="submission.rating" :editmode="editing" :options="ratingsShort()" :url="url" name="rating" />
          <ac-action v-if="editing" :url="url" method="PATCH" :send="{private: !submission.private}" :success="populateSubmission">
            <span v-if="submission.private"><i class="fa fa-eye-slash"></i> Hide submission</span>
            <span v-else><i class="fa fa-eye"></i> Unhide submission</span>
          </ac-action>
          <div v-else-if="controls" class="text-center">
            <span v-if="submission.private"><i class="fa fa-eye"></i> Submission is public</span>
            <span v-else><i class="fa fa-eye-slash"></i> Submission is private</span>
          </div>
          <ac-action :url="`${url}favorite/`" :success="populateSubmission">
            <span v-if="submission.favorite"><i class="fa fa-heart-o"></i> Remove from Favorites ({{ submission.favorite_count }})</span>
            <span v-else><i class="fa fa-heart"></i> Add to Favorites ({{ submission.favorite_count }})</span>
          </ac-action>
        </div>
        <p v-if="controls && submission.order" class="mb-0">
          From <router-link :to="{name: 'Order', params: {orderID: submission.order, username: submission.uploaded_by.username}}">Order {{submission.order}}</router-link>
        </p>
        <p v-if="(submission.order && submission.artist.username === viewer.username ) || controls && (submission.order)" class="mb-0">
          From <router-link :to="{name: 'Sale', params: {orderID: submission.order, username: submission.artist.username}}">Sale {{submission.order}}</router-link>
        </p>
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
          :character="char"
          :expanded="true"
          :key="char.id"
          :remove-url="`${url}tag-characters/`"
          :removable="(char.user.username === viewer.username) || controls"
          :callback="populateSubmission"
      >
      </ac-character-preview>
      <div class="col-sm-12 text-center mb-2">
        <b-button v-if="!showCharacterTagging" @click="showCharacterTagging=true">Tag Characters</b-button>
        <div v-else>
          <form>
            <ac-form-container
                ref="characterTaggingForm"
                :url="`${this.url}tag-characters/`"
                :schema="characterTaggingSchema"
                :options="characterTaggingOptions"
                :model="characterTaggingModel"
                :success="postTag"
            />
            <b-button variant="danger" @click.prevent="showCharacterTagging=false">Cancel</b-button>
            <b-button type="submit" @click.prevent="$refs.characterTaggingForm.submit">Tag!</b-button>
          </form>
        </div>
      </div>
    </div>
    <div class="mb-5">
      <ac-comment-section v-if="submission" :commenturl="commenturl" :nesting="true" :locked="submission.comments_disabled" />
      <div class="row shadowed" v-if="submission && controls && editing">
        <div class="col-sm-12 text-section text-center">
          <ac-patchbutton :url="url" name="comments_disabled" v-model="submission.comments_disabled" true-text="Disable Commments" false-text="Enable Comments" />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
  .info-block {
    display: inline-block;
    text-align: center;
  }
</style>

<script>
  import { artCall, setMetaContent, textualize, ratingsShort } from '../lib'
  import AcCharacterPreview from './ac-character-preview'
  import Editable from '../mixins/editable'
  import Viewer from '../mixins/viewer'
  import AcPatchfield from './ac-patchfield'
  import AcPatchbutton from './ac-patchbutton'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'
  import AcAsset from './ac-asset'
  import AcPatchdropdown from './ac-patchdropdown'
  import AcAction from './ac-action'
  import AcFormContainer from './ac-form-container'

  export default {
    name: 'Submission',
    components: {
      AcFormContainer,
      AcPatchdropdown,
      AcCharacterPreview,
      AcPatchfield,
      AcCommentSection,
      AcPatchbutton,
      AcAvatar,
      AcAsset,
      AcAction
    },
    mixins: [Viewer, Editable],
    data () {
      return {
        submission: null,
        url: `/api/profiles/v1/asset/${this.$route.params.assetID}/`,
        commenturl: `/api/profiles/v1/asset/${this.$route.params.assetID}/comments/`,
        showCharacterTagging: false,
        characterTaggingModel: {
          characters: []
        },
        characterTaggingSchema: {
          fields: [
            {
              type: 'character-search',
              model: 'characters',
              label: 'Characters',
              featured: true,
              placeholder: 'Search characters',
              styleClasses: 'field-input'
            }
          ]
        },
        characterTaggingOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      controls () {
        return this.submission.uploaded_by.username === this.$root.user.username
      },
      ownWork () {
        return this.submission.uploaded_by.username === (this.submission.artist && this.submission.artist.username)
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
      goBack () {
        if (this.$router.history.length) {
          this.$router.go(-1)
        } else {
          this.$router.history.push({name: 'Profile', params: {username: this.submission.uploaded_by.username}})
        }
      },
      postTag (response) {
        this.populateSubmission(response)
        this.showCharacterTagging = false
      },
      ratingsShort
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateSubmission, this.$error)
    }
  }
</script>
