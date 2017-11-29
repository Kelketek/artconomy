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
      </div>
      <div class="col-lg-4 p-0 section-text">
        <div class="character-panel-preview text-center">
          <img class="character-refsheet" v-if="character.primary_asset && character.primary_asset.id" :src="character.primary_asset.file"/>
          <img class="character-refsheet" v-else src="/assets/default-avatar.png"/>
        </div>
      </div>
    </div>
    <div class="row mb-3 shadowed" v-if="character">
      <div class="col-md-8 col-sm-12 text-section pt-3 pl-4">
        <h2 class="mb-0">
          About {{ character.name }}
        </h2>
        <div class="card-block">
          <div class="card-block character-description" v-html="parseDesc()"></div>
        </div>
      </div>
      <div class="col-md-4 col-sm-12 text-section pt-3 pl-4">
        <h3 class="mb-0">By <router-link :to="{name: 'Profile', params: {username: character.user.username}}">{{ character.user.username }}</router-link></h3>
      </div>
    </div>
    <div class="row mb-3" v-if="character">
      <div class="col-sm-12 col-md-9 text-center image-showcase">
        <router-link v-if="character.primary_asset && character.primary_asset.id" :to="{name: 'Submission', params: {assetID: character.primary_asset.id}}">
          <img class="character-refsheet mb-2 shadowed" :src="character.primary_asset.file"/>
          <div class="character-gallery-title text-center">{{ character.primary_asset.title }}</div>
        </router-link>
        <router-link v-else-if="assets && assets[0]" :to="{name: 'Submission', params: {assetID: assets[0].id}}">
          <img class="character-refsheet shadowed" :src="assets[0].file"/>
          <div class="character-gallery-title text-center">{{ assets[0].title }}</div>
        </router-link>
        <div class="more">
          <b-button variant="primary">See all uploads of {{ character.name }}</b-button>
        </div>
      </div>
      <div class="col-sm-12 col-md-3 character-gallery" v-if="assets != null">
        <ac-gallery-preview v-for="(asset, key, index) in assets"
             :key="key" :id="'asset-' + key"
             v-if="asset.id !== displayedId"
             :asset="asset"
        >
        </ac-gallery-preview>
      </div>
    </div>
  </div>
</template>

<script>
  import {artCall} from '../lib'
  import Perms from '../mixins/permissions'
  import AcAction from './ac-action'
  import AcPatchfield from './ac-patchfield'
  import AcGalleryPreview from './ac-gallery-preview'

  export default {
    name: 'Character',
    mixins: [Perms],
    components: {
      AcGalleryPreview,
      AcPatchfield,
      AcAction
    },
    methods: {
      parseDesc: function () {
        return this.$root.md.render(this.character.description)
      },
      setIndex: function (key) {
        this.$data.selectedIndex = key
      },
      edit: function () {
        this.$router.replace({query: Object.assign({}, this.$route.query, { editing: true })})
      },
      lock: function () {
        this.$router.replace({query: {}})
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
      loadAssets (response) {
        this.assets = response.results
      }
    },
    data () {
      return {
        selectedIndex: null,
        expand: this.expanded,
        character: null,
        assets: null,
        url: `/api/profiles/v1/${this.$route.params.username}/characters/${this.$route.params.character}/`
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
      }
    },
    created () {
      artCall(this.url, 'GET', null, this.loadCharacter)
      artCall(this.url + 'assets/', 'GET', null, this.loadAssets)
    }
  }
</script>
