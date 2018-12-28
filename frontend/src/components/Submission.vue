<template>
  <div>
    <v-container v-if="submission" id="submission-section">
      <v-layout row wrap>
        <v-flex text-xs-center xs12>
          <ac-asset :asset="submission" thumb-name="gallery" :rating="rating" />
          <a :href="submission.file.full"><p>Download</p></a>
        </v-flex>
        <v-flex text-xs-center xs12 v-if="!viewer.username">
          <v-btn @click="showRatingSettings = true" v-if="!extreme">Adjust my content rating settings</v-btn>
          <ac-form-dialog ref="ratingSettingsForm" :schema="ratingSettingsSchema" :model="ratingSettingsModel"
                             :options="settingsOptions" :success="updateSession"
                             :url="`/api/profiles/v1/session/settings/`"
                             method="PATCH"
                             title="Adjust Content Settings"
                             :reset-after="false"
                             v-model="showRatingSettings"
                             v-if="!extreme"
          >
            <v-flex slot="header" text-xs-center>
              <p>
                <router-link :to="{name: 'Login', params: {tabName: 'register'}}">Registered users</router-link>
                can save and fine tune their content settings.
                <router-link :to="{name: 'Login', params: {tabName: 'register'}}">Consider registering today!</router-link>
              </p>
            </v-flex>
          </ac-form-dialog>
          <div v-if="!viewer.username && extreme">
            <p>
              Content of this rating may only be viewed by registered users.
              <router-link :to="{name: 'Login', params: {tabName: 'register'}}">Consider registering today!
              </router-link>
            </p>
          </div>
        </v-flex>
      </v-layout>
      <v-card v-if="submission">
        <v-speed-dial v-if="controls" bottom right fixed elevation-10 style="z-index: 4">
          <v-btn v-if="controls"
                 dark
                 color="purple"
                 fab
                 hover
                 slot="activator"
                 large
          >
            <v-icon>menu</v-icon>
          </v-btn>
          <v-btn v-if="controls"
                 dark
                 color="blue"
                 fab
                 hover
                 small
                 @click="editing = !editing"
                 v-model="editing"
          >
            <v-icon v-if="editing">lock</v-icon>
            <v-icon v-else>edit</v-icon>
          </v-btn>
          <ac-action
              variant="danger" :confirm="true" :success="goBack"
              :url="url"
              method="DELETE"
              dark small color="red" fab
          ><v-icon>delete</v-icon>
            <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this submission? This cannot be undone!</div>
          </ac-action>
          <v-btn v-if="controls"
                 dark
                 color="orange"
                 fab
                 hover
                 small
                 @click="showSettings=true"
          >
            <v-icon>settings</v-icon>
          </v-btn>
        </v-speed-dial>
        <v-layout row wrap>
          <v-flex xs12 md3 class="pt-3 pl-4">
            <ac-tag-display
                :editable="true"
                :url="`${url}/tag/`"
                :callback="populateSubmission"
                :tag-list="submission.tags"
                :controls="controls"
            />
            <ac-share-button :title="shareTitle" :target-rating="submission.rating" v-if="!submission.private" />
          </v-flex>
          <v-flex xs12 md5 class="pt-3 pl-4">
            <h1><ac-patchfield v-model="submission.title" name="title" placeholder="Set the title" :editmode="editing" :url="url" /></h1>
            <div class="card-block submission-description"><ac-patchfield v-model="submission.caption" name="caption" placeholder="Add a caption" :multiline="true" :editmode="editing" :url="url" /></div>
          </v-flex>
          <v-flex xs12 md4 text-xs-center class="pt-3 pl-4">
            <div class="info-block" v-if="!artistUploader">
              <h4>Added By</h4>
              <ac-avatar :user="submission.owner" />
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
              Rating: {{ ratingText }}
              <div v-if="controls" class="text-xs-center">
                <span v-if="submission.private"><v-icon>visibility_off</v-icon> Submission is private</span>
                <span v-else><v-icon>visibility</v-icon> Submission is public</span>
              </div>
              <ac-action :url="url" :send="{subscribed: !submission.subscribed}" method="PUT" :success="populateSubmission" v-if="isLoggedIn">
                <v-icon v-if="submission.subscribed">volume_up</v-icon><v-icon v-else>volume_off</v-icon>
              </ac-action>
              <ac-action :url="`${url}favorite/`" :success="populateSubmission" v-if="isLoggedIn">
                <span v-if="submission.favorite"><v-icon>favorite_outline</v-icon> Remove from Favorites ({{ submission.favorite_count }})</span>
                <span v-else><v-icon>favorite</v-icon> Add to Favorites ({{ submission.favorite_count }})</span>
              </ac-action>
              <v-btn v-if="!showArtistTagging && isLoggedIn" @click="showArtistTagging=true">Tag Artists</v-btn>
              <div v-else-if="isLoggedIn">
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
                  <v-btn type="submit" @click.prevent="$refs.artistTaggingForm.submit" class="pulse">Tag!</v-btn>
                </form>
              </div>
            </div>
            <p v-if="controls && submission.order" class="mb-0">
              From <router-link :to="{name: 'Order', params: {orderID: submission.order, username: submission.owner.username}}">Order {{submission.order}}</router-link>
            </p>
            <p v-if="(submission.order && ownWork )" class="mb-0">
              From <router-link :to="{name: 'Sale', params: {orderID: submission.order, username: viewer.username}}">Sale {{submission.order}}</router-link>
            </p>
          </v-flex>
        </v-layout>
      </v-card>
      <v-card class="mt-3" v-if="submission.characters.length">
        <v-layout>
          <v-flex xs12 class="pl-2">
            <h2>Featuring</h2>
          </v-flex>
        </v-layout>
      </v-card>
    </v-container>
    <v-container grid-list-md v-if="submission">
      <v-layout row wrap>
          <ac-character-preview
              v-for="char in submission.characters"
              :character="char"
              :expanded="true"
              :key="char.id"
              :remove-url="`${url}tag-characters/`"
              :removable="((char.user.username === viewer.username) || controls) && !char.transfer"
              :callback="populateSubmission"
              :can-showcase="char.user.username === viewer.username"
              :asset-id="submission.id"
              xs12 sm4 lg3
          >
          </ac-character-preview>
          <v-flex xs12 class="text-xs-center" v-if="viewer.username">
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
                <v-btn type="submit" @click.prevent="$refs.characterTaggingForm.submit" class="pulse">Tag!</v-btn>
              </form>
            </div>
          </v-flex>
      </v-layout>
      <ac-form-dialog
          v-model="showSettings"
          title="Submission Settings"
          :model="settingsModel"
          :options="artistTaggingOptions"
          :schema="settingsSchema"
          :success="populateSubmission"
          method="PATCH"
          :url="url"
          submit-text="Save Settings"
      >
        <v-flex slot="header" text-xs-center>
          <v-btn color="primary" @click="showShare = true">
            <v-icon>share</v-icon> Share
          </v-btn>
        </v-flex>
      </ac-form-dialog>
      <ac-form-dialog
        v-model="showShare"
        :title="`Share ${submission.title}`"
        submit-text="Save"
        :model="shareModel"
        :options="artistTaggingOptions"
        :schema="shareSchema"
        method="POST"
        :url="`${url}share/`"
        :success="populateSubmission"
      >
        <v-container slot="footer" grid-list-lg>
          <v-layout row wrap>
            <v-flex xs12 text-xs-center>
              <p><strong>Currently shared with...</strong></p>
              <p><small>Click the x next to a name to stop sharing with this person.</small></p>

            </v-flex>
            <v-flex lg2 xs6 md4>
              <ac-avatar
                  v-for="user in submission.shared_with"
                  :key="user.id"
                  :user="user"
                  :removable="controls"
                  :remove-url="`${url}share/`"
                  field-name="shared_with"
                  :callback="reloadSubmission"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </ac-form-dialog>
    </v-container>
    <div class="mb-5">
      <ac-comment-section v-if="submission" :commenturl="commenturl" :nesting="true" :locked="submission.comments_disabled" />
    </div>
  </div>
