<template>
  <v-container grid-list-md>
    <v-layout row wrap text-xs-centered v-if="response !== null">
      <v-flex xs12 v-if="error">
        <p>{{error}}</p>
      </v-flex>
      <v-flex xs12>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
      <ac-character-preview
        v-for="char in response.results"
        v-bind:character="char"
        v-bind:expanded="true"
        v-bind:key="char.id"
        xs12 sm4 lg3
      >
      </ac-character-preview>
      <v-flex xs12>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
    </v-layout>
    <v-layout row wrapped v-else>
      <v-flex xs12 text-xs-center><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
    </v-layout>
    <div class="row-centered" v-if="controls && embedded">
      <div class="col-12 pt-3 col-md-4 col-centered text-xs-center">
        <v-btn color="primary" size="lg" @click="showNew=true" id="new-char-button">Add a new character</v-btn>
      </div>
    </div>
    <ac-form-dialog ref="newCharForm" :schema="newCharSchema" :model="newCharModel"
                       :options="newCharOptions" :success="addCharacter"
                       :url="`/api/profiles/v1/account/${this.user.username}/characters/`"
                       v-model="showNew"
    />
    <v-btn v-if="controls && !embedded"
           dark
           color="green"
           fab
           hover
           fixed
           right
           bottom
           @click="showNew=true"
    >
      <v-icon large>add</v-icon>
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

  export default {
    components: {AcFormDialog, AcFormContainer, AcCharacterPreview},
    name: 'Characters',
    mixins: [Viewer, Perms, Paginated],
    props: ['embedded', 'endpoint'],
    data: function () {
      return {
        newCharModel: {
          name: '',
          description: '',
          private: false,
          open_requests: true,
          open_requests_restrictions: ''
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
            hint: 'Only shows this character to people you have explicitly shared them to.'
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
    },
    created () {
      this.fetchItems()
    }
  }
</script>
