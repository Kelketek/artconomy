<template>
  <v-container grid-list-md>
    <v-layout row wrap text-xs-centered v-if="response !== null">
      <v-flex xs12 v-if="error" text-xs-center>
        <p>{{error}}</p>
      </v-flex>
      <v-flex xs12 text-xs-center>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" :id="scrollToId" :total-visible="10"/>
      </v-flex>
      <ac-character-preview
        v-for="char in response.results"
        v-bind:character="char"
        v-bind:expanded="true"
        v-bind:key="char.id"
        xs12 sm4 lg3
      >
      </ac-character-preview>
      <v-flex xs12 v-if="response.results.length === 0 && controls">
        <v-card color="grey darken-3">
          <v-responsive :aspect-ratio="16/5" width="100%">
            <v-container fill-height>
              <v-layout align-center>
                <v-flex>
                  <h3 class="display-3">Add a character!</h3>
                  <span class="subheading">Set up your first character in Artconomy, make a gallery for them, and commission artists.</span>
                  <v-divider class="my-3" />
                  <v-btn large color="primary" class="mx-0" @click="showNew = true">Start Now</v-btn>
                </v-flex>
              </v-layout>
            </v-container>
          </v-responsive>
        </v-card>
      </v-flex>
      <v-flex xs12 text-xs-center>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" @input="performScroll" :total-visible="5"/>
      </v-flex>
    </v-layout>
    <v-layout row wrapped v-else>
      <v-flex xs12 text-xs-center><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
    </v-layout>
    <div class="row-centered" v-if="controls && embedded && response !== null && response.results.length !== 0">
      <div class="col-12 pt-3 col-md-4 col-centered text-xs-center">
        <v-btn color="primary" size="lg" @click="showNew=true" id="new-char-button">Add a new character</v-btn>
      </div>
    </div>
    <v-flex v-if="noPagination && to && currentPage !== totalPages" xs12 text-xs-center>
      <v-btn color="primary" :to="to">{{seeMoreText}}</v-btn>
    </v-flex>
    <ac-form-dialog ref="newCharForm" :schema="newCharSchema" :model="newCharModel"
                       :options="newCharOptions" :success="addCharacter"
                       title="New Character"
                       :url="`/api/profiles/v1/account/${this.user.username}/characters/`"
                       v-model="showNew"
    />
    <v-btn
           dark
           color="green"
           fab
           hover
           fixed
           right
           bottom
           large
           @click="showNew=true"
    >
      <v-icon x-large>add</v-icon>
    </v-btn>
  </v-container>
</template>

<script>
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import Viewer from '../mixins/viewer'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'
  import AcCharacterPreview from './ac-character-preview'
  import AcFormDialog from './ac-form-dialog'
  import AcSpeedButton from './ac-speed-button'

  export default {
    components: {AcSpeedButton, AcFormDialog, AcFormContainer, AcCharacterPreview},
    name: 'Characters',
    mixins: [Viewer, Perms, Paginated],
    props: ['embedded', 'endpoint', 'noPagination', 'to', 'seeMoreText'],
    data: function () {
      return {
        newCharModel: {
          name: '',
          private: false,
          tags: []
        },
        url: this.endpoint,
        showNew: false,
        newCharSchema: {
          fields: [{
            type: 'v-text',
            label: 'Character name',
            model: 'name',
            placeholder: 'My character',
            featured: true,
            required: true,
            hint: 'This is some help text',
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Private Character?',
            model: 'private',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'Only shows this character to people you have explicitly shared them to. ' +
            'Note that this prevents your character from showing up in searches and lists, but does not hide ' +
            'submissions which are marked public.'
          }, {
            type: 'tag-search',
            model: 'tags',
            label: 'Tags',
            hint: 'Add some tags to make your character easier to search for',
            required: true,
            validator: VueFormGenerator.validators.required
          }]
        },
        newCharOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      addCharacter (response) {
        this.$router.history.push(
          {name: 'Character', params: {user: this.username, characterName: response.name}, query: {editing: true}}
        )
      }
    }
  }
</script>