</template>

<style scoped>
  .pulse {
    animation: pulse_animation 2s infinite;
  }
  @keyframes pulse_animation {
    0% { background-color: #5f2480 }
    25% {background-color: #735c94 }
    50% { background-color: #82204A }
    75% {background-color: #96345e}
    100% { background-color: #5f2480 }
  }
  .info-block {
    display: inline-block;
    text-align: center;
  }
</style>

<script>
  import {artCall, setMetaContent, textualize, ratingsShort, RATINGS_SHORT, ratings, ratingsNonExtreme} from '../lib'
  import AcCharacterPreview from './ac-character-preview'
  import Editable from '../mixins/editable'
  import Viewer from '../mixins/viewer'
  import AcPatchfield from './ac-patchfield'
  import AcPatchbutton from './ac-patchbutton'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'
  import AcAsset from './ac-asset'
  import AcAction from './ac-action'
  import AcFormContainer from './ac-form-container'
  import AcTag from './ac-tag'
  import AcTagDisplay from './ac-tag-display'
  import AcFormDialog from './ac-form-dialog'
  import AcShareButton from './ac-share-button'

  export default {
    name: 'Submission',
    components: {
      AcShareButton,
      AcFormDialog,
      AcTagDisplay,
      AcTag,
      AcFormContainer,
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
        showSettings: false,
        showRatingSettings: false,
        showShare: false,
        characterTaggingModel: {
          characters: []
        },
        settingsModel: {
          private: false,
          comments_disabled: false,
          rating: 0,
          file: [],
          preview: []
        },
        settingsSchema: {
          fields: [{
            type: 'v-checkbox',
            label: 'Private',
            hint: 'If this is checked, the submission will not be visible except to those you explicitly share it with.',
            model: 'private'
          }, {
            type: 'v-checkbox',
            label: 'Comments Disabled',
            hint: "Don't allow comments on this submission.",
            model: 'comments_disabled'
          }, {
            type: 'v-select',
            label: 'Rating',
            model: 'rating',
            featured: true,
            required: true,
            values: ratings,
            selectOptions: {
              hideNoneSelectedText: true
            }
          },
          {
            type: 'v-file-upload',
            id: 'file',
            label: 'Replace File',
            model: 'file',
            required: false
          },
          {
            type: 'v-file-upload',
            id: 'preview',
            label: 'Replace Preview Image/Thumbnail',
            model: 'preview',
            hint: 'Should be a square image. We recommend a size not smaller than 300x300 pixels.',
            required: false
          }]
        },
        characterTaggingSchema: {
          fields: [
            {
              type: 'character-search',
              model: 'characters',
              label: 'Characters',
              tagging: true,
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
              tagging: true,
              multiple: true,
              placeholder: 'Search artists',
              styleClasses: 'field-input'
            }
          ]
        },
        artistTaggingOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        shareModel: {
          shared_with: []
        },
        shareSchema: {
          fields: [
            {
              type: 'user-search',
              model: 'shared_with',
              label: 'Share with',
              featured: true,
              tagging: true,
              multiple: true,
              placeholder: 'Search users',
              styleClasses: 'field-input'
            }
          ]
        },
        ratingSettingsModel: {
          rating: 0
        },
        ratingSettingsSchema: {
          fields: [{
            type: 'v-select',
            label: 'Max Content Rating',
            model: 'rating',
            required: false,
            hint: 'By setting this value, you are affirming that the content this rating represents is legal to view in your area and you meet all legal qualifications (such as age) to view it.',
            selectOptions: {
              hideNoneSelectedText: true
            },
            values: ratingsNonExtreme
          }]
        },
        settingsOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      controls () {
        return this.submission.owner.username === this.$root.user.username
      },
      artistUploader () {
        return this.isArtist(this.submission.owner.username)
      },
      ownWork () {
        return this.isArtist(this.viewer.username)
      },
      ratingText () {
        return RATINGS_SHORT[this.submission.rating]
      },
      extreme () {
        return this.submission.rating === 3
      },
      shareTitle () {
        let title = this.submission.title
        if (this.submission.artists.length) {
          title += ' - by '
          let names = this.submission.artists.map((x) => { return x.username })
          title += names.join(', ')
        }
        return title
      }
    },
    methods: {
      reloadSubmission (response) {
        this.submission = response
        let newSettings = {}
        for (let key of Object.keys(this.settingsModel)) {
          newSettings[key] = response[key]
        }
        newSettings.file = []
        newSettings.preview = []
        this.settingsModel = newSettings
        this.ratingSettingsModel.rating = this.viewer.rating
        this.setMeta()
      },
      populateSubmission (response) {
        this.reloadSubmission(response)
        this.showSettings = false
        this.showShare = false
        this.shareModel.shared_with = []
      },
      setMeta () {
        document.title = `${this.submission.title} -- by ${this.submission.owner.username} - Artconomy`
        setMetaContent('description', textualize(this.submission.caption).slice(0, 160))
      },
      goBack () {
        if (this.$router.history.length) {
          this.$router.go(-1)
        } else {
          this.$router.history.push({name: 'Profile', params: {username: this.submission.owner.username}})
        }
      },
      updateSession (response) {
        for (let key of Object.keys(response)) {
          this.$root.user[key] = response[key]
        }
        this.showRatingSettings = false
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
      fetchSubmission () {
        artCall(this.url, 'GET', undefined, this.populateSubmission, this.$error)
      },
      ratingsShort
    },
    created () {
      this.fetchSubmission()
    }
  }
</script>
