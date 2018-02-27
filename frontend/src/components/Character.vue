<template>
  <v-container>
    <v-card v-if="character">
      <v-speed-dial v-if="controls" bottom right fixed v-model="editing" elevation-10 style="z-index: 4">
        <v-btn v-if="controls"
               dark
               color="blue"
               fab
               hover
               slot="activator"
               v-model="editing"
        >
          <v-icon>lock</v-icon>
          <v-icon>lock_open</v-icon>
        </v-btn>
        <ac-action
            variant="danger" :confirm="true" :success="goToListing"
            :url="`/api/profiles/v1/account/${this.user.username}/characters/${this.character.name}/`"
            method="DELETE"
            dark small color="red" fab
        ><v-icon>delete</v-icon>
          <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this character? This cannot be undone!</div>
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
        <v-btn v-if="controls"
               dark
               color="green"
               fab
               hover
               small
               @click="showUpload=true"
        >
          <v-icon>file_upload</v-icon>
        </v-btn>
      </v-speed-dial>
      <v-layout row wrap>
        <v-flex xs12 sm6 md7 lg8 class="pl-3 pt-3">
          <h1>{{ character.name }}</h1>
          <div class="col-6">
            <p v-if="(character.tags.length === 0) && editing">
              Add some tags to describe your character. Try tagging their species, gender or things they're commonly found doing.
            </p>
            <ac-tag-display
                :editable="editing"
                :url="`${url}tag/`"
                :callback="loadCharacter"
                :tag-list="character.tags"
                :controls="controls && editing"
                tab-name="characters"
                v-if="character.tags.length || editing"
            />
          </div>
        </v-flex>
        <v-flex xs12 sm6 md5 lg4>
          <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
            <v-card-media :src="$img(character.primary_asset, 'thumbnail')">
              <ac-asset :asset="character.primary_asset" thumbnail="thumbnail" :text-only="true" />
            </v-card-media>
          </router-link>
          <!-- Will render placeholder. -->
          <v-card-media v-else :src="$img(character.primary_asset, 'thumbnail')">
            <ac-asset :asset="character.primary_asset" thumbnail="thumbnail" :text-only="true" />
          </v-card-media>
        </v-flex>
      </v-layout>
    </v-card>
    <v-card class="row mb-3 mt-3" v-if="character">
      <v-layout row wrap class="pt-3 pl-4 pr-4">
        <v-flex xs12 md9>
          <h2 class="mb-0">
            About {{ character.name }}
          </h2>
          <div class="card-block">
            <div class="card-block character-description"><ac-patchfield v-model="character.description" name="description" :multiline="true" :editmode="editing" :url="url" /></div>
          </div>
        </v-flex>
        <v-flex md3 xs12 class="text-xs-center">
          <ac-avatar :user="character.user" />
        </v-flex>
      </v-layout>
      <v-dialog
          v-model="showUpload"
          fullscreen
          transition="dialog-bottom-transition"
          :overlay="false"
          scrollable
      >
        <v-card tile>
          <v-toolbar card dark color="primary">
            <v-btn icon @click.native="showUpload = false" dark>
              <v-icon>close</v-icon>
            </v-btn>
            <v-toolbar-title>New Upload</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn dark flat @click.prevent="$refs.newUploadForm.submit">Upload</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>
            <form @submit.prevent="$refs.newUploadForm.submit">
              <ac-form-container ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                                 :options="newUploadOptions" :success="addUpload"
                                 :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/assets/`"
              />
            </form>
          </v-card-text>
        </v-card>
      </v-dialog>
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
            <v-toolbar-title>Character Settings</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn dark flat @click.prevent="$refs.settingsForm.submit">Save Settings</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>
            <form @submit.prevent="$refs.settingsForm.submit">
              <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                                 :options="newUploadOptions" :success="updateSettings"
                                 method="PATCH"
                                 :url="url"
              />
            </form>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-card>
    <div v-if="character" class="color-section">
      <v-layout row>
        <v-flex
            v-for="refColor in character.colors"
            :key="refColor.id"
            :style="'background-color: ' + refColor.color + ';' + 'height: 3rem;'" />
      </v-layout>
      <v-expansion-panel v-if="character.colors.length || editing" class="mb-3">
        <v-expansion-panel-content>
          <div slot="header" class="text-xs-center"><v-icon>palette</v-icon></div>
          <v-card class="row mb-3 pl-2 pr-2 shadowed text-section pt-2" v-if="character && (character.colors.length || editing)">
            <div v-for="(refColor, index) in character.colors" :key="refColor.id">
              <ac-ref-color
                  :ref-color="refColor"
                  :editing="editing"
                  :callback="fetchCharacter"
                  :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/colors/${refColor.id}/`"
                  class="mb-1 mt-1"
              />
              <v-divider v-if="index + 1 < character.colors.length" :key="`divider-${index}`" />
            </div>
            <div class="col-12 mt-2 mb-2">
              <div class="row-centered" v-if="character.colors.length < 10">
                <div class="col-12 col-md-6 col-centered text-xs-center">
                  <v-btn v-if="controls && editing && !showNewColor" color="primary" @click="showNewColor = true">Add a color reference</v-btn>
                  <div v-if="showNewColor && editing">
                    <form @submit.prevent="$refs.newColorForm.submit">
                      <ac-form-container
                          ref="newColorForm" :schema="newColorSchema" :model="newColorModel"
                          class="text-xs-center"
                          :options="newUploadOptions" :success="addColor"
                          :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/colors/`"
                      />
                      <v-btn @click="showNewColor=false">Cancel</v-btn>
                      <v-btn type="submit" color="primary">Add Color</v-btn>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </div>
    <v-card v-if="character && character.open_requests && (character.open_requests_restrictions|| editing)" class="mb-3">
      <v-layout row wrap class="pt-3 pl-4 pr-4 pb-3">
        <v-flex xs12>
          <h2 class="mb-0">
            Commission Restrictions
          </h2>
        </v-flex>
        <v-flex xs12>
          <ac-patchfield v-model="character.open_requests_restrictions" name="open_requests_restrictions" :multiline="true" :editmode="editing" :url="url" />
        </v-flex>
      </v-layout>
    </v-card>
    <v-card v-if="character && assets && assets.length">
      <v-layout v-if="assets.length === 1" row wrap>
        <v-flex xs12  class="pl-2 pr-2 pt-3 pb-3">
          <ac-gallery-preview
              v-if="character.primary_asset && character.primary_asset.id"
              :asset="character.primary_asset"
              containerStyle="min-height: 50rem;"
              thumb-name="gallery"
          />
        </v-flex>
      </v-layout>
      <v-layout v-else row wrap>
        <v-flex xs12 lg9 class="pl-2 pr-2 pt-3 pb-3">
          <ac-gallery-preview
              v-if="character.primary_asset && character.primary_asset.id"
              :asset="character.primary_asset"
              containerStyle="min-height: 50rem;"
              thumb-name="gallery"
          />
          <v-flex class="text-xs-center mt-4 hidden-md-and-down">
            <router-link :to="{name: 'CharacterGallery', params: {username: username, characterName: characterName}}">
              <v-btn v-if="assets && moreToLoad" color="primary">
                See all uploads of {{ character.name }}
              </v-btn>
            </router-link>
          </v-flex>
        </v-flex>
        <v-flex sm12 lg3 class="pl-2 pr-2 pt-3 pb-3">
          <v-layout row wrap>
            <ac-gallery-preview v-for="(asset, key, index) in assets"
                                :key="key" :id="'asset-' + key"
                                v-if="asset.id !== displayedId"
                                :asset="asset"
                                lg12 md4 sm6 xs12
                                class="pr-1 pl-1"
            >
            </ac-gallery-preview>
          </v-layout>
        </v-flex>
        <v-flex xs12 class="text-xs-center mb-2 hidden-lg-and-up">
          <router-link :to="{name: 'CharacterGallery', params: {username: username, characterName: characterName}}">
            <v-btn v-if="assets && moreToLoad" color="primary">
              See all uploads of {{ character.name }}
            </v-btn>
          </router-link>
        </v-flex>
      </v-layout>
    </v-card>
  </v-container>
</template>

<style lang="scss">
  @import '../custom-bootstrap';
  .character-description {
    width: 100%
  }
  .statline p{
    margin-bottom: .5rem;
    border-bottom: 1px solid $dark-purple;
  }
  .vue-form-generator .wrapper input[type="color"] {
    display: inline-block;
  }
  .color-section .header__icon {
    display: none;
  }
</style>

<script>
  import $ from 'jquery'
  import Vue from 'vue'
  import VueFormGenerator from 'vue-form-generator'
  import { artCall, ratings } from '../lib'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import Viewer from '../mixins/viewer'
  import AcAction from './ac-action'
  import AcFormContainer from './ac-form-container'
  import AcPatchfield from './ac-patchfield'
  import AcGalleryPreview from './ac-gallery-preview'
  import AcAvatar from './ac-avatar'
  import AcAsset from './ac-asset'
  import AcTagDisplay from './ac-tag-display'
  import AcRefColor from './ac-ref-color'

  export default {
    name: 'Character',
    mixins: [Viewer, Perms, Editable],
    components: {
      AcRefColor,
      AcTagDisplay,
      AcGalleryPreview,
      AcPatchfield,
      AcAction,
      AcFormContainer,
      AcAvatar,
      AcAsset
    },
    props: ['characterName'],
    methods: {
      parseDesc: function () {
        return this.$root.md.render(this.character.description)
      },
      setIndex: function (key) {
        this.$data.selectedIndex = key
      },
      goToListing: function () {
        this.$router.history.push({name: 'Characters', params: {username: this.user.username}})
      },
      removeAsset: function (asset) {
        artCall(
          `${this.url}/asset/${asset.id}/`,
          'DELETE',
          null,
          this.postAssetDelete(asset)
        )
      },
      postPrimary: function (assetId) {
        let self = this
        return function () {
          self.character.primary_asset = assetId
        }
      },
      postAssetDelete: function (asset) {
        let self = this
        return function () {
          let index = self.character.assets.indexOf(asset)
          self.character.assets.splice(index, 1)
          if (self.selectedIndex >= index) {
            self.selectedIndex -= 1
          }
        }
      },
      showUpdater: function () {
        this.$refs.updater.showUpdater()
      },
      updateSettings (response) {
        this.loadCharacter(response)
      },
      loadCharacter (response) {
        this.character = response
        this.settingsModel = JSON.parse(JSON.stringify(response))
        this.showSettings = false
      },
      displayUploader () {
        this.showUpload = true
        Vue.nextTick(function () {
          $('html, body').animate({ scrollTop: $('#title').offset().top - 100 }, 200)
        })
      },
      addColor (response) {
        this.character.colors.push(response)
      },
      fetchAssets () {
        artCall(this.url + 'assets/?size=4', 'GET', null, this.loadAssets)
      },
      fetchCharacter () {
        artCall(this.url, 'GET', null, this.loadCharacter, this.$error)
      },
      loadAssets (response) {
        this.totalPieces = response.count
        this.assets = response.results
      },
      addUpload (response) {
        this.$router.history.push(
          {name: 'Submission', params: {assetID: response.id}}
        )
      }
    },
    data () {
      return {
        name: 'character',
        selectedIndex: null,
        expand: this.expanded,
        character: null,
        assets: null,
        totalPieces: 0,
        url: `/api/profiles/v1/account/${this.username}/characters/${this.characterName}/`,
        newUploadModel: {
          title: '',
          caption: '',
          private: false,
          rating: 0,
          file: [],
          comments_disabled: false
        },
        showNewColor: false,
        newColorModel: {
          color: '#ffffff',
          note: ''
        },
        newColorSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Note',
            placeholder: 'Fur color',
            model: 'note',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-color',
            label: 'Color',
            model: 'color',
            required: true,
            featured: true,
            colorOptions: {
              preferredFormat: 'rgb'
            }
          }]
        },
        showSettings: false,
        settingsModel: {
          name: '',
          open_comissions: false,
          private: false
        },
        settingsSchema: {
          fields: [{
            type: 'v-text',
            label: 'Name',
            hint: "This will change the URL of your character's page. Any existing links to them may be broken.",
            model: 'name'
          }, {
            type: 'v-checkbox',
            label: 'Open Requests',
            hint: 'Allow other people to commission pieces of your character. You ' +
                  'can specify restrictions for commissions after this is enabled.',
            model: 'open_requests'
          }, {
            type: 'v-checkbox',
            label: 'Private',
            hint: 'Hides your character from public listings and prevents anyone with whom they have not been ' +
                  'explicitly shared from viewing it.',
            model: 'private'
          }]
        },
        showUpload: false,
        newUploadSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Title',
            model: 'title',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            label: 'Caption',
            model: 'caption',
            featured: true,
            multiline: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Private Upload?',
            model: 'private',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Only shows this piece to people you have explicitly shared it to.'
          },
          {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Comments disabled?',
            model: 'comments_disabled',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Prevents people from commenting on this piece.'
          },
          {
            type: 'v-select',
            label: 'Rating',
            model: 'rating',
            featured: true,
            required: true,
            values: ratings,
            selectOptions: {
              hideNoneSelectedText: true
            },
            validator: VueFormGenerator.validators.required
          },
          {
            type: 'v-file-upload',
            id: 'file',
            label: 'File',
            model: 'file',
            required: true
          }]
        },
        newUploadOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      displayedId () {
        if (this.character.primary_asset) {
          return this.character.primary_asset.id
        } else if (this.assets) {
          return this.assets[0].id
        } else {
          return null
        }
      },
      moreToLoad () {
        return this.totalPieces > 4
      }
    },
    created () {
      this.fetchCharacter()
      this.fetchAssets()
    },
    watch: {
      rating () {
        this.fetchAssets()
      },
      'character.name': function (value) {
        this.$router.history.replace(
          {
            'name': 'Character',
            'params': {'username': this.user.username, 'characterName': value},
            'query': {'editing': this.editing}
          }
        )
        this.url = `/api/profiles/v1/account/${this.username}/characters/${value}/`
      }
    }
  }
</script>
