<template>
  <v-container class="account-profile">
    <v-card>
      <v-layout row wrap class="mb-4">
        <v-flex xs12 sm2  text-xs-center text-sm-left class="pt-2">
          <ac-avatar :user="user" />
        </v-flex>
        <v-flex xs12 sm10 class="pt-2 pl-2 pr-2">
          <h3>About {{user.username}}</h3>
          <ac-patchfield
              v-model="user.biography"
              name="biography"
              :multiline="true"
              :editmode="controls"
              :url="url"
              placeholder="Write a bit about yourself!"
          />
        </v-flex>
        <v-flex sm3 class="hidden-sm-and-down">
        </v-flex>
      </v-layout>
    </v-card>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-products" v-if="user.has_products"><v-icon>shopping_basket</v-icon>&nbsp;Products</v-tab>
      <v-tab href="#tab-characters"><v-icon>people</v-icon>&nbsp;Characters</v-tab>
      <v-tab href="#tab-gallery"><v-icon>image</v-icon>&nbsp;Gallery</v-tab>
      <v-tab href="#tab-favorites" v-if="!user.favorites_hidden || controls"><v-icon>favorite</v-icon>&nbsp;Favorites<span v-if="user.favorites_hidden">&nbsp;<v-icon>visibility_off</v-icon></span></v-tab>
      <v-tab href="#tab-other"><v-icon>more</v-icon>&nbsp;Other Submissions</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" class="min-height">
      <v-tab-item id="tab-products" :class="{'tab-shown': shownTab('tab-products')}">
        <store :endpoint="`/api/sales/v1/account/${username}/products/`" :username="username" :track-pages="true" tab-name="tab-store"/>
      </v-tab-item>
      <v-tab-item id="tab-characters" :class="{'tab-shown': shownTab('tab-characters')}">
        <Characters
            :username="username"
            :endpoint="`/api/profiles/v1/account/${username}/characters/`" :track-pages="true" tab-name="tab-characters" />
      </v-tab-item>
      <v-tab-item id="tab-gallery" :class="{'tab-shown': shownTab('tab-gallery')}">
        <ac-asset-gallery
            :endpoint="`/api/profiles/v1/account/${username}/gallery/`" :track-pages="true" tab-name="tab-gallery"
        />
        <v-btn v-if="controls"
               dark
               color="green"
               fab
               hover
               fixed
               right
               bottom
               @click="newUploadModel.is_artist=true; showUpload=true"
        >
          <v-icon large>add</v-icon>
        </v-btn>
      </v-tab-item>
      <v-tab-item id="tab-favorites" v-if="!user.favorites_hidden || controls">
        <ac-asset-gallery
            :endpoint="`/api/profiles/v1/account/${username}/favorites/`" :track-pages="true" tab-name="tab-favorites"
        />
      </v-tab-item>
      <v-tab-item id="tab-other" :class="{'tab-shown': shownTab('tab-other')}">
        <ac-asset-gallery
            :endpoint="`/api/profiles/v1/account/${username}/submissions/`" :track-pages="true" tab-name="tab-other"
        />
        <v-btn v-if="controls"
               dark
               color="green"
               fab
               hover
               fixed
               right
               bottom
               @click="newUploadModel.is_artist=false; showUpload=true"
        >
          <v-icon large>add</v-icon>
        </v-btn>
      </v-tab-item>
    </v-tabs-items>
    <ac-form-dialog ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                    :options="newUploadOptions" :success="addUpload"
                    v-model="showUpload"
                    :url="`/api/profiles/v1/account/${user.username}/gallery/`"
    />
  </v-container>
</template>

<style scoped>
  .min-height {
    min-height: 25rem;
  }
</style>

<style>
  @keyframes delay-display {
    0% { opacity: 0 }
    99% { opacity: 0 }
    100% { opacity: 1 }
  }
  .account-profile .btn--floating {
    visibility: hidden;
    opacity: 0;
    transition: none;
  }
  .account-profile .tab-shown .btn--floating {
    visibility: visible;
    opacity: 1;
    animation: delay-display 1s;
  }
</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import Characters from './Characters'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'
  import AcAssetGallery from './ac-asset-gallery'
  import { paramHandleMap, ratings, EventBus } from '../lib'
  import AcContextGallery from './ac-context-gallery'
  import Store from './Store'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'Profile',
    mixins: [Viewer, Perms],
    components: {
      AcFormDialog,
      Store,
      AcContextGallery,
      AcAssetGallery,
      AcPatchfield,
      AcAvatar,
      Characters,
      Editable
    },
    methods: {
      shownTab (tabName) {
        if (tabName === this.tab) {
          EventBus.$emit('tab-shown', tabName)
          return true
        }
      },
      addUpload (response) {
        this.$router.history.push({name: 'Submission', params: {assetID: response.id}})
      }
    },
    data: function () {
      return {
        user: {username: this.username},
        url: `/api/profiles/v1/data/user/${this.username}/`,
        count: 0,
        assets: null,
        showUpload: false,
        newUploadModel: {
          title: '',
          caption: '',
          private: false,
          rating: null,
          file: [],
          comments_disabled: false,
          characters: [],
          is_artist: false,
          artists: [],
          tags: []
        },
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
            type: 'character-search',
            model: 'characters',
            label: 'Characters',
            featured: true,
            commission: false,
            placeholder: 'Search characters',
            styleClasses: 'field-input'
          },
          {
            type: 'tag-search',
            model: 'tags',
            label: 'tags',
            featured: true,
            placeholder: 'Search tags',
            styleClasses: 'field-input'
          },
          {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'I am an Artist who worked on this piece',
            model: 'is_artist',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, this submission will be shown in your gallery. If not, it will be ' +
            "displayed in the galleries of any characters you own and have tagged, or in the 'Other Submissions' " +
            'section of your profile.'
          },
          {
            type: 'user-search',
            model: 'artists',
            label: 'Other Artists',
            featured: true,
            tagging: true,
            placeholder: 'Search artists',
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
            label: 'File',
            model: 'file',
            required: true
          }
          ]
        },
        newUploadOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      controls: function () {
        return this.$root.user.is_staff || (this.user.username === this.$root.user.username)
      },
      tab: paramHandleMap('tabName')
    }
  }
</script>
