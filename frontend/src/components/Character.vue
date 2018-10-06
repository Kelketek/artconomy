<template>
  <v-container>
    <v-card v-if="character" id="character-profile">
      <v-speed-dial v-if="controls" bottom right fixed v-model="speedDial" elevation-10 style="z-index: 4">
        <v-btn
          dark
          color="purple"
          fab
          hover
          slot="activator"
          large
          v-model="speedDial"
        >
          <v-icon>menu</v-icon>
        </v-btn>
        <v-btn
               dark
               color="blue"
               fab
               hover
               small
               v-model="editing"
               @click="editing = !editing"
        >
          <v-icon v-if="editing">lock</v-icon>
          <v-icon v-else>edit</v-icon>
        </v-btn>
        <v-btn
               dark
               color="orange"
               fab
               hover
               small
               @click="showSettings=true"
        >
          <v-icon>settings</v-icon>
        </v-btn>
        <v-btn
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
        <v-flex xs12 sm6 md7 lg7 class="pl-3 pt-3">
          <h1>{{ character.name }}</h1>
          <ac-attributes :attributes="character.attributes" :url="`${url}attributes/`" :edit-mode="editing" :success="fetchCharacter"/>
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
          <ac-share-button :title="`${character.name} - by ${character.user.username}`" :target-rating="character.primary_asset && character.primary_asset.rating" v-if="!character.private" />
        </v-flex>
        <v-flex xs12 sm6 md5 lg4 offset-lg1>
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
      <ac-form-dialog ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                         :options="newUploadOptions" :success="addUpload"
                         v-model="showUpload"
                         :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/assets/`"
      />

      <ac-form-dialog ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                         :options="newUploadOptions" :success="updateSettings"
                         method="PATCH"
                         submit-text="Save"
                         title="Character Settings"
                         :url="url"
                         v-model="showSettings"
      >
        <v-layout slot="header" row wrap text-xs-center>
          <v-flex>
            <ac-action
                variant="danger" :confirm="true" :success="goBack"
                :url="`/api/profiles/v1/account/${this.user.username}/characters/${this.character.name}/`"
                method="DELETE"
                dark color="red"
            ><v-icon>delete</v-icon> Delete
              <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this character? This cannot be undone!</div>
            </ac-action>
          </v-flex>
          <v-flex>
            <v-btn @click="showTransfer" color="purple"><v-icon>compare_arrows</v-icon> Transfer</v-btn>
          </v-flex>
          <v-flex>
            <v-btn @click="showShare=true" color="primary"><v-icon>share</v-icon> Share</v-btn>
          </v-flex>
        </v-layout>
      </ac-form-dialog>
      <ac-form-dialog ref="transferForm" :schema="transferSchema" :model="transferModel"
                      :options="newUploadOptions" :success="postTransfer"
                      method="POST"
                      submit-text="Save"
                      title="Transfer Character"
                      :url="`/api/sales/v1/account/${user.username}/transfer/character/${character.name}/`"
                      v-model="transferVisible"
      >
        <v-layout slot="header">
          <v-flex text-xs-center v-if="price && !user.escrow_disabled" xs6 md3 offset-md3>
            <strong>Price: ${{price}}</strong> <br />
            Artconomy service fee: -${{ fee }} <br />
            <strong>Your payout: ${{ payout }}</strong> <br />
          </v-flex>
          <v-flex text-xs-center xs6 md3>
            All transfers are subject to the <router-link :to="{name: 'CharacterTransferAgreement'}">Character Transfer Agreement.</router-link> Character transfers are final and non-refundable.
          </v-flex>
        </v-layout>
      </ac-form-dialog>
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
    <ac-context-gallery
        v-if="character && assets && assets.length"
        :to="{name: 'CharacterGallery', params: {username: username, characterName: characterName}}"
        :showcased="character.primary_asset"
        :assets="assets"
        :totalPieces="totalPieces"
        :see-more-text="`See all uploads of ${character.name}`"
    />
    <ac-form-dialog
        v-model="showShare"
        :title="`Share ${character.name}`"
        submit-text="Save"
        :model="shareModel"
        :options="newUploadOptions"
        :schema="shareSchema"
        method="POST"
        :url="`${url}share/`"
        :success="loadCharacter"
        v-if="character && controls"
    >
      <v-container slot="footer" grid-list-lg>
        <v-layout row wrap>
          <v-flex xs12 text-xs-center>
            <p><strong>Currently shared with...</strong></p>
            <p><small>Click the x next to a name to stop sharing with this person.</small></p>

          </v-flex>
          <v-flex lg2 xs6 md4>
            <ac-avatar
                v-for="user in character.shared_with"
                :key="user.id"
                :user="user"
                :removable="controls"
                :remove-url="`${url}share/`"
                field-name="shared_with"
                :callback="setCharacter"
            />
          </v-flex>
        </v-layout>
      </v-container>
    </ac-form-dialog>
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
  import {artCall, minimumOrZero, ratings, validateTrue, validNumber} from '../lib'
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
  import AcFormDialog from './ac-form-dialog'
  import AcContextGallery from './ac-context-gallery'
  import AcAttributes from './ac-attributes'
  import AcShareButton from './ac-share-button'

  export default {
    name: 'Character',
    mixins: [Viewer, Perms, Editable],
    components: {
      AcShareButton,
      AcAttributes,
      AcContextGallery,
      AcFormDialog,
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
      goBack () {
        if (this.$router.history.length) {
          this.$router.go(-1)
        } else {
          this.$router.history.push({name: 'Profile', params: {username: this.username}})
        }
      },
      postTransfer (response) {
        this.$router.history.push({name: 'CharacterTransfer', params: {'transferID': response.id, username: this.username}})
      },
      showUpdater: function () {
        this.$refs.updater.showUpdater()
      },
      updateSettings (response) {
        this.loadCharacter(response)
      },
      setCharacter (response) {
        this.character = response
        this.settingsModel = JSON.parse(JSON.stringify(response))
      },
      loadCharacter (response) {
        this.setCharacter(response)
        this.showSettings = false
        this.showShare = false
        this.shareModel.shared_with = []
        this.newUploadModel.private = response.private
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
      },
      loadPricing (response) {
        this.pricing = response
      },
      showTransfer () {
        if (!this.character.transfer) {
          this.transferVisible = true
        } else {
          this.$router.history.push(
            {name: 'CharacterTransfer', params: {transferID: this.character.transfer, username: this.username}})
        }
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
        speedDial: false,
        url: `/api/profiles/v1/account/${this.username}/characters/${this.characterName}/`,
        showShare: false,
        newUploadModel: {
          title: '',
          caption: '',
          private: false,
          rating: null,
          file: [],
          preview: [],
          tags: [],
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
            validator: VueFormGenerator.validators.required
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
          private: false,
          taggable: true
        },
        settingsSchema: {
          fields: [{
            type: 'v-text',
            label: 'Name',
            required: true,
            featured: true,
            hint: "This will change the URL of your character's page. Any existing links to them may be broken.",
            model: 'name',
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-checkbox',
            label: 'Open Requests',
            hint: 'Allow other people to commission pieces of your character. You ' +
                  'can specify restrictions for commissions after this is enabled. Note: If this character is private, ' +
            'and this checkbox is checked, anyone you have shared this character with will be able to share the ' +
            'character with an artist when placing a commission.',
            model: 'open_requests'
          }, {
            type: 'v-checkbox',
            label: 'Private',
            hint: 'Hides your character from public listings and prevents anyone with whom they have not been ' +
                  'explicitly shared from viewing it.',
            model: 'private'
          }, {
            type: 'v-checkbox',
            label: 'Taggable',
            hint: 'If unchecked, this character cannot be tagged by others.',
            model: 'taggable'
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
            multiLine: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'tag-search',
            model: 'tags',
            label: 'Tags',
            featured: true,
            placeholder: 'Search tags',
            styleClasses: 'field-input'
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
            label: 'Full File',
            model: 'file',
            required: true
          },
          {
            type: 'v-file-upload',
            id: 'preview',
            label: 'Preview Image/Thumbnail',
            model: 'preview',
            required: false
          }]
        },
        newUploadOptions: {
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
        transferModel: {
          buyer: null,
          price: 0,
          include_assets: false
        },
        transferVisible: false,
        transferSchema: {
          fields: [{
            type: 'user-search',
            label: 'Transferee',
            model: 'buyer',
            hint: 'The person who will receive the transfer. Transferees must accept the transfer to receive the character.'
          }, {
            type: 'v-checkbox',
            label: 'Include Submissions',
            model: 'include_assets',
            hint: 'Also transfer over any pieces you own in which this character is tagged. Note: ' +
                  'This also includes pieces where other characters are tagged.'
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Price (USD)',
            model: 'price',
            step: '.01',
            min: '0.00',
            validator: [minimumOrZero, validNumber],
            hint: 'Optionally, require payment for this transfer.'
          }, {
            type: 'v-checkbox',
            label: 'I agree to the Character Transfer Agreement',
            model: 'read_agreement',
            validator: [validateTrue],
            hint: 'I have read and understood the Character Transfer Agreement and agree to it'
          }]
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
      },
      fee () {
        return ((this.price * (this.pricing.landscape_percentage * 0.01)) + parseFloat(this.pricing.landscape_static)).toFixed(2)
      },
      payout () {
        return (this.price - this.fee).toFixed(2)
      },
      price () {
        if (parseFloat(this.transferModel.price + '') <= 0) {
          return 0
        }
        if (isNaN(parseFloat(this.transferModel.price + ''))) {
          return 0
        }
        return (parseFloat(this.transferModel.price + '')).toFixed(2)
      }
    },
    created () {
      this.fetchCharacter()
      this.fetchAssets()
      artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing)
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
            'query': {'editing': this.editing || undefined}
          }
        )
        this.url = `/api/profiles/v1/account/${this.username}/characters/${value}/`
      }
    }
  }
</script>
