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
                       :url="`/api/profiles/v1/${this.user.username}/characters/${this.character.name}/`"
                       method="DELETE" class="fg-dark"
            ><i class="fg-light fa fa-trash-o fa-2x"></i>
              <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this character? This cannot be undone!</div>
            </ac-action>
          </div>
        <div class="row">
          <div class="col-sm-6">
            <div class="statline">
              <strong>Species:</strong> <ac-patchfield v-model="character.species" name="species" :editmode="editing" :url="url"></ac-patchfield>
            </div>
            <div class="statline">
              <strong>Gender:</strong> <ac-patchfield v-model="character.gender" name="gender" :editmode="editing" :url="url"></ac-patchfield>
            </div>
          </div>
          <div class="col-sm-6 pull-right">
            <div class="statline">
              <strong>Species:</strong> <ac-patchfield v-model="character.species" name="species" :editmode="editing" :url="url"></ac-patchfield>
            </div>
            <div class="statline">
              <strong>Gender:</strong> <ac-patchfield v-model="character.gender" name="gender" :editmode="editing" :url="url"></ac-patchfield>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-4 p-0 section-text">
        <div class="character-panel-preview text-center">
          <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
            <ac-asset img-class="character-refsheet" :asset="character.primary_asset"></ac-asset>
          </router-link>
          <img class="character-refsheet" v-else src="/static/images/default-avatar.png"/>
        </div>
      </div>
    </div>
    <div class="row mb-3 shadowed" v-if="character">
      <div class="col-md-8 col-sm-12 text-section pt-3 pl-4">
        <h2 class="mb-0">
          About {{ character.name }}
        </h2>
        <div class="card-block">
          <div class="card-block character-description"><ac-patchfield v-model="character.description" name="description" :multiline="true" :editmode="editing" :url="url"></ac-patchfield></div>
        </div>
      </div>
      <div class="col-md-4 col-sm-12 text-section text-center pt-3 pl-4">
        <ac-avatar :user="character.user"></ac-avatar>
      </div>
    </div>
    <div class="row mb-3" v-if="character">
      <div class="col-sm-12 col-md-9 text-center image-showcase" v-if="assets && assets.length">
        <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
          <img class="character-refsheet mb-2 shadowed" :src="character.primary_asset.file"/>
          <div class="character-gallery-title text-center">{{ character.primary_asset.title }}</div>
        </router-link>
        <router-link v-else-if="assets && assets[0]" :to="{name: 'Submission', params: {assetID: assets[0].id}}">
          <img class="character-refsheet shadowed" :src="assets[0].file"/>
          <div class="gallery-image-overlay">
            <div class="gallery-image-stats"><i class="fa fa-star"></i> {{ asset.favorite_count }} <i class="fa fa-comment"></i> {{ asset.comment_count }}</div>
          </div>
          <div class="character-gallery-title text-center">{{ assets[0].title }}</div>
        </router-link>
        <div class="more">
          <b-button v-if="controls && !showUpload" variant="primary" @click="displayUploader">Upload a new picture of {{ character.name }}</b-button> <b-button v-if="assets && moreToLoad" variant="primary">See all uploads of {{ character.name }}</b-button>
        </div>
      </div>
      <div class="col-sm-12 text-center" v-else>
        <b-button v-if="controls && !showUpload" variant="primary" @click="displayUploader">Upload a new picture of {{ character.name }}</b-button>
      </div>
      <div class="col-sm-12 col-md-3 character-gallery" v-if="assets != null">
        <ac-gallery-preview v-for="(asset, key, index) in assets"
             :key="key" :id="'asset-' + key"
             v-if="asset.id !== displayedId"
             :asset="asset"
        >
        </ac-gallery-preview>
      </div>
      <div class="col-sm-12" v-if="showUpload">
        <form>
          <ac-form-container ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                             :options="newUploadOptions" :success="addUpload"
                             :url="`/api/profiles/v1/${user.username}/characters/${character.name}/assets/`"
          >
            <b-button @click="showUpload=false">Cancel</b-button>
            <b-button type="submit" variant="primary" @click.prevent="$refs.newUploadForm.submit">Create</b-button>
          </ac-form-container>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  @import '../custom-bootstrap';
  .character-description {
    width: 100%
  }
  .statline p{
    margin-bottom: .5rem;
    border-bottom: 1px solid $dark-purple;
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

  export default {
    name: 'Character',
    mixins: [Viewer, Perms, Editable],
    components: {
      AcGalleryPreview,
      AcPatchfield,
      AcAction,
      AcFormContainer,
      AcAvatar,
      AcAsset
    },
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
      showcase: function (asset) {
        artCall(
          `${this.url}/asset/primary/${asset.id}/`,
          'POST',
          null,
          this.postPrimary(asset.id)
        )
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
      rating: function (rate) {
        return {
          0: 'Clean/Safe for work',
          1: 'Risque/mature',
          2: 'Adult'
        }[rate]
      },
      nameUpdate () {
        this.$router.history.replace(
          {
            'name': 'Character',
            'params': {'username': this.user.username, 'character': this.character.name},
            'query': {'editing': true}
          }
        )
        this.url = `/api/profiles/v1/${this.$route.params.username}/characters/${this.$route.params.character}/`
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
      fetchAssets () {
        artCall(this.url + 'assets/?size=4', 'GET', null, this.loadAssets)
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
        selectedIndex: null,
        expand: this.expanded,
        character: null,
        assets: null,
        totalPieces: 0,
        url: `/api/profiles/v1/${this.$route.params.username}/characters/${this.$route.params.character}/`,
        newUploadModel: {
          title: '',
          caption: '',
          private: false,
          rating: 0,
          file: '',
          comments_disabled: false
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
      artCall(this.url, 'GET', null, this.loadCharacter)
      this.fetchAssets()
    },
    watch: {
      rating () {
        this.fetchAssets()
      }
    }
  }
</script>
