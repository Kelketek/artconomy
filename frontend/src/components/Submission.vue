<template>
  <div class="container">
    <div class="row shadowed" v-if="submission">
      <div class="col-12 character-refsheet-container text-xs-center text-section">
        <ac-asset :asset="submission" thumb-name="gallery" :rating="rating" />
      </div>
      <div class="col-md-3 col-12 text-section pt-3 pl-4">
        <ac-tag-display
            :editable="true"
            :url="`${url}/tag/`"
            :callback="populateSubmission"
            :tag-list="submission.tags"
            :controls="controls"
        />
      </div>
      <div class="col-12 col-md-5 text-section pt-3 pl-4">
        <ac-patchfield v-model="submission.title" name="title" styleclass="name-edit" placeholder="Set the title" :editmode="editing" :url="url" />
        <div class="card-block submission-description"><ac-patchfield v-model="submission.caption" name="caption" placeholder="Add a caption" :multiline="true" :editmode="editing" :url="url" /></div>
      </div>
      <div class="col-12 col-md-4 text-section pt-3 pl-4 text-xs-center">
        <div class="info-block" v-if="!artistUploader">
          <h4>Added By</h4>
          <ac-avatar :user="submission.uploaded_by" />
        </div>
        <div
            v-if="submission.artists.length"
            class="info-block"
        >
          <h4 v-if="submission.artists.length === 1">Artist</h4>
          <h4 v-else>Artists</h4>
          <ac-avatar
              v-for="artist in submission.artists"
              :key="artist.id"
              :user="artist"
              :removable="(artist.username === viewer.username) || controls"
              :remove-url="`${url}tag-artists/`"
              field-name="artists"
              :callback="populateSubmission"
          />
        </div>
        <div>
          <ac-patchdropdown v-model="submission.rating" :editmode="editing" :options="ratingsShort()" :url="url" name="rating" />
          <ac-action v-if="editing" :url="url" method="PATCH" :send="{private: !submission.private}" :success="populateSubmission">
            <span v-if="submission.private"><i class="fa fa-eye-slash"></i> Hide submission</span>
            <span v-else><i class="fa fa-eye"></i> Unhide submission</span>
          </ac-action>
          <div v-else-if="controls" class="text-xs-center">
            <span v-if="submission.private"><i class="fa fa-eye"></i> Submission is public</span>
            <span v-else><i class="fa fa-eye-slash"></i> Submission is private</span>
          </div>
          <ac-action :url="`${url}favorite/`" :success="populateSubmission">
            <span v-if="submission.favorite"><i class="fa fa-heart-o"></i> Remove from Favorites ({{ submission.favorite_count }})</span>
            <span v-else><i class="fa fa-heart"></i> Add to Favorites ({{ submission.favorite_count }})</span>
          </ac-action>
          <v-btn v-if="!showArtistTagging" @click="showArtistTagging=true">Tag Artists</v-btn>
          <div v-else>
            <form>
              <ac-form-container
                  ref="artistTaggingForm"
                  :url="`${this.url}tag-artists/`"
                  :schema="artistTaggingSchema"
                  :options="artistTaggingOptions"
                  :model="artistTaggingModel"
                  :success="postArtistTag"
              />
              <v-btn variant="danger" @click.prevent="showArtistTagging=false">Cancel</v-btn>
              <v-btn type="submit" @click.prevent="$refs.artistTaggingForm.submit">Tag!</v-btn>
            </form>
          </div>
        </div>
        <p v-if="controls && submission.order" class="mb-0">
          From <router-link :to="{name: 'Order', params: {orderID: submission.order, username: submission.uploaded_by.username}}">Order {{submission.order}}</router-link>
        </p>
        <p v-if="(submission.order && ownWork ) || controls && (submission.order)" class="mb-0">
          From <router-link :to="{name: 'Sale', params: {orderID: submission.order, username: viewer.username}}">Sale {{submission.order}}</router-link>
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
      <div class="col-12 text-section mb-2">
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
          :can-showcase="controls"
          :asset-id="submission.id"
      >
      </ac-character-preview>
      <div class="col-12 text-xs-center mb-2">
        <v-btn v-if="!showCharacterTagging" @click="showCharacterTagging=true">Tag Characters</v-btn>
        <div v-else>
          <form>
            <ac-form-container
                ref="characterTaggingForm"
                :url="`${this.url}tag-characters/`"
                :schema="characterTaggingSchema"
                :options="characterTaggingOptions"
                :model="characterTaggingModel"
                :success="postCharacterTag"
            />
            <v-btn variant="danger" @click.prevent="showCharacterTagging=false">Cancel</v-btn>
            <v-btn type="submit" @click.prevent="$refs.characterTaggingForm.submit">Tag!</v-btn>
          </form>
        </div>
      </div>
    </div>
    <div class="mb-5">
      <ac-comment-section v-if="submission" :commenturl="commenturl" :nesting="true" :locked="submission.comments_disabled" />
      <div class="row shadowed" v-if="submission && controls && editing">
        <div class="col-12 text-section text-xs-center">
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
  import AcTag from './ac-tag'
  import AcTagDisplay from './ac-tag-display'

  export default {
    name: 'Submission',
    components: {
      AcTagDisplay,
      AcTag,
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
        showArtistTagging: false,
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
        },
        artistTaggingModel: {
          artists: []
        },
        artistTaggingSchema: {
          fields: [
            {
              type: 'user-search',
              model: 'artists',
              label: 'Artists',
              featured: true,
              placeholder: 'Search artists',
              styleClasses: 'field-input'
            }
          ]
        },
        artistTaggingOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      controls () {
        return this.submission.uploaded_by.username === this.$root.user.username
      },
      artistUploader () {
        return this.isArtist(this.submission.uploaded_by.username)
      },
      ownWork () {
        return this.isArtist(this.viewer.username)
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
      isArtist (username) {
        for (let artist of this.submission.artists) {
          if (artist.username === username) {
            return true
          }
        }
        return false
      },
      postArtistTag (response) {
        this.populateSubmission(response)
        this.showArtistTagging = false
      },
      postCharacterTag (response) {
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
