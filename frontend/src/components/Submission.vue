<template>
  <div>
    <v-container v-if="submission">
      <v-layout row wrap>
        <v-flex text-xs-center xs12>
          <ac-asset :asset="submission" thumb-name="gallery" :rating="rating" />
        </v-flex>
        <v-flex text-xs-center xs12 v-if="!viewer.username">
          <v-btn @click="showRatingSettings = true">Adjust my content rating settings</v-btn>
          <ac-form-dialog ref="ratingSettingsForm" :schema="ratingSettingsSchema" :model="ratingSettingsModel"
                             :options="settingsOptions" :success="updateSession"
                             :url="`/api/profiles/v1/session/settings/`"
                             method="PATCH"
                             title="Adjust Content Settings"
                             :reset-after="false"
                             v-model="showRatingSettings"
          >
            <v-flex slot="header" text-xs-center>
              <p>
                <router-link :to="{name: 'Login', params: {tabName: 'register'}}">Registered users</router-link>
                can save and fine tune their content settings.
                <router-link :to="{name: 'Login', params: {tabName: 'register'}}">Consider registering today!</router-link>
              <p/>
            </v-flex>
          </ac-form-dialog>
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
            <v-icon>lock</v-icon>
            <v-icon>lock_open</v-icon>
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
              <ac-action :url="url" :send="{subscribed: !submission.subscribed}" method="PUT" :success="populateSubmission">
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
            <p v-if="(submission.order && ownWork ) || controls && (submission.order)" class="mb-0">
              From <router-link :to="{name: 'Sale', params: {orderID: submission.order, username: viewer.username}}">Sale {{submission.order}}</router-link>
            </p>
          </v-flex>
        </v-layout>
      </v-card>
      <v-card class="mt-3">
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
          <v-flex xs12 class="text-xs-center">
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
      <v-dialog
          v-model="showSettings"
          fullscreen
          transition="dialog-bottom-transition"
          :overlay="false"
          scrollable
      >
        <v-card tile>
          <v-toolbar card dark color="primary">
            <v-btn icon @click.native="showSettings = false" dark>
              <v-icon>close</v-icon>
            </v-btn>
            <v-toolbar-title>Submission Settings</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn dark flat @click.prevent="$refs.settingsForm.submit">Save Settings</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="$refs.settingsForm.submit">
              <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                                 :options="artistTaggingOptions" :success="populateSubmission"
                                 method="PATCH"
                                 :url="url"
              />
            </v-form>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
    <div class="mb-5">
      <ac-comment-section v-if="submission" :commenturl="commenturl" :nesting="true" :locked="submission.comments_disabled" />
    </div>
  </div>
</template>

<style scoped lang="scss">
  @import '../custom-bootstrap';
  .pulse {
    animation: pulse_animation 2s infinite;
  }
  @keyframes pulse_animation {
    0% { background-color: $primary; }
    25% {background-color: lighten($primary, 20)}
    50% { background-color: $secondary; }
    75% {background-color: lighten($secondary, 20)}
    100% { background-color: $primary; }
  }
  .info-block {
    display: inline-block;
    text-align: center;
  }
</style>

<script>
  import { artCall, setMetaContent, textualize, ratingsShort, RATINGS_SHORT, ratings } from '../lib'
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
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'Submission',
    components: {
      AcFormDialog,
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
        showSettings: false,
        showRatingSettings: false,
        characterTaggingModel: {
          characters: []
        },
        settingsModel: {
          private: false,
          comments_disabled: false,
          rating: 0
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
            values: ratings
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
      }
    },
    methods: {
      populateSubmission (response) {
        this.submission = response
        let newSettings = {}
        for (let key of Object.keys(this.settingsModel)) {
          newSettings[key] = response[key]
        }
        this.settingsModel = newSettings
        this.showSettings = false
        this.ratingSettingsModel.rating = this.viewer.rating
        this.setMeta()
      },
      setMeta () {
        document.title = `${this.submission.title} -- by ${this.submission.owner.username}`
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
