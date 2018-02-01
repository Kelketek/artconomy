<template>
  <div class="container">
    <div class="row mb-3 shadowed" v-if="character">
      <div class="col-lg-8 text-section pt-3 pl-4">
        <ac-patchfield v-model="character.name" name="name" styleclass="name-edit" :editmode="editing" :callback="nameUpdate" :url="url"></ac-patchfield>
          <i v-if="controls && !editing" class="ml-2 fa fa-2x fa-lock clickable pull-right" @click="edit"></i>
          <i v-if="controls && editing" class="ml-2 fa fa-2x fa-unlock clickable pull-right" @click="lock"></i>
          <div v-if="controls" class="pull-right">
            <ac-action :button="false"
                       variant="danger" :confirm="true" :success="goToListing"
                       :url="`/api/profiles/v1/account/${this.user.username}/characters/${this.character.name}/`"
                       method="DELETE" class="fg-dark"
            ><i class="fg-light fa fa-trash-o fa-2x"></i>
              <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this character? This cannot be undone!</div>
            </ac-action>
          </div>
        <div class="row">
          <div class="col-6">
            <p v-if="(character.tags.length === 0) && editing">
              Add some tags to describe your character. Try tagging their species, gender or things they're commonly found doing.
            </p>
            <ac-tag-display
                :editable="editing"
                :url="`${url}tag/`"
                :callback="loadCharacter"
                :tag-list="character.tags"
                :controls="controls"
                v-if="character.tags.length || editing"
            />
          </div>
          <div class="col-6 pull-right">
            <ac-action v-if="editing" class="text-center" style="display:block" :url="url" method="PATCH" :send="{private: !character.private}" :success="loadCharacter">
              <span v-if="character.private"><i class="fa fa-eye"></i> Unhide character</span>
              <span v-else><i class="fa fa-eye-slash"></i> Hide character</span>
            </ac-action>
            <div v-else-if="controls" class="text-center">
              <span v-if="character.private"><i class="fa fa-eye-slash"></i> Character is private</span>
              <span v-else><i class="fa fa-eye"></i> Character is public</span>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-4 p-0 section-text">
        <div class="character-panel-preview text-center">
          <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
            <ac-asset
                img-class="character-refsheet"
                thumb-name="gallery"
                :asset="character.primary_asset"
            />
          </router-link>
          <img class="character-refsheet" v-else src="/static/images/default-avatar.png"/>
        </div>
      </div>
    </div>
    <div class="row mb-3 shadowed" v-if="character">
      <div class="col-md-8 col-12 text-section pt-3 pl-4">
        <h2 class="mb-0">
          About {{ character.name }}
        </h2>
        <div class="card-block">
          <div class="card-block character-description"><ac-patchfield v-model="character.description" name="description" :multiline="true" :editmode="editing" :url="url" /></div>
        </div>
      </div>
      <div class="col-md-4 col-12 text-section text-center pt-3 pl-4">
        <ac-avatar :user="character.user" />
      </div>
    </div>
    <div class="row mb-3 shadowed text-section pt-2" v-if="character && (character.colors.length || editing)">
      <div class="col-12 text-center"><h3>Colors</h3></div>
      <ac-ref-color
          v-for="refColor in character.colors"
          :key="refColor.id"
          :ref-color="refColor"
          :editing="editing"
          :callback="fetchCharacter"
          :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/colors/${refColor.id}/`"
      />
      <div class="col-12 mt-2 mb-2">
        <div class="row-centered" v-if="character.colors.length < 10">
          <div class="col-12 col-md-6 col-centered text-center">
            <b-button v-if="controls && editing && !showNewColor" variant="primary" @click="showNewColor = true">Add a color reference</b-button>
            <div v-if="showNewColor && editing">
              <ac-form-container
                  ref="newColorForm" :schema="newColorSchema" :model="newColorModel"
                  class="text-center"
                  :options="newUploadOptions" :success="addColor"
                  :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/colors/`"
              />
              <b-button @click="showNewColor=false">Cancel</b-button>
              <b-button type="submit" variant="primary" @click.prevent="$refs.newColorForm.submit">Add Color</b-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row mb-3" v-if="character">
      <div class="col-12 col-md-9 text-center image-showcase" v-if="assets && assets.length">
        <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
          <ac-asset class="mb-2 shadowed" :asset="character.primary_asset" thumb-name="gallery" img-class="character-refsheet" />
          <div class="character-gallery-title text-center">{{ character.primary_asset.title }}</div>
        </router-link>
        <router-link v-else-if="assets && assets[0]" :to="{name: 'Submission', params: {assetID: assets[0].id}}">
          <img class="character-refsheet shadowed" :src="assets[0].file.gallery"/>
          <div class="character-gallery-title text-center">{{ assets[0].title }} <i class="fa fa-star"></i> {{ assets[0].favorite_count }} <i class="fa fa-comment"></i> {{ assets[0].comment_count }}</div>
        </router-link>
        <div class="more">
          <b-button v-if="controls && !showUpload" variant="primary" @click="displayUploader">Upload a new picture of {{ character.name }}</b-button>
          <router-link :to="{name: 'CharacterGallery', params: {username: username, characterName: characterName}}">
            <b-button v-if="assets && moreToLoad" variant="primary">
              See all uploads of {{ character.name }}
            </b-button>
          </router-link>
        </div>
      </div>
      <div class="col-12 text-center" v-else>
        <b-button v-if="controls && !showUpload" variant="primary" @click="displayUploader">Upload a new picture of {{ character.name }}</b-button>
      </div>
      <div class="col-12 col-md-3 character-gallery" v-if="assets != null">
        <ac-gallery-preview v-for="(asset, key, index) in assets"
             :key="key" :id="'asset-' + key"
             v-if="asset.id !== displayedId"
             :asset="asset"
        >
        </ac-gallery-preview>
      </div>
      <div class="col-12" v-if="showUpload">
        <form>
          <ac-form-container ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                             :options="newUploadOptions" :success="addUpload"
                             :url="`/api/profiles/v1/account/${user.username}/characters/${character.name}/assets/`"
          >
            <b-button @click="showUpload=false">Cancel</b-button>
            <b-button type="submit" variant="primary" @click.prevent="$refs.newUploadForm.submit">Create</b-button>
          </ac-form-container>
        </form>
      </div>
    </div>
  </div>
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
      nameUpdate () {
        this.$router.history.replace(
          {
            'name': 'Character',
            'params': {'username': this.user.username, 'character': this.character.name},
            'query': {'editing': true}
          }
        )
        this.url = `/api/profiles/v1/account/${this.username}/characters/${this.characterName}/`
      },
      loadCharacter (response) {
        this.character = response
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
        name: 'haracter',
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
          file: '',
          comments_disabled: false
        },
        showNewColor: false,
        newColorModel: {
          color: '#ffffff',
          note: ''
        },
        newColorSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Note',
            placeholder: 'Fur color',
            model: 'note',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'color',
            label: 'Color',
            model: 'color',
            required: true,
            featured: true,
            colorOptions: {
              preferredFormat: 'rgb'
            }
          }]
        },
        showUpload: false,
        newUploadSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Title',
            model: 'title',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'textArea',
            label: 'Caption',
            model: 'caption',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Private Upload?',
            model: 'private',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Only shows this piece to people you have explicitly shared it to.'
          },
          {
            type: 'checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Comments disabled?',
            model: 'comments_disabled',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Prevents people from commenting on this piece.'
          },
          {
            type: 'select',
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
            type: 'image',
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
      editing () {
        return this.controls && this.$route.query.editing
      },
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
      }
    }
  }
</script>
