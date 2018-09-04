<template>
  <v-container class="account-profile" :key="username">
    <v-card>
      <v-layout row wrap class="mb-4">
        <v-flex xs12 sm2  text-xs-center text-sm-left class="pt-2">
          <v-layout row wrap>
            <v-flex xs12 text-xs-center>
              <ac-avatar :user="user" :show-rating="true" :no-link="true" />
            </v-flex>
            <v-flex xs12 text-xs-center v-if="!isCurrent">
              <ac-action :url="`/api/profiles/v1/account/${username}/watch/`" :success="replaceUser" v-if="isLoggedIn">
                <span v-if="user.watching"><v-icon>visibility_off</v-icon>&nbsp;Stop Watching</span>
                <span v-else><v-icon>visibility</v-icon>&nbsp;Watch</span>
              </ac-action>
            </v-flex>
            <v-flex xs12 text-xs-center v-if="!isCurrent">
              <ac-action :url="`/api/profiles/v1/account/${username}/block/`" :success="replaceUser" v-if="isLoggedIn">
                <v-icon>block</v-icon>
                <span v-if="user.blocked">&nbsp;Unblock</span><span v-else>&nbsp;Block</span>
              </ac-action>
            </v-flex>
            <v-flex xs12 text-xs-center v-if="!isCurrent && isLoggedIn">
              <v-btn @click="showNewMessage = true">
                <v-icon>message</v-icon>
                <span>&nbsp;Message</span>
              </v-btn>
            </v-flex>
            <v-flex v-if="!isCurrent && user.watching" text-xs-center>
              <v-btn v-if="isLoggedIn && !portrait" color="purple" :to="{name: 'Upgrade'}">Alert when open</v-btn>
              <span v-if="portrait && user.watching">You will be alerted when this artist is open.</span>
            </v-flex>
          </v-layout>
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
    <ac-journals :username="username" :limit="3" class="mb-3"/>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-products" v-if="user.has_products"><v-icon>shopping_basket</v-icon>&nbsp;Products</v-tab>
      <v-tab href="#tab-characters"><v-icon>people</v-icon>&nbsp;Characters</v-tab>
      <v-tab href="#tab-gallery"><v-icon>image</v-icon>&nbsp;Gallery</v-tab>
      <v-tab href="#tab-favorites" v-if="!user.favorites_hidden || controls"><v-icon>favorite</v-icon>&nbsp;Favorites<span v-if="user.favorites_hidden">&nbsp;<v-icon>visibility_off</v-icon></span></v-tab>
      <v-tab href="#tab-other"><v-icon>more</v-icon>&nbsp;Other Submissions</v-tab>
      <v-tab href="#tab-watchlists"><v-icon>visibility</v-icon>&nbsp;Watchlists</v-tab>
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
               large
               @click="newUploadModel.is_artist=true; showUpload=true"
        >
          <v-icon x-large>add</v-icon>
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
               large
               @click="newUploadModel.is_artist=false; showUpload=true"
        >
          <v-icon x-large>add</v-icon>
        </v-btn>
      </v-tab-item>
      <v-tab-item id="tab-watchlists">
        <v-tabs v-model="watchTab" fixed-tabs>
          <v-tab href="#tab-watchers">Watchers</v-tab>
          <v-tab href="#tab-watching">Watching</v-tab>
        </v-tabs>
        <v-tabs-items v-model="watchTab">
          <v-tab-item id="tab-watchers">
            <ac-user-gallery :endpoint="`/api/profiles/v1/account/${username}/watchers/`" />
          </v-tab-item>
          <v-tab-item id="tab-watching">
            <ac-user-gallery :endpoint="`/api/profiles/v1/account/${username}/watching/`" />
          </v-tab-item>
        </v-tabs-items>
      </v-tab-item>
    </v-tabs-items>
    <ac-form-dialog ref="newUploadForm" :schema="newUploadSchema" :model="newUploadModel"
                    :options="newUploadOptions" :success="addUpload"
                    v-model="showUpload"
                    :url="`/api/profiles/v1/account/${user.username}/gallery/`"
    />
    <ac-form-dialog ref="newMessageForm" :schema="newMessageSchema" :model="newMessageModel"
                    :options="newMessageOptions" :success="goToMessage"
                    title="New Message"
                    :url="`/api/profiles/v1/account/${this.viewer.username}/messages/sent/`"
                    v-model="showNewMessage"
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
  import AcAction from './ac-action'
  import AcUserGallery from './ac-user-gallery'
  import AcJournals from './ac-journals'

  export default {
    name: 'Profile',
    mixins: [Viewer, Perms],
    components: {
      AcJournals,
      AcUserGallery,
      AcAction,
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
      },
      replaceUser (response) {
        this.$setUser(response.username, response)
        this.user = response
      },
      goToMessage (response) {
        this.$router.push({name: 'Message', params: {messageID: response.id, username: response.sender.username}})
      }
    },
    data: function () {
      return {
        user: {username: this.username},
        count: 0,
        assets: null,
        showUpload: false,
        showNewMessage: false,
        journals: null,
        newUploadModel: {
          title: '',
          caption: '',
          private: false,
          rating: null,
          file: [],
          preview: [],
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
            multiLine: true,
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
            label: 'Tags',
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
            styleClasses: 'field-input',
            multiple: true
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
          },
          {
            type: 'v-file-upload',
            id: 'preview',
            label: 'Preview Image/Thumbnail',
            model: 'preview',
            required: false
          }
          ]
        },
        newUploadOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        newMessageModel: {
          subject: '',
          body: '',
          recipients: []
        },
        newMessageSchema: {
          fields: [{
            type: 'user-search',
            model: 'recipients',
            label: 'Recipients',
            featured: true,
            tagging: true,
            placeholder: 'Search users',
            styleClasses: 'field-input',
            multiple: true
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Subject',
            model: 'subject',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            label: 'Body',
            model: 'body',
            featured: true,
            multiLine: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        newMessageOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    watch: {
      username () {
        this.user = {username: this.username}
        this.refreshUser()
      },
      user () {
        if (this.user.id) {
          EventBus.$emit('userfield-add-recipients', this.user)
        }
      }
    },
    computed: {
      controls: function () {
        return this.$root.user.is_staff || (this.username === this.$root.user.username)
      },
      url () {
        return `/api/profiles/v1/data/user/${this.username}/`
      },
      tab: paramHandleMap('tabName'),
      watchTab: paramHandleMap('subTabName', undefined, ['tab-watchers', 'tab-watching'], 'tab-watchers')
    }
  }
</script>
